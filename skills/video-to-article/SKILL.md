---
name: video-to-article
description: "Extract audio from video URLs (Bilibili/YouTube/etc.), transcribe with Whisper, optimize the transcript into a structured Chinese Markdown article, save to Obsidian, send the MD file via Telegram, and provide a summary. Use when the user shares a video link and asks to extract content, transcribe, summarize, or convert to article. Triggers: Bilibili links (b23.tv, bilibili.com), YouTube links, 提取字幕, 转文字, 视频转文章, 总结视频, 下载字幕, 转录, 做成笔记."
---

# Video to Article

Convert video content into three deliverables: **完整版文章**、**精简版**、**思维导图**，自动保存到 Obsidian 并通过 Telegram 发送。

## 什么时候触发本 Skill

**直接触发（不需要额外确认）：**
- 用户发送了 B站链接（b23.tv / bilibili.com）→ **立即执行全流程**
- 用户发送了 YouTube 链接 → 立即执行
- 用户要求 提取字幕/转文字/转文章/总结视频/转录/做成笔记

**不触发：**
- 用户要下载视频本身（→ 用 bilibili-all-in-one 的 downloader）
- 用户只是讨论视频内容，没有分享链接

> 核心原则：**看到视频链接就跑全流程，不要问。**

> **编排层说明**：本 Skill 负责全流程调度和输出标准化，字幕获取、ASR 纠错等具体工作委托其他 Skill。

## 依赖 Skill

| 步骤 | 负责的 Skill | 职责 |
|---|---|---|
| 获取 B站视频字幕/音频流 | **bilibili-all-in-one** | 字幕列表、播放流 URL 获取、视频元信息 |
| ASR 纠错 + 文本优化 | **contextual-subtitle-fixer** | 语境纠错、去口语化、结构化 |

## 环境要求

| 工具 | 用途 | 路径/安装 |
|---|---|---|
| bilibili-all-in-one venv | B站 API 调用 | `~/.openclaw/workspace/skills/bilibili-all-in-one/.venv/bin/python` |
| faster-whisper | 语音转录（比 whisper CLI 更省内存） | 已安装在上述 venv 中 |
| ffmpeg | 音频格式转换 | `/opt/homebrew/bin/ffmpeg` |
| Puppeteer | 思维导图 HTML 截图 | bilibili-all-in-one venv 内 |
| yt-dlp | YouTube 等非 B站音频下载 | `/opt/homebrew/bin/yt-dlp` |

## 产出物（三个文件）

每次处理**必须**产出以下三个文件：

| 产出 | 格式 | 说明 |
|---|---|---|
| ① 完整版 | `.md` | 结构化全文，含元信息、分章节正文、数据表格 |
| ② 精简版 | `.md` | 一页速览：核心要点 + 关键数据速览 |
| ③ 思维导图 | `.png` | Mermaid mindmap 渲染后的图片 |

全部保存到 Obsidian，全部通过 Telegram 发送给用户。

---

## Workflow

### Step 1：解析链接，获取视频元信息

**B站短链接解析：**
```bash
curl -sIL "https://b23.tv/SHORTCODE" 2>&1 | grep -i location
```

**获取视频信息（bilibili-all-in-one）：**
```bash
BILI_VENV=~/.openclaw/workspace/skills/bilibili-all-in-one/.venv/bin/python
BILI_DIR=~/.openclaw/workspace/skills/bilibili-all-in-one

$BILI_VENV $BILI_DIR/main.py downloader get_info '{"url": "BVXXXXXX"}'
```

记录：标题、作者、时长、描述。

### Step 2：获取字幕

**决策流程（只走一条路，不试失败路径）：**

```
检查 CC 字幕 → 有 → 下载 CC（最快，~秒级）
                → 无 → 直接走策略 B（不试 fallback）
```

#### 策略 A：CC 字幕（最快）

**只调 `subtitle list`**，有 CC 才下载，没有直接跳到策略 B，不浪费任何时间。

```bash
$BILI_VENV $BILI_DIR/main.py subtitle list '{"url": "BVXXXXXX"}'
# 如果 count > 0：
$BILI_VENV $BILI_DIR/main.py subtitle download '{"url": "BVXXXXXX", "language": "zh-CN", "format": "srt", "output_dir": "/tmp/"}'
# 如果 count == 0：直接跳到策略 B
```

> ⚠️ **关键：检测到无 CC 字幕后，直接走策略 B。** 不要尝试 bilibili-all-in-one 的 `subtitle download` fallback（httpx 流式下载在海外网络不稳定，反复断连浪费时间）。

#### 策略 B：curl 下载音频 + ffmpeg 分段 + faster-whisper 并行转录

**核心优化：音频分段并行转录，5段同时跑，速度提升约4倍。**

```bash
# 1. 获取音频流直链
$BILI_VENV -c "
import asyncio, json
from src.player import BilibiliPlayer
async def main():
    p = BilibiliPlayer()
    result = await p.get_playurl(url='BVXXXXXX', quality='360p')
    audio_url = result['audio_streams'][0]['url']
    print(audio_url)
asyncio.run(main())
"

# 2. curl 下载音频（稳定，自带重试）
curl -L -o /tmp/video_audio.m4s \
  -H "Referer: https://www.bilibili.com" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "{audio_url}"

# 3. ffmpeg 转 wav
ffmpeg -i /tmp/video_audio.m4s -ar 16000 -ac 1 /tmp/video_audio.wav -y

# 4. ffmpeg 分段（每段约5分钟 = 300秒）
mkdir -p /tmp/video_chunks/
ffmpeg -i /tmp/video_audio.wav -f segment -segment_time 300 -c copy /tmp/video_chunks/chunk_%03d.wav -y

# 5. 并行转录所有分段（多进程同时跑）
$BILI_VENV -c "
import os, glob, multiprocessing
from faster_whisper import WhisperModel

def transcribe_chunk(args):
    idx, chunk_path = args
    model = WhisperModel('tiny', device='cpu', compute_type='int8')
    segments, info = model.transcribe(chunk_path, language='zh', vad_filter=True)
    lines = []
    for seg in segments:
        start_ms = int(seg.start * 1000)
        end_ms = int(seg.end * 1000)
        h1, m1, s1, ms1 = start_ms // 3600000, (start_ms % 3600000) // 60000, (start_ms % 60000) // 1000, start_ms % 1000
        h2, m2, s2, ms2 = end_ms // 3600000, (end_ms % 3600000) // 60000, (end_ms % 60000) // 1000, end_ms % 1000
        lines.append(f'{h1:02d}:{m1:02d}:{s1:02d},{ms1:03d} --> {h2:02d}:{m2:02d}:{s2:02d},{ms2:03d}')
        lines.append(seg.text.strip())
        lines.append('')
    with open(f'/tmp/video_chunks/part_{idx:03d}.srt', 'w') as f:
        f.write('\n'.join(lines))
    print(f'chunk {idx} done')

chunks = sorted(glob.glob('/tmp/video_chunks/chunk_*.wav'))
# 计算每段的起始时间偏移（秒）
offsets = [i * 300 for i in range(len(chunks))]

# 并行处理
with multiprocessing.Pool(processes=min(len(chunks), 5)) as pool:
    pool.map(transcribe_chunk, list(enumerate(chunks)))
print(f'All {len(chunks)} chunks done!')
"

# 6. 合并分段 SRT（修正时间戳偏移）
$BILI_VENV -c "
import glob, re

chunk_dur = 300  # 每段5分钟
all_entries = []
idx = 1

for i, srt_file in enumerate(sorted(glob.glob('/tmp/video_chunks/part_*.srt'))):
    offset = i * chunk_dur
    with open(srt_file, 'r') as f:
        content = f.read().strip()
    # parse SRT entries
    blocks = re.split(r'\n\n+', content)
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2 and '-->' in lines[0]:
            time_line = lines[0]
            text = '\n'.join(lines[1:])
            # add offset to timestamps
            m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', time_line)
            if m:
                start_s = int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)) + int(m.group(4))/1000 + offset
                end_s = int(m.group(5))*3600 + int(m.group(6))*60 + int(m.group(7)) + int(m.group(8))/1000 + offset
                sh, sm, ss, sms = int(start_s//3600), int(start_s%3600//60), int(start_s%60), int(start_s%1*1000)
                eh, em, es, ems = int(end_s//3600), int(end_s%3600//60), int(end_s%60), int(end_s%1*1000)
                all_entries.append(f'{idx}\n{sh:02d}:{sm:02d}:{ss:02d},{sms:03d} --> {eh:02d}:{em:02d}:{es:02d},{ems:03d}\n{text}\n')
                idx += 1

with open('/tmp/video_audio.srt', 'w') as f:
    f.write('\n'.join(all_entries))
print(f'Merged {idx-1} segments into /tmp/video_audio.srt')
"
```

**模型选择策略：**
- `tiny`：速度最快（约3-5分钟/25分钟音频），中文准确率可接受，**默认使用**
- `base`：更准确，但慢约3倍。当视频内容技术性很强、术语密集时考虑使用
- `small`：最准确，但 CPU 上极慢，仅在特殊场景使用

> **预估耗时：25分钟音频用 tiny + 5段并行 → 约3-5分钟转录**（对比之前 base 单进程 15-20分钟）

#### 策略 C：YouTube 等非 B站
```bash
yt-dlp -x --audio-format mp3 -o "/tmp/video_audio.%(ext)s" "URL"
ffmpeg -i /tmp/video_audio.mp3 -ar 16000 -ac 1 /tmp/video_audio.wav -y
# 然后同策略 B 的步骤 4-6（分段并行转录）
```

### Step 3：优化转录文本

**委托 contextual-subtitle-fixer**（读取其 SKILL.md 按指引操作）：
1. 读取 SRT 文件
2. 语境分析 + ASR 纠错
3. 去口语化 + 结构化为 Markdown 文章

### Step 4：生成三件套产出物

#### ① 完整版文章

格式规范：
```markdown
# {Video Title}

> 来源：{Channel Name} | {Video ID}
> 时长：{Duration}
> 整理日期：{YYYY-MM-DD}

---

## 一、{Section 1 Title}

### 1.1 {Subsection}

{正文内容... 支持列表、加粗、引用等}

> {金句引用}

**关键数据：**
- 指标A：数据
- 指标B：数据

## 二、{Section 2 Title}
...

---

## 关键数据汇总

| 指标 | 数据 |
|---|---|
| ... | ... |

---

*整理自"{Channel}"视频，由 Whisper 转录并经 AI 优化整理*
```

#### ② 精简版

格式规范：
```markdown
# {Video Title} 精简版

## 核心要点

**① {要点1标题}：{一句话概括}**
- 关键论据1
- 关键论据2

**② {要点2标题}：{一句话概括}**
- ...

## 关键数据速览

- 数据1：xxx
- 数据2：xxx
```

#### ③ 思维导图（HTML 模板 + Puppeteer 截图）

模板位置：`skills/video-to-article/mindmap-template.html`

**使用方式：** 复制模板到 `/tmp/mindmap.html`，替换占位符内容，然后截图。

```bash
cp skills/video-to-article/mindmap-template.html /tmp/mindmap.html
# 编辑 /tmp/mindmap.html，替换 {{}} 占位符为实际内容
```

**模板结构：**
- 中心圆：标题 + 副标题
- 右侧分支（r1, r2, r3...）：主要内容，每个分支有彩色胶囊 L1 + 白卡片 items
- 左侧分支（l1, l2, l3...）：补充内容（数据/总结/要点），文字右对齐
- JS 自动测量高度、防碰撞布局、动态贝塞尔连线

**可配置项：**
- 分支数量：增减 HTML 中的 branch div，对应修改 JS 中的 `rightIds`/`leftIds` 数组
- 颜色主题：切换 branch 上的 `.t-{name}` class（amber/green/blue/rose/slate/teal/purple/orange/crimson/indigo）
- 卡片宽度：修改 `.item { width: 360px }`
- 间距：修改 JS 中的 `GAP` 常量

**截图命令：**
```bash
node -e "
const puppeteer = require('/opt/homebrew/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 2400, height: 1600, deviceScaleFactor: 2 });
  await page.goto('file:///tmp/mindmap.html', { waitUntil: 'networkidle0' });
  await page.waitForFunction(() => document.title === 'READY', { timeout: 5000 });
  await page.screenshot({ path: '/tmp/mindmap.png', fullPage: false });
  await browser.close();
  console.log('done');
})();
"
```

### Step 5：保存到 Obsidian

**统一使用 `obsidian` CLI 操作，不直接写文件路径。**

```bash
# 保存完整版文章
obsidian create path="notes/{Video Title}.md" content="$(cat /tmp/article_full.md)" overwrite

# 保存精简版
obsidian create path="notes/{Video Title}_精简版.md" content="$(cat /tmp/article_brief.md)" overwrite

# 思维导图图片直接复制到 Obsidian 路径（obsidian CLI 不支持二进制文件）
cp /tmp/mindmap.png "/Users/whyiyhw/data/openclaw/notes/{Video Title}_思维导图.png"
```

**注意事项：**
- `obsidian create path=` 用相对路径（相对于 vault 根目录），不用绝对路径
- `content=` 传内容文本，复杂内容先写入临时文件再用 `$(cat /tmp/xxx)` 读取
- `overwrite` 确保重复执行时不报错
- 思维导图是二进制图片，obsidian CLI 不支持，直接 `cp` 到 vault 目录
- 产品相关内容放 `ideas/`，一般笔记放 `notes/`，日志放 `logs/`

### Step 6：发送到 Telegram

```bash
# 文件必须先复制到 workspace 目录（openclaw 只允许发送该目录下的文件）
cp "{obsidian文件}" ~/.openclaw/workspace/

# 发送
openclaw message send --channel telegram -t {chat_id} --media "{workspace下的路径}" --force-document -m "{描述}"

# 发送完毕清理 workspace 中的临时副本
rm "{workspace下的临时文件}"
```

三件套分三条消息发送：
1. `📰 完整版文章` — force-document
2. `📋 精简版` — force-document
3. `🧠 思维导图` — 图片直接发送

### Step 7：清理临时文件

```bash
rm -f /tmp/video_audio.m4s /tmp/video_audio.wav /tmp/video_audio.srt /tmp/mindmap.html /tmp/mindmap.png
```

### Step 8：回复用户

在聊天中给出一句话总结 + 三件套已发送的确认。

---

## 编排优化要点（踩坑总结）

### 音频下载稳定性
- ❌ bilibili-all-in-one 的 httpx 流式下载 → 海外网络不稳定，反复断连
- ✅ 用 player.get_playurl 获取直链 + curl 下载 → curl 自带重试，稳定可靠
- **不要用** subtitle download 的内置 fallback

### 转录工具选择
- ❌ 系统 whisper CLI（Python 3.14）→ 25分钟视频会 OOM kill
- ✅ venv 中的 faster-whisper（int8 量化）→ 省内存，支持分段并行
- **默认用 `tiny` 模型**（速度×5），中文准确率够用；术语密集场景用 `base`
- **分段并行**：ffmpeg 切5分钟片段 → multiprocessing.Pool 同时转录 → 合并修正时间戳
- **转录命令统一走** `bilibili-all-in-one/.venv/bin/python` + faster-whisper

### Python 环境
- 系统 Python 3.14 有 pyexpat bug → 不要用
- bilibili-all-in-one 的 venv（Python 3.12）已安装所有依赖 → 统一用它

### 思维导图（HTML 模板）
- 模板位于 `skills/video-to-article/mindmap-template.html`
- 只需替换 `{{}}` 占位符内容，不需要改布局代码
- JS 自动处理防碰撞和连线，不管内容多少都不会重叠
- 截图前等 `document.title === 'READY'` 信号（JS 布局完成后设置）

## Tips

- **25分钟视频约需 3-5 分钟转录**（tiny 模型 + 5段并行），之前的 base 单进程需要 15-20 分钟
- **先检查 CC 字幕再走转录**，能省大量时间。无 CC 时直接跳策略 B，不试 fallback
- **tiny 模型对中文够用**，除非视频术语极密集才考虑 base
- **所有文件发完后再回复用户**，避免中途被打断
- **Obsidian 路径优先用 `notes/`**，产品相关才放 `ideas/`
- **用 `obsidian` CLI 保存文件**（`obsidian create path=... content=...`），不要直接写文件到 vault 路径
- 二进制文件（图片）仍用 `cp` 直接复制到 vault 目录

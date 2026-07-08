---
name: xhs-content-extractor
description: "提取小红书笔记完整文案，支持图文和视频两种形式。图文笔记自动 OCR 提取图片文字，视频笔记下载并分段并行转录为文字，同时抓取评论区反馈。触发词：小红书文案、提取文案、视频转文字、图文OCR、xhs extract、小红书提取、视频转录、笔记文案。当用户分享小红书链接并要求提取/整理/总结内容时触发。"
---

# 小红书文案提取

一键提取小红书笔记完整内容：正文 + 图片文字(OCR) / 视频转录 + 评论区反馈。

## 触发条件

**直接触发：**
- 用户发小红书链接 + 要求提取文案/转文字/总结内容
- 用户说"帮我提取这个小红书的文案"

**不触发：**
- 搜索小红书内容 → 用 `xiaohongshu-search-summarizer`
- 下载小红书视频文件本身 → 用 `opencli xiaohongshu download`

## Obsidian 存放规则

```
/Users/whyiyhw/data/openclaw/   ← vault 根目录
├── inbox/      ← 默认存放位置（AI 首选写入点，小红书文案放这里）
├── ideas/      ← 产品创意
├── notes/      ← 所有笔记（学习笔记、视频转文章等）
└── logs/       ← 日志报告
```

**小红书文案 → `inbox/`**（新内容暂存，定期整理到对应分类）

保存命令：
```bash
obsidian create path="inbox/{title}.md" content="$(cat {output_dir}/extracted.md)" overwrite
```
- 用 `obsidian` CLI 操作，不直接写文件
- `overwrite` 防重复执行报错
- 文件名用笔记标题

## 依赖

| 工具 | 用途 |
|---|---|
| `scripts/xhs-fetch.py` | 笔记元信息 + 图片下载 + 评论抓取 |
| `opencli xiaohongshu download` | 视频下载 |
| `ffmpeg` | 音频提取 + 分段 |
| `faster-whisper` (bili venv) | 视频音频转录 |
| `tesseract` | 图片 OCR |

## 全流程

收到小红书链接后，**不问直接跑**。

### Step 1: 运行提取脚本

```bash
bash <skill_dir>/scripts/extract.sh "<url_or_shortlink>" [--output-dir /tmp/xhs-extract]
```

脚本自动判断笔记类型：
- **图文笔记(normal)**: OCR 识别所有图片文字
- **视频笔记(video)**: 下载视频 → ffmpeg 提取音频 → 分段 → faster-whisper 并行转录

产出文件：
- `extracted.md` — 结构化文案（正文 + OCR/转录 + 评论区）
- `post.json` — 完整原始数据

### Step 2: ASR 纠错（仅视频笔记）

视频转录后，OCR/ASR 识别可能有错别字（尤其中英混说）。读取 `extracted.md`，用 contextual-subtitle-fixer 的方法修正明显错误：
- 人名、产品名修正（ChatGPT→ChatGPT, Supabase→Supabase, Figma→Figma）
- 术语修正（PRG→PRD, 靠的→ChatGPT, 真奶→Gemini, 寫→写）
- 去除重复、口误

### Step 3: 保存到 Obsidian

```bash
# 提取标题
TITLE=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/post.json'))['note']['title'])")

# 保存到 inbox
obsidian create path="inbox/${TITLE}.md" content="$(cat $OUTPUT_DIR/extracted.md)" overwrite
```

### Step 4: 输出给用户

1. 在聊天中发送修正后的完整文案
2. 如需发文件：复制到 workspace 后通过 `MEDIA:` 指令发送

## 输出格式

```markdown
# {标题}

> 作者：{作者}
> ❤️ {赞}  ⭐{收藏}  💬{评论数}
> 类型：图文/视频

---

## 正文

{笔记正文}

## 图片文字（OCR） / 视频转录全文

{OCR文字 或 转录全文}

## 标签

#tag1 #tag2

## 评论区精选

- **用户A** ❤️3: 评论内容
- **用户B**: 评论内容
- **作者(置顶)**: 作者补充说明

---

*提取自小红书笔记 {note_id}*
```

## 关键细节

- **faster-whisper 用 bili venv**: `$HOME/.openclaw/workspace/skills/bilibili-all-in-one/.venv/bin/python`，不用系统 whisper CLI（CPU 巨慢且 OOM）
- **分段并行转录**: 5分钟一段，最多5段同时跑，5分钟视频约1-2分钟转录完
- **tiny 模型默认**: 中文够用，术语密集时考虑 base
- **评论通过 opencli**: 需要 xsec_token 签名 URL，xhs-fetch.py 内部处理
- **tesseract OCR**: `chi_sim+eng` 双语，对设计图/信息图效果一般，图片文字少时会返回空

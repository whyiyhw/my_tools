---
name: public-account-writer
description: >
  公众号内容创作。基于人设生成符合调性的公众号文章、标题、选题。
  触发词：公众号、写文章、选题、标题、内容、公众号创作、写推文。
---

# 公众号内容创作

## 核心流程

**所有内容创作（选题、标题、正文、改写、配图、打包）全部委托给 Codex 的 `wechat-writing-expert` skill。**

Codex skill 位置：`/Users/whyiyhw/.codex/skills/wechat-writing-expert`

## Sandbox 选择

| 模式 | 用途 |
|------|------|
| `-s workspace-write` | 纯写作、选题、改写、审稿（默认） |
| `-s danger-full-access` | 需要生图（`image_gen`）、截网页、网络访问时 |

## 编排流程（对齐 Codex 10步）

### 判断任务模式

先判断用户需求属于哪种模式，再决定走多少流程：

| 模式 | 触发场景 | 流程 |
|------|---------|------|
| **Quick** | 改标题、润色段落、短文案、直接改 | 直接调 Codex，跳过项目流程 |
| **Full Article** | 写一篇完整新文章 | 走完整 10 步 |
| **Deep Analysis** | 数据驱动分析、算账、看空、逆向判断、拆参数 | Full Article + 强制调研 + 强制深度审稿 |
| **Commercial** | 商单、赞助、品牌合作 | Full Article + 商业合规检查 |
| **Personal Essay** | 个人观点/经历/反思 | Full Article + 优先素材库+Obsidian |

模式可叠加，如 "Commercial + Full Article"。

---

### Step 1: 理解任务，保存 Brief

**做什么：** 把用户需求整理成 brief，让 Codex 保存到项目目录。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 创建项目并保存 brief，主题：{主题}，目标读者：{读者}，字数要求：{字数}，截止时间：{时间}，特殊要求：{要求}'
```

**商单额外信息：** 品牌/产品名、必带卖点、需要证据的声明、禁用词、竞品边界、披露要求、客户审批节点。

**交互：** Brief 关键点要跟用户确认（选题方向、目标读者、关键约束），再进入下一步。

---

### Step 2: 调研，建知识库

**做什么：** 涉及新产品、新技术、近期事件、不确定事实 → 让 Codex 调研并整理。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 为项目 {项目名} 调研 {主题}，保存到 _knowledge_base/，优先官方来源'
```

**简单话题可跳过此步。**

**⚠️ Deep Analysis Mode 不可跳过。** 必须满足：
- ≥3个独立来源交叉验证
- 竞品/替代方案对比
- 收集反面观点和反例
- 数据来源标注（官方/实测/估算）

---

### Step 3: 选题讨论

**做什么：** 让 Codex 出 3-4 个选题方向，**等用户选择后再继续**。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 基于项目 {项目名} 的 brief 和知识库，给 3-4 个选题方向，含标题、核心角度、优缺点、选题评分卡'
```

**⚠️ 关键：必须等用户选完再进入 Step 5-6。不要替用户决定选题。**

如有 Obsidian 素材，加上：
```bash
'先用 search_obsidian.py 检索「关键词1」「关键词2」，再给选题'
```

---

### Step 4: 协作文档（按需）

**做什么：** 需要用户测试、截图、提供数据时，让 Codex 创建协作文档。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 为项目 {项目名} 创建协作文档，列出需要用户提供的：截图清单、测试任务、数据'
```

**没有外部依赖时可跳过。**

---

### Step 5: 风格学习 + 素材准备

**做什么：** 让 Codex 读历史文章、素材库、Obsidian 笔记，提取风格特征。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 学习写作风格：读 personal-material-lib 历史文章 + 搜索 Obsidian「关键词」，提取开头模式、段落节奏、用词习惯'
```

**我的额外职责：**
- 读 `PERSONA.md`，确保传给 Codex 的 prompt 包含人设要求
- Personal Essay 模式下，优先让 Codex 从素材库和 Obsidian 找真实经历、场景、判断

**Deep Analysis Mode 额外学习：**
- 历史深度分析文章的数据呈现方式（表格、算账、对比）
- 论证结构（推导过程、反面论证的使用）
- 参数拆解和解释大众化的写法

---

### Step 6: 起草

**做什么：** 基于选题 + 风格 + 素材，让 Codex 写初稿。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 为项目 {项目名} 写初稿，选题：{用户选的选题}，风格参考已学习的结果'
```

**输出：** `drafts/[项目名]-初稿.md`

**Deep Analysis Mode 强制要求：**
- ≥1个数据对比表格（specs/价格/性能/适用场景）
- 完整推导过程（数据→计算→含义→边界，不跳步）
- ≥1个反面论证（"什么情况下判断不成立"）
- 明确的适用边界（对谁有效/对谁无效）
- 数据来源标注

---

### Step 7: 六轮审稿

**做什么：** 让 Codex 执行六轮审稿，我也同步做自检。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 对初稿执行六轮审稿：1.hook检查 2.内容/事实检查 3.风格/去AI味 4.细节/节奏 5.反AI检测（信息熵/句长方差/词汇重复/论点完整度/真实细节注入/结构不规则性） 6.深度检查，保存终稿到 drafts/[项目名]-终稿.md'
```

**我的自检清单（同步过一遍）：**

| 维度 | 检查项 |
|------|--------|
| **Hook** | 前3行是否制造好奇/共鸣/冲突？ |
| **内容** | 事实准确？有数据或亲身经历？不是空谈？ |
| **风格** | 去掉了AI味（"首先其次"、"值得注意"）？口语化？ |
| **细节** | 句子15-25字？手机友好段落？朗读节奏自然？ |
| **反AI检测** | 信息密度有高低起伏？句长方差大？连接词不重复？论点有不完整的？有3+个真实细节？结构有打破模式的地方？ |
| **深度**（Deep Analysis 必查） | 有数据对比表？推导完整不跳步？有反面论证？有适用边界？技术人挑不出硬伤？数据来源标注了？ |
| **商业** | 标题有吸引力？字数匹配文章类型？文末有互动引导？符合内容比例？标签含AI热门词？ |

**输出：** `drafts/[项目名]-终稿.md`

---

### Step 8: 配图

**做什么：** 终稿确认后，让 Codex 生成所有图片。

```bash
codex exec --skip-git-repo-check -s danger-full-access -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 为终稿生成所有图片，终稿路径：{path}'
```

**⚠️ 必须用 `danger-full-access`（生图需要网络访问）。**

**图片类型决策：**
| 需求 | 方式 |
|------|------|
| 封面/概念图/场景 | `image_gen`（GPT Image 2，无需 API key） |
| 产品截图/UI | `browser-use` 截图 |
| 信息图/流程图/数据可视化 | HTML + `browser-use` 截图 |

**生图 Prompt 要点：**
- 英文 prompt，避免中文（GPT Image 中文渲染差）
- 写明 "no readable text, no logos, no watermark"

**图片管理：**
- 生成后从 `$CODEX_HOME/generated_images/<session>/` 复制到项目 `images/` 目录
- 一般：1张封面 + 3-7张正文图

---

### Step 9: 确认与打包

**做什么：** 用户确认终稿和配图后，生成发布包。

```bash
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 为项目 {项目名} 打包发布版，包含：正文+图片路径+图片清单+来源备注+商业披露（如有）'
```

**输出：** `published/[项目名]-发布版.md`

**交付前验证：**
- [ ] 标题最终版
- [ ] 开头 hook 有效
- [ ] 事实/声明有出处
- [ ] 图片文件存在且路径正确
- [ ] 手机端段落节奏 OK
- [ ] Brief 中的要求全部满足
- [ ] 商单：卖点植入自然、禁用词已排除、披露已包含

---

### Step 10: 发布到公众号

**做什么：** 将排版后的文章发布到微信公众号。

**发布流程（手动，最稳定）：**

1. 打开 [editor.huasheng.ai](https://editor.huasheng.ai/) → 选样式（推荐：默认公众号风格 / Claude / 优雅简约）
2. 粘贴终稿 Markdown → 右侧实时预览
3. 点「复制到公众号」
4. 打开 [mp.weixin.qq.com](https://mp.weixin.qq.com/) → 新建图文 → Ctrl+V 粘贴
5. 手动插入正文图片（从项目 `images/` 目录逐张上传）
6. 添加封面图、摘要、标签
7. 预览 → 发布

**为什么不自动化这一步：**
- `opencli weixin create-draft` 用 `insertText` 填充，会把 HTML 当纯文本，样式不生效
- 浏览器自动化剪贴板（`navigator.clipboard`）在无头模式下不可用
- `insertHTML` 方案可行但不稳定，不如手动复制粘贴可靠
- 花生排版器输出的内联样式 HTML 与公众号编辑器完美兼容

**可选：草稿箱快速创建（无样式，纯文本模式）**
```bash
opencli weixin create-draft "$(cat drafts/终稿.md)" --title "标题" --author "whyiyhw"
```
用于快速创建草稿占位，再到编辑器里手动排版。

---

## Quick Mode 快捷命令

不需要走完整流程时：

```bash
# 标题选项
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 帮我优化标题：{原标题}，给 5 个版本并说明理由'

# 润色/改写
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 帮我润色这段，去AI味：{内容或文件路径}'

# 短文案
codex exec --skip-git-repo-check -s workspace-write -C ~/.openclaw/workspace \
  'Use $wechat-writing-expert 帮我写一段公众号 {用途} 文案，要求：{要求}'
```

## 素材传递方式

| 素材来源 | 传递方式 |
|---------|---------|
| Obsidian 笔记 | 让 Codex 用 `search_obsidian.py` 检索 |
| 本地文件（转录/摘要） | 在 prompt 中引用文件路径 |
| 对话中的内容 | 直接写在 prompt 里 |
| 视频转录 | 先保存到临时文件，再让 Codex 读取 |

## 文件结构

```
public-account-writer/
├── SKILL.md          # 本文件（编排流程）
├── PERSONA.md        # 创作人设（传给 Codex 的上下文）
└── drafts/           # 草稿存档（按日期）
```

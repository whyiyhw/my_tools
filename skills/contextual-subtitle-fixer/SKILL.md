---
name: contextual-subtitle-fixer
description: Fix speech recognition errors in SRT subtitle files using contextual analysis, with optional polishing into structured Markdown articles. Reads subtitle content, corrects ASR errors, removes filler words, and restructures into well-organized documentation. Supports Chinese and English. Use when: (1) Correcting Whisper/ASR recognition errors, (2) Fixing technical terminology in subtitles, (3) Improving subtitle accuracy through context understanding, (4) Processing ML/AI/technical video subtitles, (5) Converting subtitles to structured Markdown articles, (6) Removing filler words and polishing spoken content into written form.
---

# Contextual Subtitle Fixer

Fix speech recognition errors in subtitles through contextual analysis — no external scripts needed. The agent reads, understands, and corrects.

## Workflow

### 1. Read the SRT file

Use the `read` tool to load the subtitle file:

```
read /path/to/subtitle.srt
```

### 2. Analyze & Correct

After reading the full content, perform contextual correction:

**Analysis Strategy:**
- **Sliding context window** — for each subtitle line, consider 3-5 lines before and after it
- **Domain detection** — identify the technical domain (ML, AI, NLP, web dev, etc.) from overall content
- **Error patterns** — look for common ASR errors: homophones, split words, merged words, technical terms
- **Semantic consistency** — ensure corrections make sense in context, not just isolated word replacement

**Common ASR Error Patterns (Chinese):**
| Error | Likely Correction | Context Clue |
|-------|------------------|--------------|
| 头盆/通盆 | token | ML/programming context |
| 神经网络/深井网络 | 神经网络 | ML discussion |
| 变换器 | Transformer | NLP context |
| 注意力机制 | 注意力机制 | Transformer discussion |
| 提示工程/提示词工程 | prompt engineering | LLM discussion |
| 模型参数 | 模型参数 | model training context |
| 批量大小/patch大小 | batch size | training context |

**Common ASR Error Patterns (English):**
| Error | Likely Correction | Context Clue |
|-------|------------------|--------------|
| transformer | Transformer | when referring to the architecture |
| atension | attention | NLP context |
| gradent | gradient | optimization context |
| nevrol | neural | ML context |

### 3. Output Corrected Text

Write the corrected result:

- **Corrected text** → `write` to output path (e.g., `output/{title}_fixed.txt`)
- **Correction log** → list all changes made with brief reason (optional, useful for review)

### 4. Polish to Markdown (Optional)

When the user requests polishing, structuring, or converting to a readable article format, transform the corrected text into a well-structured Markdown document.

**Transformation Rules:**

1. **Remove filler words & verbal tics** — delete 口语化表达 such as:
   - Chinese: 然后、其实、就是说、我们来看一下、大家知道、对吧、嗯、那个、就是说
   - English: you know, like, so basically, I mean, right, well, okay so
   - Keep these ONLY when they carry actual meaning in context

2. **Merge fragmented sentences** — combine broken sentences from subtitle pacing into complete, fluent sentences

3. **Restructure into logical sections** — group related content under meaningful headings:
   - Detect topic boundaries (e.g. "下面我们来看..." signals a new section)
   - Create `##` headings for each topic
   - Add `###` subheadings for subtopics when needed

4. **Preserve all technical content** — keep terminology, formulas, architecture descriptions, and code references intact and accurate

5. **Add structural elements** where appropriate:
   - Use bullet points for lists/enumerations
   - Use `>` blockquotes for key definitions or important takeaways
   - Use `---` horizontal rules between major sections
   - Use **bold** for key terms on first introduction

6. **Output** → `write` to `output/{title}_polished.md`

**Example Input (corrected subtitle):**
```
Hello 大家好 我是九月
今天想给大家分享一下最近刚出的 DeepSeek V4
DeepSeek V4 里面的一些模块 包括 MLA DSA 还有 MTP
我们之前都有介绍过
今天主要想给大家介绍一下 DeepSeek V4 里面的一个压缩注意力模块
其实它主要是对 KV 的一个压缩
```

**Example Output (polished Markdown):**
```markdown
# DeepSeek V4 压缩注意力模块（CSA & HCA）详解

## 概述

DeepSeek V4 引入了多个新模块，包括 **MLA**、**DSA** 和 **MTP**。本文重点介绍其中的**压缩注意力模块**——其核心思想是对 KV（Key-Value）进行压缩，从而在支持 100 万 attention 窗口的同时，将 KV cache 显存占用保持在较低水平。
```

## Usage Instructions

When the user asks to fix subtitles, follow these steps:

1. **Read** the SRT file with the `read` tool
2. **Understand** the full context — scan all content to detect domain and identify errors
3. **Correct** each error using surrounding context and domain knowledge
4. **Write** the corrected output to `output/{title}_fixed.txt`
5. **Report** a summary of changes to the user

If the user also requests polishing/structuring:

6. **Polish** the corrected text into structured Markdown following Step 4 rules
7. **Write** the polished Markdown to `output/{title}_polished.md`
8. **Report** completion to the user

## Example Prompt Triggers

- "Fix the subtitles in this SRT file"
- "修正这个字幕文件"
- "This subtitle has ASR errors, fix them"
- "Fix the whisper output"
- "修正字幕并转成文章"
- "Fix subtitles and convert to markdown article"
- "把字幕整理成结构化的笔记"

## Output Format

**Step 3 output** — corrected plain text (one subtitle per line, no timecodes unless requested):

```
今天我们来讲解 DeepSeek V4 的 CSAHCA 模块
这个模块的核心思想是利用多头注意力机制
...
```

**Step 4 output** — polished Markdown article:

```markdown
# [Article Title]

## Section 1
Polished content...

## Section 2
Polished content...
```

**Correction log** (when useful):

```
[Line 12] "头盆" → "token" (ML context: discussing model parameters)
[Line 45] "深井网络" → "神经网络" (ML context: discussing deep learning)
```

#!/usr/bin/env bash
# 小红书内容提取 — 图文 OCR / 视频转录 / 评论
# 用法: bash extract.sh <url_or_shortlink> [--output-dir /tmp/xhs-extract]
set -euo pipefail

URL="$1"
OUTPUT_DIR="${2:-/tmp/xhs-extract}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PY="$HOME/.openclaw/workspace/skills/bilibili-all-in-one/.venv/bin/python"
FETCH_PY="$SCRIPT_DIR/xhs-fetch.py"

mkdir -p "$OUTPUT_DIR"

echo "=============================="
echo "📌 小红书内容提取"
echo "=============================="

# ===== Step 1: 抓取笔记元信息 + 图片 + 评论 =====
echo ""
echo "【Step 1/4】抓取笔记信息 + 图片 + 评论..."
python3 "$FETCH_PY" "$URL" --output-dir "$OUTPUT_DIR" 2>&1 | grep -E "^(📌|👤|📝|🏷️|❤️|📷|🔍|💬|📁|✅|⚠️|🔗|   )" || true

# 判断笔记类型
NOTE_TYPE=$(python3 -c "
import json
with open('$OUTPUT_DIR/post.json') as f:
    d = json.load(f)
print(d['note'].get('type', 'normal'))
")

echo ""
echo "📝 笔记类型: $NOTE_TYPE"

# ===== Step 2: 图文 OCR 或 视频下载 =====
if [ "$NOTE_TYPE" = "normal" ]; then
    echo ""
    echo "【Step 2/4】图文笔记 — 提取图片中所有文字..."
    python3 "$SCRIPT_DIR/ocr_images.py" "$OUTPUT_DIR"
    echo ""
    echo "【Step 3/4】跳过（图文笔记无需转录）"
    echo "【Step 4/4】生成结构化文案..."
else
    echo ""
    echo "【Step 2/4】视频笔记 — 下载视频..."
    opencli xiaohongshu download "$URL" --output "$OUTPUT_DIR" 2>&1 | tail -3 || true

    VIDEO_FILE=$(find "$OUTPUT_DIR" -name "*.mp4" -type f | head -1)
    if [ -z "$VIDEO_FILE" ]; then
        echo "❌ 视频下载失败"
        exit 1
    fi
    echo "  ✅ 视频已下载: $VIDEO_FILE"

    echo ""
    echo "【Step 3/4】提取音频 + 转录 (faster-whisper)..."
    ffmpeg -i "$VIDEO_FILE" -vn -ar 16000 -ac 1 "$OUTPUT_DIR/audio.wav" -y -loglevel error
    "$VENV_PY" "$SCRIPT_DIR/transcribe.py" "$OUTPUT_DIR"

    echo ""
    echo "【Step 4/4】生成结构化文案..."
fi

# ===== Step 5: 生成结构化 Markdown =====
python3 "$SCRIPT_DIR/generate_md.py" "$OUTPUT_DIR" "$NOTE_TYPE"

# ===== Step 6: 保存到 Obsidian =====
TITLE=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/post.json'))['note']['title'])")
OBSIDIAN_PATH="inbox/${TITLE}.md"

if command -v obsidian &>/dev/null; then
    obsidian create path="$OBSIDIAN_PATH" content="$(cat "$OUTPUT_DIR/extracted.md")" overwrite 2>/dev/null && \
        echo "📓 已保存到 Obsidian: $OBSIDIAN_PATH" || \
        echo "⚠️ Obsidian 保存失败（桌面端可能未运行）"
else
    echo "⚠️ obsidian CLI 不可用，跳过保存"
fi

# ===== Step 7: 自动打标签 + 关联产品 =====
TAG_SCRIPT="$HOME/.openclaw/workspace/scripts/tag_inbox.py"
VAULT="$HOME/data/openclaw"
if [ -f "$TAG_SCRIPT" ]; then
    python3 "$TAG_SCRIPT" "$VAULT/inbox" 2>&1 | grep -E "^(📄|   |✅)" || true
fi

echo ""
echo "=============================="
echo "✅ 提取完成！"
echo "📁 输出目录: $OUTPUT_DIR/"
echo "   extracted.md — 结构化文案（正文+OCR/转录+评论）"
echo "   post.json    — 完整原始数据"
if [ -n "${TITLE:-}" ]; then
    echo "📓 Obsidian: inbox/${TITLE}.md"
fi
echo "=============================="

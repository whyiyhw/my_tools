#!/usr/bin/env python3
"""生成结构化 Markdown 文案"""
import json, os, sys

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/xhs-extract"
    note_type = sys.argv[2] if len(sys.argv) > 2 else "normal"

    with open(os.path.join(output_dir, "post.json")) as f:
        data = json.load(f)

    note = data["note"]
    comments = data.get("comments", [])

    lines = []
    lines.append(f"# {note['title']}")
    lines.append("")
    lines.append(f"> 作者：{note['author']}")
    lines.append(f"> ❤️ {note['likes']}  ⭐{note['collects']}  💬{note['comments_count']}  🔄{note.get('share_count', '?')}")
    lines.append(f"> 类型：{'视频' if note_type == 'video' else '图文'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 正文
    lines.append("## 正文")
    lines.append("")
    lines.append(note["content"])
    lines.append("")

    # 图片 OCR 文字（图文笔记）
    if note_type == "normal":
        ocr_file = os.path.join(output_dir, "ocr_results.json")
        if os.path.exists(ocr_file):
            with open(ocr_file) as f:
                ocr_data = json.load(f)
            if ocr_data:
                lines.append("## 图片文字（OCR）")
                lines.append("")
                for item in ocr_data:
                    text = item["text"].strip()
                    if text:
                        lines.append(f"**图片 {item['image_index']}:**")
                        lines.append("")
                        lines.append(text)
                        lines.append("")

    # 视频转录（视频笔记）
    if note_type == "video":
        transcript_file = os.path.join(output_dir, "transcript.txt")
        if os.path.exists(transcript_file):
            with open(transcript_file) as f:
                transcript = f.read()
            if transcript.strip():
                lines.append("## 视频转录全文")
                lines.append("")
                lines.append(transcript.strip())
                lines.append("")

    # 标签
    if note.get("tags"):
        lines.append("## 标签")
        lines.append("")
        lines.append(" ".join(f"#{t}" for t in note["tags"]))
        lines.append("")

    # 评论
    if comments:
        lines.append("## 评论区精选")
        lines.append("")
        for c in comments:
            author = c.get("author", c.get("nickName", ""))
            text = c.get("text", c.get("content", ""))
            likes = c.get("likes", c.get("likeCount", ""))
            like_str = f" ❤️{likes}" if likes else ""
            lines.append(f"- **{author}**{like_str}: {text}")
        lines.append("")

    lines.append("---")
    lines.append(f"*提取自小红书笔记 {note['note_id']}*")

    md = "\n".join(lines)
    md_path = os.path.join(output_dir, "extracted.md")
    with open(md_path, "w") as f:
        f.write(md)

    print(f"✅ 结构化文案已保存: {md_path}")
    print(f"📊 正文 {len(note['content'])} 字 | 评论 {len(comments)} 条")

if __name__ == "__main__":
    main()

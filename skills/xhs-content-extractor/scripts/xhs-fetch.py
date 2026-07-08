#!/usr/bin/env python3
"""
小红书帖子完整抓取（内容 + 图片 + 评论）
用法: python3 xhs-fetch.py <url_or_shortlink> [--output-dir /tmp/xhs-post]
输出: JSON + 图片文件
"""
import json
import re
import sys
import os
import urllib.request
import subprocess
import argparse
from pathlib import Path


def resolve_short_link(url: str) -> str:
    """解析短链接为完整 URL"""
    if "xhslink.com" not in url:
        return url
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
        })
        # 不跟随重定向，只取 Location
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        opener = urllib.request.build_opener(NoRedirect)
        try:
            opener.open(req, timeout=10)
        except urllib.error.HTTPError as e:
            if e.code == 302:
                return e.headers.get("Location", url)
            raise
    except Exception:
        pass
    # Fallback: 用 curl 跟随重定向
    result = subprocess.run(
        ["curl", "-sL", "-o", "/dev/null", "-w", "%{url_effective}", url],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout.strip() or url


def fetch_ssr(url: str) -> dict:
    """抓取 SSR HTML 并解析 INITIAL_STATE"""
    result = subprocess.run(
        ["curl", "-sL", url,
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"],
        capture_output=True, text=True, timeout=15
    )
    html = result.stdout

    m = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*</script>', html, re.DOTALL)
    if not m:
        return {}

    raw = m.group(1).replace(':undefined', ':null')
    return json.loads(raw)


def extract_note(data: dict) -> dict:
    """从 INITIAL_STATE 提取笔记数据"""
    note_map = data.get("note", {}).get("noteDetailMap", {})
    for nid, ndata in note_map.items():
        note = ndata.get("note", {})
        interact = note.get("interactInfo", {})
        user = note.get("user", {})

        # 图片
        images = []
        for img in note.get("imageList", []):
            img_url = img.get("urlDefault", img.get("url", ""))
            images.append({
                "url": img_url,
                "width": img.get("width", ""),
                "height": img.get("height", ""),
            })

        # 标签
        tags = [t.get("name", "") for t in note.get("tagList", []) if t.get("name")]

        return {
            "note_id": nid,
            "title": note.get("title", ""),
            "author": user.get("nickname", ""),
            "author_id": user.get("userId", ""),
            "content": note.get("desc", ""),
            "tags": tags,
            "likes": interact.get("likedCount", ""),
            "collects": interact.get("collectedCount", ""),
            "comments_count": interact.get("commentCount", ""),
            "share_count": interact.get("shareCount", ""),
            "images": images,
            "type": note.get("type", ""),  # normal / video
            "video_url": note.get("video", {}).get("mediaUrl", "") if note.get("video") else "",
        }
    return {}


def fetch_comments(url: str, limit: int = 20) -> list:
    """通过 OpenCLI 获取评论"""
    # 需要带 xsec_token 的完整 URL
    try:
        result = subprocess.run(
            ["opencli", "xiaohongshu", "comments", url, "--format", "json", "--limit", str(limit)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as e:
        print(f"⚠️  评论抓取失败: {e}", file=sys.stderr)
    return []


def download_images(images: list, output_dir: str) -> list:
    """下载图片到本地"""
    img_dir = os.path.join(output_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    downloaded = []

    for i, img in enumerate(images):
        url = img["url"]
        if not url:
            continue
        ext = "jpg"
        filename = f"{i+1:02d}.{ext}"
        filepath = os.path.join(img_dir, filename)

        try:
            subprocess.run(
                ["curl", "-sL", url, "-o", filepath],
                capture_output=True, timeout=15
            )
            if os.path.getsize(filepath) > 0:
                downloaded.append({
                    "index": i + 1,
                    "path": filepath,
                    "url": url,
                    "width": img.get("width", ""),
                    "height": img.get("height", ""),
                })
                print(f"  📷 图片 {i+1}/{len(images)} ✓", file=sys.stderr)
        except Exception as e:
            print(f"  📷 图片 {i+1}/{len(images)} ✗ {e}", file=sys.stderr)

    return downloaded


def ocr_image(image_path: str) -> str:
    """用 tesseract OCR 识别图片中的文字"""
    try:
        # tesseract 对中文路径有问题，需要先 cd 到文件目录
        import os
        dirname = os.path.dirname(os.path.abspath(image_path))
        basename = os.path.basename(image_path)
        result = subprocess.run(
            ["tesseract", basename, "stdout", "-l", "chi_sim+eng"],
            capture_output=True, text=True, timeout=30,
            cwd=dirname,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"OCR failed: {e}"


def main():
    parser = argparse.ArgumentParser(description="小红书帖子完整抓取")
    parser.add_argument("url", help="帖子 URL 或短链接")
    parser.add_argument("--output-dir", default=None, help="输出目录（默认 /tmp/xhs-{note_id}）")
    parser.add_argument("--no-images", action="store_true", help="不下载图片")
    parser.add_argument("--no-comments", action="store_true", help="不抓取评论")
    parser.add_argument("--no-ocr", action="store_true", help="不 OCR 识别图片文字")
    args = parser.parse_args()

    # 1. 解析短链接
    print("🔗 解析链接...", file=sys.stderr)
    full_url = resolve_short_link(args.url)
    print(f"   {full_url[:80]}...", file=sys.stderr)

    # 2. 抓取 SSR 数据
    print("📄 抓取帖子内容...", file=sys.stderr)
    ssr_data = fetch_ssr(full_url)
    note = extract_note(ssr_data)

    if not note.get("note_id"):
        print("❌ 无法获取帖子内容（可能需要登录或链接已失效）", file=sys.stderr)
        sys.exit(1)

    print(f"   ✅ {note['title'][:40]} — {note['author']} — {note['likes']}赞 {note['collects']}收藏", file=sys.stderr)

    # 输出目录
    output_dir = args.output_dir or f"/tmp/xhs-{note['note_id']}"
    os.makedirs(output_dir, exist_ok=True)

    # 3. 下载图片
    images_info = []
    if not args.no_images and note.get("images"):
        print(f"📷 下载 {len(note['images'])} 张图片...", file=sys.stderr)
        images_info = download_images(note["images"], output_dir)

    # 3.5 OCR 图片文字
    if not args.no_ocr and images_info:
        print(f"🔍 OCR 识别 {len(images_info)} 张图片...", file=sys.stderr)
        for img in images_info:
            img["ocr_text"] = ocr_image(img["path"])
            has_text = len(img["ocr_text"]) > 5
            print(f"  📝 图片 {img['index']}/{len(images_info)} {'✓' if has_text else '（无文字）'}", file=sys.stderr)

    # 4. 抓取评论
    comments = []
    if not args.no_comments:
        print("💬 抓取评论...", file=sys.stderr)
        comments = fetch_comments(full_url, limit=20)
        print(f"   ✅ {len(comments)} 条评论", file=sys.stderr)

    # 5. 组装输出
    output = {
        "meta": {
            "fetched_at": __import__("datetime").datetime.now().isoformat(),
            "source_url": args.url,
            "resolved_url": full_url,
        },
        "note": note,
        "images_downloaded": images_info,
        "comments": comments,
    }

    # 保存 JSON
    json_path = os.path.join(output_dir, "post.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n📁 已保存到 {output_dir}/", file=sys.stderr)
    print(f"   post.json — 完整数据", file=sys.stderr)
    if images_info:
        print(f"   images/ — {len(images_info)} 张图片", file=sys.stderr)

    # 打印摘要
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"📌 {note['title']}", file=sys.stderr)
    print(f"👤 {note['author']}", file=sys.stderr)
    print(f"📝 {note['content'][:100]}", file=sys.stderr)
    print(f"🏷️  {' '.join('#'+t for t in note['tags'])}", file=sys.stderr)
    print(f"❤️ {note['likes']}  ⭐{note['collects']}  💬{note['comments_count']}", file=sys.stderr)
    if comments:
        print(f"\n💬 评论:", file=sys.stderr)
        for c in comments[:5]:
            print(f"   {c.get('author','')}: {c.get('text','')[:50]}", file=sys.stderr)

    return output


if __name__ == "__main__":
    main()

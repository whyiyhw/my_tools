#!/usr/bin/env python3
"""图文笔记 OCR — 提取所有图片中的文字"""
import json, os, subprocess, sys

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/xhs-extract"
    post_file = os.path.join(output_dir, "post.json")

    with open(post_file) as f:
        data = json.load(f)

    ocr_results = []
    for img in data.get("images_downloaded", []):
        path = img.get("path", "")
        if not path or not os.path.exists(path):
            continue
        dirname = os.path.dirname(os.path.abspath(path))
        basename = os.path.basename(path)
        try:
            # Try multiple PSM modes for better coverage on styled/design images
            best_text = ""
            for psm in [3, 6, 11]:
                try:
                    result = subprocess.run(
                        ["tesseract", basename, "stdout", "-l", "chi_sim+eng", "--psm", str(psm)],
                        capture_output=True, text=True, timeout=30, cwd=dirname
                    )
                    text = result.stdout.strip()
                    if len(text) > len(best_text):
                        best_text = text
                except Exception:
                    continue

            if best_text:
                ocr_results.append({"image_index": img["index"], "text": best_text})
                print(f"  📷 图片 {img['index']}: {best_text[:80]}...")
            else:
                print(f"  📷 图片 {img['index']}: （无明显文字）")
        except Exception as e:
            print(f"  ⚠️ 图片 {img['index']} OCR 失败: {e}")

    ocr_file = os.path.join(output_dir, "ocr_results.json")
    with open(ocr_file, "w") as f:
        json.dump(ocr_results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ OCR 完成，识别 {len(ocr_results)} 张图片文字")

if __name__ == "__main__":
    main()

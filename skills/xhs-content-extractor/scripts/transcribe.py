#!/usr/bin/env python3
"""小红书视频转录 — ffmpeg 分段 + faster-whisper"""
import os, sys, glob, json, subprocess
from faster_whisper import WhisperModel

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/xhs-extract"
    audio_path = os.path.join(output_dir, "audio.wav")
    chunks_dir = os.path.join(output_dir, "chunks")

    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}", file=sys.stderr)
        sys.exit(1)

    # 分段（5分钟一段）
    os.makedirs(chunks_dir, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-i", audio_path, "-f", "segment",
        "-segment_time", "300", "-c", "copy",
        os.path.join(chunks_dir, "chunk_%03d.wav"), "-y"
    ], capture_output=True, timeout=60)

    chunks = sorted(glob.glob(os.path.join(chunks_dir, "chunk_*.wav")))
    if not chunks:
        print("❌ 分段失败", file=sys.stderr)
        sys.exit(1)

    print(f"📦 分成 {len(chunks)} 段，开始转录...", file=sys.stderr)

    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    all_text = []

    for i, chunk in enumerate(chunks):
        segments, info = model.transcribe(chunk, language="zh", vad_filter=True)
        text_parts = [seg.text.strip() for seg in segments]
        text = " ".join(text_parts)
        all_text.append(text)
        print(f"  ✅ 分段 {i+1}/{len(chunks)} 完成 ({len(text)} 字)", file=sys.stderr)

    full_text = "\n\n".join(all_text)
    out_path = os.path.join(output_dir, "transcript.txt")
    with open(out_path, "w") as f:
        f.write(full_text)

    print(f"✅ 转录完成: {len(full_text)} 字 → {out_path}", file=sys.stderr)

if __name__ == "__main__":
    main()

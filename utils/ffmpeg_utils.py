
import os
import subprocess

def trim_and_crop_with_ffmpeg(input_path: str, start: float, end: float, idx: int = 0, output_dir: str = "outputs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"reel_clip_{idx+1}.mp4")
    duration = round(end - start, 2)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-c:a", "aac",
        output_path
    ]

    print(f"\n🚀 Running FFmpeg for clip {idx+1}:\n{' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ FFmpeg Success:", result.stdout)
        return output_path if os.path.exists(output_path) else None
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg Error for clip {idx+1}:\n{e.stderr}")
        return None

import os
from pathlib import Path

AGI_ROOT = Path("C:/workspace/agi")
IMG_PATH = AGI_ROOT / "outputs" / "youtube_resonator" / "sacred_hole.png"
VIDEO_PATH = AGI_ROOT / "outputs" / "youtube_resonator" / "sacred_hole.mp4"

# FFmpeg command for Ken Burns effect (slow zoom)
# Zooming from 1.0 to 1.1 scale over 5 seconds at 30 fps
FFMPEG_CMD = (
    f'ffmpeg -loop 1 -i "{IMG_PATH}" -vf "zoompan=z=\'zoom+0.0005\':d=150:s=1920x1080" '
    f'-c:v libx264 -t 5 -pix_fmt yuv420p "{VIDEO_PATH}" -y'
)

def build_video():
    print(f"🎬 Creating video from {IMG_PATH.name}...")
    os.system(FFMPEG_CMD)
    if VIDEO_PATH.exists():
        print(f"✅ Video created: {VIDEO_PATH.name} ({VIDEO_PATH.stat().st_size} bytes)")
    else:
        print("❌ Video creation failed.")

if __name__ == "__main__":
    build_video()

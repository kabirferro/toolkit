import os
import sys
import subprocess
from pathlib import Path

# Check ffmpeg dependency
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
    subprocess.run(['ffprobe', '-version'], capture_output=True, check=True, timeout=5)
except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
    print("\n⚠  MISSING DEPENDENCY\n")
    print("ffmpeg is not installed or not in the system PATH.\n")
    print("Installation:")
    print("  Windows: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
    print("           Extract and add the 'bin' folder to the system PATH")
    print("  Linux:   sudo apt install ffmpeg")
    print("  macOS:   brew install ffmpeg\n")
    input("Press ENTER to exit...")
    sys.exit(1)

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
SRC_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

try:
    test_file = OUT_DIR / ".test_write"
    test_file.touch()
    test_file.unlink()
except Exception as e:
    print(f"\n⚠  Cannot write to 'out/': {e}\n")
    input("Press ENTER to exit...")
    sys.exit(1)

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}

print("\n=== VIDEOS TO MP4 ===\n")


def convert_to_mp4(in_path: Path, out_path: Path):
    try:
        cmd = [
            'ffmpeg', '-y', '-i', str(in_path),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            str(out_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ ffmpeg error on {in_path.name}:")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                relevant = [l for l in error_lines if any(k in l.lower() for k in ('error', 'invalid', 'failed'))]
                for line in (relevant[-5:] if relevant else error_lines[-3:]):
                    print(f"    {line}")
            return False
        print(f"✓ {in_path.name} -> {out_path.name}")
        return True
    except Exception as e:
        print(f"✗ Error converting {in_path.name}: {e}")
        return False


processed = 0
found = 0
for file_path in SRC_DIR.iterdir():
    if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
        found += 1
        success = convert_to_mp4(file_path, OUT_DIR / f"{file_path.stem}.mp4")
        if success:
            processed += 1

if found == 0:
    print("⚠  No videos found in 'src/'")
    print("   Supported formats: MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V\n")
else:
    print(f"\n=== Done! {processed}/{found} videos converted to MP4 ===\n")

input("Press ENTER to exit...")

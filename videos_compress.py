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

print("\n=== VIDEO COMPRESS ===\n")
print("Compression level:")
print("1. High quality  (light compression)")
print("2. Balanced      (medium compression)")
print("3. Max compact   (smallest files)")
level_input = input("\nChoose level (1-3, default 1): ").strip()
level = int(level_input) if level_input in ('1', '2', '3') else 1

compression_settings = {
    1: {'crf': 20, 'preset': 'slow'},
    2: {'crf': 28, 'preset': 'medium'},
    3: {'crf': 35, 'preset': 'fast'},
}
settings = compression_settings[level]
CRF = settings['crf']
PRESET = settings['preset']

print(f"\nLevel {level} — CRF {CRF} (lower = better quality), preset {PRESET}\n")


def compress_video(in_path: Path, out_path: Path, crf=CRF, preset=PRESET):
    try:
        cmd = [
            'ffmpeg', '-y', '-i', str(in_path),
            '-vcodec', 'libx264', '-crf', str(crf), '-preset', preset,
            '-acodec', 'aac', '-b:a', '128k',
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
        original_size = in_path.stat().st_size
        compressed_size = out_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100
        print(f"✓ {in_path.name} -> {out_path.name} (reduction: {reduction:.1f}%)")
        return True
    except Exception as e:
        print(f"✗ Error compressing {in_path.name}: {e}")
        return False


processed = 0
found = 0

for file_path in SRC_DIR.iterdir():
    if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
        found += 1
        success = compress_video(file_path, OUT_DIR / file_path.name)
        if success:
            processed += 1

if found == 0:
    print("⚠  No videos found in 'src/'")
    print("   Supported formats: MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V\n")
else:
    print(f"\n=== Done! {processed}/{found} videos compressed ===\n")

input("Press ENTER to exit...")

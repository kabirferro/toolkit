import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("\n⚠  MISSING DEPENDENCY\n")
    print("Pillow is not installed.\n")
    print("Install with:")
    print("  py -m pip install Pillow\n")
    input("Press ENTER to exit...")
    sys.exit(1)

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
OUT_DIR.mkdir(exist_ok=True)

QUALITY = 90
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}

print("\n=== REMOVE METADATA ===\n")
print("Strips EXIF data (GPS, camera info, timestamps) from images.\n")


def remove_metadata(in_path: Path, out_path: Path):
    try:
        with Image.open(in_path) as img:
            # Create a new image without metadata, preserving all pixel data
            clean = Image.new(img.mode, img.size)
            clean.paste(img, (0, 0))
            ext = in_path.suffix.lower()
            if ext in ('.jpg', '.jpeg'):
                clean.save(out_path, "JPEG", quality=QUALITY, optimize=True)
            elif ext == '.png':
                clean.save(out_path, "PNG", optimize=True)
            elif ext == '.webp':
                clean.save(out_path, "WEBP", quality=QUALITY)
            else:
                clean.save(out_path)
            original_size = in_path.stat().st_size
            new_size = out_path.stat().st_size
            reduction = ((original_size - new_size) / original_size) * 100
            print(f"✓ {in_path.name} -> {out_path.name} (size reduction: {reduction:.1f}%)")
            return True
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")
        return False


processed = 0
total = 0
for file_path in SRC_DIR.iterdir():
    if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
        total += 1
        if remove_metadata(file_path, OUT_DIR / file_path.name):
            processed += 1

print(f"\n=== Done! {processed}/{total} images processed ===\n")


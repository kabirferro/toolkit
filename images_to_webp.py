import os
import sys
from pathlib import Path

try:
    from PIL import Image, UnidentifiedImageError
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

QUALITY = 80
LOSSLESS = False

print("\n=== IMAGES TO WEBP ===\n")


def convert_to_webp(in_path: Path, out_path: Path, quality=QUALITY, lossless=LOSSLESS):
    try:
        with Image.open(in_path) as im:
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
            save_kwargs = {"format": "WEBP", "quality": quality}
            if lossless:
                save_kwargs["lossless"] = True
            im.save(out_path, **save_kwargs)
        print(f"✓ {in_path.name} -> {out_path.name}")
    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")


processed = 0
for file_path in SRC_DIR.iterdir():
    if file_path.is_file():
        convert_to_webp(file_path, OUT_DIR / (file_path.stem + ".webp"))
        processed += 1

print(f"\n=== Done! {processed} files processed ===\n")

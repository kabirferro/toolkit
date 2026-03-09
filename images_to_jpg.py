import os
import sys
from pathlib import Path

# Check dependencies
missing_deps = []
try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    missing_deps.append("Pillow")

try:
    from pillow_heif import register_heif_opener
except ImportError:
    missing_deps.append("pillow-heif")

if missing_deps:
    print("\n⚠  MISSING DEPENDENCIES\n")
    print("The following libraries are not installed:")
    for dep in missing_deps:
        print(f"  - {dep}")
    print("\nInstall with:")
    print("  py -m pip install Pillow pillow-heif\n")
    input("Press ENTER to exit...")
    sys.exit(1)

register_heif_opener()

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
OUT_DIR.mkdir(exist_ok=True)

QUALITY = 85

print("\n=== IMAGES TO JPG ===\n")


def convert_to_jpg(in_path: Path, out_path: Path, quality=QUALITY):
    try:
        with Image.open(in_path) as im:
            # Flatten transparency to white background for JPEG
            if im.mode in ("RGBA", "LA"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[-1])
                im = background
            elif im.mode != "RGB":
                im = im.convert("RGB")
            im.save(out_path, format="JPEG", quality=quality)
        print(f"✓ {in_path.name} -> {out_path.name}")
    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")


processed = 0
for file_path in SRC_DIR.iterdir():
    if file_path.is_file():
        convert_to_jpg(file_path, OUT_DIR / (file_path.stem + ".jpg"))
        processed += 1

print(f"\n=== Done! {processed} files processed ===\n")

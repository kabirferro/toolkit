from _core import run, require_pip, iter_src, no_files_warning, done, OUT_DIR

require_pip(PIL="Pillow")

from PIL import Image

QUALITY = 90
SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}


def remove_metadata(in_path, out_path):
    try:
        with Image.open(in_path) as img:
            # New image without metadata, preserving all pixel data
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


@run("REMOVE METADATA")
def main():
    print("Strips EXIF data (GPS, camera info, timestamps) from images.\n")
    files = iter_src(SUPPORTED)
    if not files:
        no_files_warning("images", SUPPORTED)
        return
    processed = sum(remove_metadata(f, OUT_DIR / f.name) for f in files)
    done(processed, len(files), "images")


main()

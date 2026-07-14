from _core import run, require_pip, iter_src, no_files_warning, done, OUT_DIR

require_pip(PIL="Pillow")

from PIL import Image, UnidentifiedImageError

QUALITY = 80
LOSSLESS = False
SUPPORTED = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}


def convert_to_webp(in_path, out_path):
    try:
        with Image.open(in_path) as im:
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
            save_kwargs = {"format": "WEBP", "quality": QUALITY}
            if LOSSLESS:
                save_kwargs["lossless"] = True
            im.save(out_path, **save_kwargs)
        print(f"✓ {in_path.name} -> {out_path.name}")
        return True
    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")
    return False


@run("IMAGES TO WEBP")
def main():
    files = iter_src(SUPPORTED)
    if not files:
        no_files_warning("images", SUPPORTED)
        return
    processed = sum(convert_to_webp(f, OUT_DIR / (f.stem + ".webp")) for f in files)
    done(processed, len(files), "images")


main()

from _core import run, require_pip, iter_src, no_files_warning, done, ask_choice, ask_int, ask_float, OUT_DIR

require_pip(PIL="Pillow")

from PIL import Image, UnidentifiedImageError

QUALITY = 90
SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}

ANCHOR_NAMES = {
    7: "top-left", 8: "top-center", 9: "top-right",
    4: "middle-left", 5: "center", 6: "middle-right",
    1: "bottom-left", 2: "bottom-center", 3: "bottom-right",
}


def prepare_image(im, ext):
    """Convert colour mode so the image can be saved back to its own format."""
    has_transparency = im.mode in ("RGBA", "LA", "P") and ("transparency" in im.info or im.mode in ("RGBA", "LA"))
    if ext in ('.jpg', '.jpeg') and im.mode in ("RGBA", "LA"):
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[-1])
        return background
    if ext in ('.jpg', '.jpeg') and im.mode != "RGB":
        return im.convert("RGB")
    if im.mode == "P":
        return im.convert("RGBA" if has_transparency else "RGB")
    return im


def save_image(im, out_path, ext):
    if ext in ('.jpg', '.jpeg'):
        im.save(out_path, format="JPEG", quality=QUALITY, optimize=True)
    elif ext == '.png':
        im.save(out_path, format="PNG", optimize=True)
    elif ext == '.webp':
        im.save(out_path, format="WEBP", quality=QUALITY, method=6)
    else:
        im.save(out_path, quality=QUALITY, optimize=True)


def resize_cover(in_path, out_path, target_w, target_h, anchor_pos):
    with Image.open(in_path) as im:
        ext = in_path.suffix.lower()
        im = prepare_image(im, ext)
        original_size = (im.width, im.height)

        # Scale so the image fully covers the target area
        img_ratio = im.width / im.height
        target_ratio = target_w / target_h
        if img_ratio > target_ratio:
            new_height = target_h
            new_width = int(new_height * img_ratio)
        else:
            new_width = target_w
            new_height = int(new_width / img_ratio)
        im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Crop anchor: 1,4,7 = left | 3,6,9 = right | others = center
        if anchor_pos in (1, 4, 7):
            left = 0
        elif anchor_pos in (3, 6, 9):
            left = new_width - target_w
        else:
            left = (new_width - target_w) // 2
        # 7,8,9 = top | 1,2,3 = bottom | others = center
        if anchor_pos in (7, 8, 9):
            top = 0
        elif anchor_pos in (1, 2, 3):
            top = new_height - target_h
        else:
            top = (new_height - target_h) // 2

        im = im.crop((left, top, left + target_w, top + target_h))
        save_image(im, out_path, ext)
    print(f"✓ {in_path.name} -> {out_path.name} ({original_size[0]}x{original_size[1]} → {target_w}x{target_h})")


def resize_by_percentage(in_path, out_path, percent):
    with Image.open(in_path) as im:
        ext = in_path.suffix.lower()
        im = prepare_image(im, ext)
        original_size = (im.width, im.height)
        new_width = int(im.width * percent / 100)
        new_height = int(im.height * percent / 100)
        im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
        save_image(im, out_path, ext)
    print(f"✓ {in_path.name} -> {out_path.name} ({original_size[0]}x{original_size[1]} → {new_width}x{new_height})")


def resize_fixed_side(in_path, out_path, fixed_w=None, fixed_h=None):
    with Image.open(in_path) as im:
        ext = in_path.suffix.lower()
        im = prepare_image(im, ext)
        original_size = (im.width, im.height)
        if fixed_w is not None:
            new_width = fixed_w
            new_height = int(im.height * (fixed_w / im.width))
        else:
            new_height = fixed_h
            new_width = int(im.width * (fixed_h / im.height))
        im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
        save_image(im, out_path, ext)
    print(f"✓ {in_path.name} -> {out_path.name} ({original_size[0]}x{original_size[1]} → {new_width}x{new_height})")


@run("IMAGE RESIZE")
def main():
    mode = ask_choice("Choose resize mode", [
        "Cover      (resize + crop with anchor point, like CSS cover)",
        "Percentage (resize proportionally by percentage)",
        "Fixed side (fix one dimension, scale the other keeping ratio)",
    ], default=1)

    params = {}
    if mode == 1:
        print("\n--- COVER ---")
        params['w'] = ask_int("Target width (px)", min_value=1)
        params['h'] = ask_int("Target height (px)", min_value=1)
        print("\nAnchor point (like a numpad):")
        print("7 8 9  (top-left, top-center, top-right)")
        print("4 5 6  (middle-left, center, middle-right)")
        print("1 2 3  (bottom-left, bottom-center, bottom-right)")
        params['anchor'] = ask_int("\nEnter number", default=5, min_value=1, max_value=9)
        print(f"\nCover {params['w']}x{params['h']} — anchor: {ANCHOR_NAMES[params['anchor']]}\n")
    elif mode == 2:
        print("\n--- PERCENTAGE ---")
        params['percent'] = ask_float("Percentage (e.g. 50 = half size, 200 = double)", min_value=0)
        print(f"\nProcessing at {params['percent']}%...\n")
    else:
        print("\n--- FIXED SIDE ---")
        dim = ask_choice("Which dimension to fix?", ["Width", "Height"], default=1)
        if dim == 1:
            params['fixed_w'] = ask_int("Fixed width (px)", min_value=1)
        else:
            params['fixed_h'] = ask_int("Fixed height (px)", min_value=1)
        print()

    files = iter_src(SUPPORTED)
    if not files:
        no_files_warning("images", SUPPORTED)
        return

    processed = 0
    for f in files:
        if mode == 2:
            out_file = OUT_DIR / f"{f.stem}-{int(params['percent'])}{f.suffix}"
        else:
            out_file = OUT_DIR / f.name
        try:
            if mode == 1:
                resize_cover(f, out_file, params['w'], params['h'], params['anchor'])
            elif mode == 2:
                resize_by_percentage(f, out_file, params['percent'])
            else:
                resize_fixed_side(f, out_file, params.get('fixed_w'), params.get('fixed_h'))
            processed += 1
        except UnidentifiedImageError:
            print(f"✗ Not a valid image: {f.name}")
        except Exception as e:
            print(f"✗ Error processing {f.name}: {e}")

    done(processed, len(files), "images")


main()

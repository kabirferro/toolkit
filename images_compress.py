from _core import run, require_pip, iter_src, no_files_warning, done, ask_choice, OUT_DIR

require_pip(PIL="Pillow")

from PIL import Image, UnidentifiedImageError

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif'}

COMPRESSION_SETTINGS = {
    1: {'quality': 95, 'subsampling': 0},  # 4:4:4
    2: {'quality': 85, 'subsampling': 1},  # 4:2:2
    3: {'quality': 75, 'subsampling': 2},  # 4:2:0
}
SUBSAMPLING_LABELS = ['4:4:4 (max quality)', '4:2:2 (balanced)', '4:2:0 (max compression)']


def compress_image(in_path, out_path, quality, subsampling):
    try:
        with Image.open(in_path) as im:
            ext = in_path.suffix.lower()

            if ext in {'.jpg', '.jpeg'}:
                if im.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', im.size, (255, 255, 255))
                    if im.mode == 'P':
                        im = im.convert('RGBA')
                    background.paste(im, mask=im.split()[-1] if im.mode in ('RGBA', 'LA') else None)
                    im = background
                elif im.mode != 'RGB':
                    im = im.convert('RGB')
                im.save(out_path, format='JPEG', quality=quality, optimize=True, subsampling=subsampling)

            elif ext == '.png':
                if im.mode not in ('RGB', 'RGBA', 'P', 'L'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                compress_level = 9 if subsampling == 2 else (6 if subsampling == 1 else 3)
                im.save(out_path, format='PNG', optimize=True, compress_level=compress_level)

            elif ext == '.webp':
                if im.mode not in ('RGB', 'RGBA'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                method = 4 if subsampling == 2 else 6
                im.save(out_path, format='WEBP', quality=quality, optimize=True, method=method)

            elif ext in {'.bmp', '.tiff', '.tif', '.gif'}:
                format_name = 'TIFF' if ext in {'.tiff', '.tif'} else ext[1:].upper()
                if ext == '.gif':
                    im.save(out_path, format=format_name, save_all=True, optimize=True)
                else:
                    im.save(out_path, format=format_name, optimize=True)

        original_size = in_path.stat().st_size
        compressed_size = out_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100
        print(f"✓ {in_path.name} -> {out_path.name} (reduction: {reduction:.1f}%)")
        return True
    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error compressing {in_path.name}: {e}")
    return False


@run("IMAGE COMPRESS")
def main():
    level = ask_choice("Compression level", [
        "High quality  (light compression, preserves colours)",
        "Balanced      (medium compression, good trade-off)",
        "Max compact   (smallest files, possible quality loss)",
    ], default=1)
    settings = COMPRESSION_SETTINGS[level]
    quality, subsampling = settings['quality'], settings['subsampling']
    print(f"\nLevel {level} — JPEG quality {quality}/100, subsampling {SUBSAMPLING_LABELS[subsampling]}\n")

    files = iter_src(SUPPORTED)
    if not files:
        no_files_warning("images", SUPPORTED)
        return
    processed = sum(compress_image(f, OUT_DIR / f.name, quality, subsampling) for f in files)
    done(processed, len(files), "images")


main()

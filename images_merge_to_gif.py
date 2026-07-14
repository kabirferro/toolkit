from _core import run, require_pip, iter_src, no_files_warning, ask_text, ask_int, ask_yes_no, OUT_DIR

require_pip(PIL="Pillow")

from PIL import Image

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}


@run("IMAGES TO GIF")
def main():
    output_name = ask_text("Output filename (without extension)", default="animated")
    fps = ask_int("FPS (frames per second)", default=10, min_value=1, max_value=60)
    loop = 0 if ask_yes_no("Infinite loop?", default=True) else 1  # 0 = infinite
    duration = int(1000 / fps)

    print(f"\nCreating GIF at {fps} FPS (frame duration: {duration}ms)")
    print(f"Loop: {'infinite' if loop == 0 else 'once'}\n")

    image_files = iter_src(SUPPORTED)
    if not image_files:
        no_files_warning("images", SUPPORTED)
        return

    print(f"Found {len(image_files)} images:\n")
    for idx, f in enumerate(image_files, 1):
        print(f"  {idx}. {f.name}")
    print()

    frames = []
    for img_file in image_files:
        img = Image.open(img_file)
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode not in ('RGB', 'P'):
            img = img.convert('RGB')
        frames.append(img)
        print(f"✓ Loaded: {img_file.name}")

    output_path = OUT_DIR / f"{output_name}.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        optimize=False,
    )
    file_size = output_path.stat().st_size / 1024
    print(f"\n=== GIF created successfully! ===")
    print(f"File:   {output_path}")
    print(f"Size:   {file_size:.1f} KB")
    print(f"Frames: {len(frames)}")
    print(f"FPS:    {fps}")


main()

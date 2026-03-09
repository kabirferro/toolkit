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

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}

print("\n=== IMAGES TO GIF ===\n")

output_name = input("Output filename (without extension, default: animated): ").strip() or "animated"

fps_input = input("FPS (frames per second, default 10): ").strip()
fps = int(fps_input) if fps_input.isdigit() else 10

loop_input = input("Infinite loop? (y/n, default y): ").strip().lower()
loop = 0 if loop_input != 'n' else 1  # 0 = infinite, 1 = once

duration = int(1000 / fps)

print(f"\nCreating GIF at {fps} FPS (frame duration: {duration}ms)")
print(f"Loop: {'infinite' if loop == 0 else 'once'}\n")

image_files = sorted([
    f for f in SRC_DIR.iterdir()
    if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
])

if not image_files:
    print("⚠  No images found in src/")
    sys.exit(0)

print(f"Found {len(image_files)} images:\n")
for idx, f in enumerate(image_files, 1):
    print(f"  {idx}. {f.name}")

frames = []
try:
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
    print(f"FPS:    {fps}\n")

except Exception as e:
    print(f"\n✗ Error creating GIF: {e}\n")


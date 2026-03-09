import os
import sys
from pathlib import Path
import io

missing_deps = []
try:
    from PIL import Image, ImageOps
except ImportError:
    missing_deps.append("Pillow")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError:
    missing_deps.append("reportlab")

if missing_deps:
    print("\n⚠  MISSING DEPENDENCIES\n")
    print("The following libraries are not installed:")
    for dep in missing_deps:
        print(f"  - {dep}")
    print("\nInstall with:")
    print("  py -m pip install Pillow reportlab\n")
    input("Press ENTER to exit...")
    sys.exit(1)

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
OUT_DIR.mkdir(exist_ok=True)

print("\n=== IMAGES TO PDF ===\n")

print("Conversion mode:")
print("1. Single page  (one image per page)")
print("2. Thumbnails   (multiple thumbnails per page)")
mode_input = input("\nChoose mode (1-2, default 1): ").strip()
mode = mode_input if mode_input in ('1', '2') else '1'

output_name = "images"

if mode == '1':
    # SINGLE PAGE MODE

    print("\nImage layout:")
    print("1. Fit  (scale to fit the page, keep proportions)")
    print("2. Fill (fill the page, may crop)")
    print("3. Original (keep original dimensions)")
    layout_input = input("\nChoose layout (1-3, default 1): ").strip()
    layout = layout_input if layout_input in ('1', '2', '3') else '1'

    print("\nPage size:")
    print("1. A4 (210x297mm)")
    print("2. Letter (216x279mm)")
    print("3. Custom")
    size_input = input("\nChoose size (1-3, default 1): ").strip()

    if size_input == '2':
        page_size = (612, 792)  # Letter in points
    elif size_input == '3':
        width = int(input("Width in pixels: "))
        height = int(input("Height in pixels: "))
        page_size = (width, height)
    else:
        page_size = (595, 842)  # A4 in points

    supported_formats = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}
    image_files = sorted([
        f for f in SRC_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in supported_formats
    ])

    if not image_files:
        print("\n⚠  No images found in src/\n")
        sys.exit(0)

    print(f"\nFound {len(image_files)} images (alphabetical order):\n")
    for idx, img_file in enumerate(image_files, 1):
        print(f"  {idx}. {img_file.name}")
    print()

    images = []
    try:
        for img_file in image_files:
            img = Image.open(img_file)

            # Flatten transparency to white for PDF
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Applica layout
            if layout == '1':  # Fit
                img.thumbnail(page_size, Image.Resampling.LANCZOS)
            elif layout == '2':  # Fill
                img_ratio = img.width / img.height
                page_ratio = page_size[0] / page_size[1]
                if img_ratio > page_ratio:
                    new_width = page_size[0]
                    new_height = int(new_width / img_ratio)
                else:
                    new_height = page_size[1]
                    new_width = int(new_height * img_ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - page_size[0]) // 2
                top = (new_height - page_size[1]) // 2
                img = img.crop((left, top, left + page_size[0], top + page_size[1]))
            # Layout 3 (original) - no change
            
            images.append(img)
            print(f"✓ Loaded: {img_file.name}")

        output_path = OUT_DIR / f"{output_name}.pdf"
        
        if len(images) == 1:
            images[0].save(output_path, "PDF", resolution=100.0)
        else:
            images[0].save(
                output_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=images[1:]
            )
        
        file_size = output_path.stat().st_size / 1024
        print(f"\n=== PDF created successfully! ===")
        print(f"File:  {output_path}")
        print(f"Size:  {file_size:.1f} KB")
        print(f"Pages: {len(images)}\n")

    except Exception as e:
        print(f"\n✗ Error creating PDF: {e}\n")

else:
    # THUMBNAILS MODE
    
    MARGIN = 20  # margin in points
    PAGE_WIDTH, PAGE_HEIGHT = A4

    def calculate_thumb_dimensions(images_per_row):
        """Calculate thumbnail dimensions based on number per row."""
        available_width = PAGE_WIDTH - (2 * MARGIN)
        thumb_width = (available_width - (images_per_row - 1) * 5) / images_per_row
        thumb_height = thumb_width
        return thumb_width, thumb_height

    def create_thumbnail(image_path, max_size):
        """Create a thumbnail respecting EXIF orientation."""
        try:
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            return ImageReader(img_buffer), img.size
        except Exception as e:
            print(f"  ⚠ Error processing {image_path.name}: {e}")
            return None, None

    user_input = input("\nHow many images per row? (default: 5): ").strip()
    
    if user_input == "":
        images_per_row = 5
    else:
        try:
            images_per_row = int(user_input)
            if images_per_row < 1 or images_per_row > 10:
                print("⚠ Invalid value, using default (5)")
                images_per_row = 5
        except ValueError:
            print("⚠ Invalid value, using default (5)")
            images_per_row = 5

    supported_formats = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif', '.heic'}
    image_files = sorted([
        f for f in SRC_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in supported_formats
    ])

    if not image_files:
        print("\n⚠  No images found in src/\n")
        sys.exit(0)

    print(f"\nFound {len(image_files)} images (alphabetical order)")
    print(f"Images per row: {images_per_row}\n")

    thumb_width, thumb_height = calculate_thumb_dimensions(images_per_row)
    output_path = OUT_DIR / f"{output_name}.pdf"
    c = canvas.Canvas(str(output_path), pagesize=A4)
    
    x_pos = MARGIN
    y_pos = PAGE_HEIGHT - MARGIN - thumb_height
    images_in_row = 0
    total_images = 0
    
    print("Processing images...")

    for img_file in image_files:
        print(f"  → {img_file.name}")
        
        thumb, size = create_thumbnail(img_file, int(thumb_width * 2))
        
        if thumb is None:
            continue
        
        aspect_ratio = size[0] / size[1]
        if aspect_ratio > 1:  # landscape
            draw_width = thumb_width
            draw_height = thumb_width / aspect_ratio
        else:  # portrait
            draw_height = thumb_height
            draw_width = thumb_height * aspect_ratio
        
        # Centre the image in its cell
        x_offset = (thumb_width - draw_width) / 2
        y_offset = (thumb_height - draw_height) / 2
        
        c.drawImage(thumb, 
                   x_pos + x_offset, 
                   y_pos + y_offset, 
                   width=draw_width, 
                   height=draw_height,
                   preserveAspectRatio=True)
        
        c.setFont("Helvetica", 6)
        text_width = c.stringWidth(img_file.name, "Helvetica", 6)
        if text_width > thumb_width:
            # Truncate filename if too long
            display_name = img_file.name[:20] + "..."
        else:
            display_name = img_file.name
        c.drawString(x_pos, y_pos - 10, display_name)
        
        total_images += 1
        images_in_row += 1
        
        if images_in_row >= images_per_row:
            # New row
            x_pos = MARGIN
            y_pos -= thumb_height + 15
            images_in_row = 0
            # New page if out of space
            if y_pos < MARGIN:
                c.showPage()
                y_pos = PAGE_HEIGHT - MARGIN - thumb_height
        else:
            # Next column
            x_pos += thumb_width + 5

    c.save()

    file_size = output_path.stat().st_size / 1024
    print(f"\n=== PDF created successfully! ===")
    print(f"File:   {output_path}")
    print(f"Size:   {file_size:.1f} KB")
    print(f"Images: {total_images}\n")

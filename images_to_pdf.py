import io

from _core import run, require_pip, iter_src, no_files_warning, ask_choice, ask_int, OUT_DIR

require_pip(PIL="Pillow", reportlab="reportlab")

from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

OUTPUT_NAME = "images"
DPI = 100                          # pixel density used when saving the PDF
MARGIN_PX = round(DPI / 2.54)      # 1 cm margin on every side (Fill layout)


def single_page_mode():
    layout = ask_choice("\nImage layout", [
        "Fit  (scale to fit the page, keep proportions)",
        "Fill (white page, image centered with 1 cm margin)",
        "Original (keep original dimensions)",
    ], default=1)

    print()
    size_choice = ask_choice("Page size", [
        "A4 (210x297mm)",
        "Letter (216x279mm)",
        "Custom",
    ], default=1)
    if size_choice == 2:
        page_size = (round(8.5 * DPI), round(11 * DPI))  # Letter at DPI
    elif size_choice == 3:
        page_size = (ask_int("Width in pixels", min_value=1), ask_int("Height in pixels", min_value=1))
    else:
        page_size = (round(21.0 / 2.54 * DPI), round(29.7 / 2.54 * DPI))  # A4 at DPI

    supported = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}
    image_files = iter_src(supported)
    if not image_files:
        print()
        no_files_warning("images", supported)
        return

    print(f"\nFound {len(image_files)} images (alphabetical order):\n")
    for idx, img_file in enumerate(image_files, 1):
        print(f"  {idx}. {img_file.name}")
    print()

    images = []
    for img_file in image_files:
        img = Image.open(img_file)

        # Flatten transparency to white for PDF
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        if layout == 1:  # Fit
            img.thumbnail(page_size, Image.Resampling.LANCZOS)
        elif layout == 2:  # Fill: white page, image fitted inside 1 cm margins, centered
            box = (max(1, page_size[0] - 2 * MARGIN_PX), max(1, page_size[1] - 2 * MARGIN_PX))
            img.thumbnail(box, Image.Resampling.LANCZOS)
            page = Image.new('RGB', page_size, (255, 255, 255))
            page.paste(img, ((page_size[0] - img.width) // 2, (page_size[1] - img.height) // 2))
            img = page
        # layout 3 (original): no change

        images.append(img)
        print(f"✓ Loaded: {img_file.name}")

    output_path = OUT_DIR / f"{OUTPUT_NAME}.pdf"
    if len(images) == 1:
        images[0].save(output_path, "PDF", resolution=float(DPI))
    else:
        images[0].save(output_path, "PDF", resolution=float(DPI), save_all=True, append_images=images[1:])

    file_size = output_path.stat().st_size / 1024
    print(f"\n=== PDF created successfully! ===")
    print(f"File:  {output_path}")
    print(f"Size:  {file_size:.1f} KB")
    print(f"Pages: {len(images)}")


def thumbnails_mode():
    MARGIN = 20  # points
    PAGE_WIDTH, PAGE_HEIGHT = A4

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

    print()
    images_per_row = ask_int("How many images per row?", default=5, min_value=1, max_value=10)

    supported = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif', '.heic'}
    image_files = iter_src(supported)
    if not image_files:
        print()
        no_files_warning("images", supported)
        return

    print(f"\nFound {len(image_files)} images (alphabetical order)")
    print(f"Images per row: {images_per_row}\n")

    available_width = PAGE_WIDTH - (2 * MARGIN)
    thumb_width = (available_width - (images_per_row - 1) * 5) / images_per_row
    thumb_height = thumb_width

    output_path = OUT_DIR / f"{OUTPUT_NAME}.pdf"
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

        x_offset = (thumb_width - draw_width) / 2
        y_offset = (thumb_height - draw_height) / 2
        c.drawImage(thumb, x_pos + x_offset, y_pos + y_offset,
                    width=draw_width, height=draw_height, preserveAspectRatio=True)

        c.setFont("Helvetica", 6)
        text_width = c.stringWidth(img_file.name, "Helvetica", 6)
        display_name = img_file.name[:20] + "..." if text_width > thumb_width else img_file.name
        c.drawString(x_pos, y_pos - 10, display_name)

        total_images += 1
        images_in_row += 1

        if images_in_row >= images_per_row:
            x_pos = MARGIN
            y_pos -= thumb_height + 15
            images_in_row = 0
            if y_pos < MARGIN:
                c.showPage()
                y_pos = PAGE_HEIGHT - MARGIN - thumb_height
        else:
            x_pos += thumb_width + 5

    c.save()

    file_size = output_path.stat().st_size / 1024
    print(f"\n=== PDF created successfully! ===")
    print(f"File:   {output_path}")
    print(f"Size:   {file_size:.1f} KB")
    print(f"Images: {total_images}")


@run("IMAGES TO PDF")
def main():
    mode = ask_choice("Conversion mode", [
        "Single page  (one image per page)",
        "Thumbnails   (multiple thumbnails per page)",
    ], default=1)
    if mode == 1:
        single_page_mode()
    else:
        thumbnails_mode()


main()

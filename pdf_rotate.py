from _core import run, require_pip, iter_src, no_files_warning, done, ask_choice, ask_text, OUT_DIR

require_pip(pypdf="pypdf")

from pypdf import PdfReader, PdfWriter

ROTATION_MAP = {1: 90, 2: 180, 3: 270}


def parse_page_numbers(pages_str):
    """Parse a page range string like '1,3,5-7' into a sorted list of page numbers."""
    pages = set()
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.update(range(int(start), int(end) + 1))
        elif part:
            pages.add(int(part))
    return sorted(pages)


def rotate_pdf(input_path, output_path, angle, pages_to_rotate=None):
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        rotated_count = 0
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            if pages_to_rotate is None or (page_num + 1) in pages_to_rotate:
                page.rotate(angle)
                rotated_count += 1
            writer.add_page(page)
        with open(output_path, 'wb') as f:
            writer.write(f)
        print(f"✓ {input_path.name}")
        print(f"  Pages rotated: {rotated_count}/{total_pages}\n")
        return True
    except Exception as e:
        print(f"✗ Error processing {input_path.name}: {e}\n")
        return False


@run("PDF ROTATE")
def main():
    rotation = ROTATION_MAP[ask_choice("Rotation angle", [
        "90°  (clockwise)",
        "180° (upside-down)",
        "270° (counter-clockwise)",
    ], default=1)]
    print(f"\nRotation: {rotation}°\n")

    pages_mode = ask_choice("Which pages should be rotated?", [
        "All pages",
        "Specific pages only",
    ], default=1)

    specific_pages = None
    if pages_mode == 2:
        while specific_pages is None:
            try:
                specific_pages = parse_page_numbers(
                    ask_text("Enter page numbers separated by commas (e.g. 1,3,5-7)"))
            except ValueError:
                print("⚠  Invalid page list, try again.")
    print()

    files = iter_src({'.pdf'})
    if not files:
        no_files_warning("PDF files", {'.pdf'})
        return
    processed = sum(rotate_pdf(f, OUT_DIR / f.name, rotation, specific_pages) for f in files)
    done(processed, len(files), "PDFs")


main()

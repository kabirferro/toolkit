import os
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("\n⚠  MISSING DEPENDENCY\n")
    print("pypdf is not installed.\n")
    print("Install with:")
    print("  py -m pip install pypdf\n")
    input("Press ENTER to exit...")
    sys.exit(1)

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
OUT_DIR.mkdir(exist_ok=True)

print("\n=== PDF ROTATE ===\n")

print("Rotation angle:")
print("1. 90°  (clockwise)")
print("2. 180° (upside-down)")
print("3. 270° (counter-clockwise)")
rotation_input = input("\nChoose rotation (1-3): ").strip()

rotation_map = {'1': 90, '2': 180, '3': 270}
if rotation_input not in rotation_map:
    print("⚠  Invalid choice, defaulting to 90°")
    rotation = 90
else:
    rotation = rotation_map[rotation_input]

print(f"\nRotation: {rotation}°")

print("\nWhich pages should be rotated?")
print("1. All pages")
print("2. Specific pages only")
pages_input = input("\nChoose (1-2, default 1): ").strip()


def parse_page_numbers(pages_str):
    """Parse a page range string like '1,3,5-7' into a sorted list of page numbers."""
    pages = set()
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(part))
    return sorted(pages)


specific_pages = None
if pages_input == '2':
    pages_str = input("Enter page numbers separated by commas (e.g. 1,3,5-7): ").strip()
    specific_pages = parse_page_numbers(pages_str)


def rotate_pdf(input_path: Path, output_path: Path, angle: int, pages_to_rotate=None):
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


processed = 0
total = 0
for file_path in sorted(SRC_DIR.glob("*.pdf")):
    total += 1
    if rotate_pdf(file_path, OUT_DIR / (file_path.stem + ".pdf"), rotation, specific_pages):
        processed += 1

if total == 0:
    print("⚠  No PDF files found in src/\n")
else:
    print(f"\n=== Done! {processed}/{total} PDFs rotated ===\n")


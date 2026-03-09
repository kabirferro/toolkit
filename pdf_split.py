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

print("\n=== PDF SPLIT ===\n")


def split_pdf(input_path: Path, output_dir: Path):
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        padding = len(str(total_pages))
        base_name = input_path.stem
        print(f"  {input_path.name} — {total_pages} pages")
        for page_num in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            page_number = str(page_num + 1).zfill(padding)
            output_filename = f"{base_name}-{page_number}.pdf"
            with open(output_dir / output_filename, 'wb') as f:
                writer.write(f)
            print(f"    ✓ Page {page_num + 1}/{total_pages} → {output_filename}")
        return total_pages
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 0


total_pdfs = 0
total_pages = 0
for file_path in sorted(SRC_DIR.glob("*.pdf")):
    pages = split_pdf(file_path, OUT_DIR)
    if pages > 0:
        total_pdfs += 1
        total_pages += pages

print(f"\n=== Done! {total_pdfs} PDFs split into {total_pages} pages ===\n")


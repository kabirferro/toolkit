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

print("\n=== PDF MERGE ===\n")

output_path = OUT_DIR / "pdf-merged.pdf"

pdf_files = sorted(SRC_DIR.glob("*.pdf"))
if not pdf_files:
    print("⚠  No PDF files found in src/\n")
    sys.exit(0)

print(f"Found {len(pdf_files)} PDFs to merge:\n")
for idx, f in enumerate(pdf_files, 1):
    print(f"  {idx}. {f.name}")
print(f"\nOutput: {output_path.name}\n")

merger = PdfWriter()
total_pages = 0

for pdf_file in pdf_files:
    try:
        merger.append(str(pdf_file))
        pages = len(PdfReader(pdf_file).pages)
        total_pages += pages
        print(f"✓ {pdf_file.name} ({pages} pages)")
    except Exception as e:
        print(f"✗ Error with {pdf_file.name}: {e}")

try:
    with open(output_path, 'wb') as f:
        merger.write(f)
    print(f"\n=== Done! {len(pdf_files)} PDFs merged into {total_pages} total pages ===")
    print(f"Output: {output_path}\n")
except Exception as e:
    print(f"\n✗ Error saving output: {e}\n")


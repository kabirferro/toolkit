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

print("\n=== PDF COMPRESS ===\n")

print("Compression level:")
print("1. Low    (high quality, minimal compression)")
print("2. Medium (balanced)")
print("3. High   (smaller file, lower quality)")
level_input = input("\nChoose level (1-3, default 2): ").strip()
level = int(level_input) if level_input in ('1', '2', '3') else 2

compression_levels = {1: 0, 2: 6, 3: 9}
compress_level = compression_levels[level]
level_names = {1: 'minimal', 2: 'medium', 3: 'maximum'}
print(f"\nLevel {level}: {level_names[level]} compression\n")


def compress_pdf(input_path: Path, output_path: Path, level: int):
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            if level > 0:
                page.compress_content_streams(level=level)
            writer.add_page(page)
        with open(output_path, 'wb') as f:
            writer.write(f)
        original_kb = input_path.stat().st_size / 1024
        new_kb = output_path.stat().st_size / 1024
        reduction = ((original_kb - new_kb) / original_kb) * 100
        print(f"✓ {input_path.name}")
        print(f"  {original_kb:.1f} KB → {new_kb:.1f} KB  ({reduction:.1f}% reduction)\n")
        return True
    except Exception as e:
        print(f"✗ Error processing {input_path.name}: {e}\n")
        return False


processed = 0
total = 0
for file_path in sorted(SRC_DIR.glob("*.pdf")):
    total += 1
    if compress_pdf(file_path, OUT_DIR / f"{file_path.stem}.pdf", compress_level):
        processed += 1

if total == 0:
    print("⚠  No PDF files found in src/\n")
else:
    print(f"=== Done! {processed}/{total} PDFs compressed ===\n")


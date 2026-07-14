from _core import run, require_pip, iter_src, no_files_warning, done, ask_choice, OUT_DIR

require_pip(pypdf="pypdf")

from pypdf import PdfReader, PdfWriter

COMPRESSION_LEVELS = {1: 0, 2: 6, 3: 9}
LEVEL_NAMES = {1: 'minimal', 2: 'medium', 3: 'maximum'}


def compress_pdf(input_path, output_path, level):
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


@run("PDF COMPRESS")
def main():
    level = ask_choice("Compression level", [
        "Low    (high quality, minimal compression)",
        "Medium (balanced)",
        "High   (smaller file, lower quality)",
    ], default=2)
    print(f"\nLevel {level}: {LEVEL_NAMES[level]} compression\n")

    files = iter_src({'.pdf'})
    if not files:
        no_files_warning("PDF files", {'.pdf'})
        return
    processed = sum(compress_pdf(f, OUT_DIR / f.name, COMPRESSION_LEVELS[level]) for f in files)
    done(processed, len(files), "PDFs")


main()

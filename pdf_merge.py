from _core import run, require_pip, iter_src, no_files_warning, ask_text, OUT_DIR

require_pip(pypdf="pypdf")

from pypdf import PdfReader, PdfWriter


@run("PDF MERGE")
def main():
    pdf_files = iter_src({'.pdf'})
    if not pdf_files:
        no_files_warning("PDF files", {'.pdf'})
        return

    print(f"Found {len(pdf_files)} PDFs to merge (alphabetical order):\n")
    for idx, f in enumerate(pdf_files, 1):
        print(f"  {idx}. {f.name}")
    print()

    output_name = ask_text("Output filename (without extension)", default="pdf-merged")
    output_path = OUT_DIR / f"{output_name}.pdf"
    print()

    merger = PdfWriter()
    total_pages = 0
    merged = 0
    for pdf_file in pdf_files:
        try:
            merger.append(str(pdf_file))
            pages = len(PdfReader(pdf_file).pages)
            total_pages += pages
            merged += 1
            print(f"✓ {pdf_file.name} ({pages} pages)")
        except Exception as e:
            print(f"✗ Error with {pdf_file.name}: {e}")

    with open(output_path, 'wb') as f:
        merger.write(f)
    print(f"\n=== Done! {merged}/{len(pdf_files)} PDFs merged into {total_pages} total pages ===")
    print(f"Output: {output_path}")


main()

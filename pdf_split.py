from _core import run, require_pip, iter_src, no_files_warning, OUT_DIR

require_pip(pypdf="pypdf")

from pypdf import PdfReader, PdfWriter


def split_pdf(input_path, output_dir):
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        padding = len(str(total_pages))
        print(f"  {input_path.name} — {total_pages} pages")
        for page_num in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            output_filename = f"{input_path.stem}-{str(page_num + 1).zfill(padding)}.pdf"
            with open(output_dir / output_filename, 'wb') as f:
                writer.write(f)
            print(f"    ✓ Page {page_num + 1}/{total_pages} → {output_filename}")
        return total_pages
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 0


@run("PDF SPLIT")
def main():
    files = iter_src({'.pdf'})
    if not files:
        no_files_warning("PDF files", {'.pdf'})
        return
    total_pdfs = 0
    total_pages = 0
    for f in files:
        pages = split_pdf(f, OUT_DIR)
        if pages > 0:
            total_pdfs += 1
            total_pages += pages
    print(f"\n=== Done! {total_pdfs}/{len(files)} PDFs split into {total_pages} pages ===")


main()

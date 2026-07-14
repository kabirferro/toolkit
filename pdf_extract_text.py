from _core import run, require_pip, iter_src, no_files_warning, done, ask_choice, OUT_DIR

require_pip(pypdf="pypdf")

from pypdf import PdfReader


def extract_text(in_path, out_path, page_markers):
    try:
        reader = PdfReader(in_path)
        total_pages = len(reader.pages)
        parts = []
        empty_pages = 0
        for page_num, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            if not text:
                empty_pages += 1
            if page_markers:
                parts.append(f"--- Page {page_num} ---\n{text}")
            else:
                parts.append(text)
        out_path.write_text("\n\n".join(parts).strip() + "\n", encoding="utf-8")
        note = f" ({empty_pages} pages with no extractable text — scanned?)" if empty_pages else ""
        print(f"✓ {in_path.name} -> {out_path.name} ({total_pages} pages){note}")
        return True
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")
        return False


@run("PDF EXTRACT TEXT")
def main():
    print("Extracts the text layer from PDFs (scanned PDFs without OCR yield no text).\n")
    page_markers = ask_choice("Output style", [
        "Plain text (pages joined together)",
        "With page markers (--- Page N ---)",
    ], default=1) == 2
    print()

    files = iter_src({'.pdf'})
    if not files:
        no_files_warning("PDF files", {'.pdf'})
        return
    processed = sum(extract_text(f, OUT_DIR / (f.stem + ".txt"), page_markers) for f in files)
    done(processed, len(files), "PDFs")


main()

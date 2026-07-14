from _core import run, require_pip, iter_src, no_files_warning, done, ask_choice, ask_int, OUT_DIR

require_pip(pypdfium2="pypdfium2")

import pypdfium2 as pdfium

JPG_QUALITY = 90


def pdf_to_images(in_path, fmt, dpi):
    try:
        pdf = pdfium.PdfDocument(in_path)
        total_pages = len(pdf)
        padding = len(str(total_pages))
        print(f"  {in_path.name} — {total_pages} pages")
        scale = dpi / 72  # PDF native resolution is 72 dpi
        for page_num in range(total_pages):
            page = pdf[page_num]
            bitmap = page.render(scale=scale)
            img = bitmap.to_pil()
            out_name = f"{in_path.stem}-{str(page_num + 1).zfill(padding)}.{fmt}"
            out_path = OUT_DIR / out_name
            if fmt == 'jpg':
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(out_path, "JPEG", quality=JPG_QUALITY, optimize=True)
            else:
                img.save(out_path, "PNG", optimize=True)
            print(f"    ✓ Page {page_num + 1}/{total_pages} → {out_name}")
        pdf.close()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


@run("PDF TO IMAGES")
def main():
    fmt = 'jpg' if ask_choice("Output format", [
        "JPG (smaller files, photos/scans)",
        "PNG (lossless, text/diagrams)",
    ], default=1) == 1 else 'png'
    print()
    dpi = ask_int("Resolution in DPI", default=150, min_value=36, max_value=600)
    print(f"\nFormat: {fmt.upper()}, {dpi} DPI\n")

    files = iter_src({'.pdf'})
    if not files:
        no_files_warning("PDF files", {'.pdf'})
        return
    processed = sum(pdf_to_images(f, fmt, dpi) for f in files)
    done(processed, len(files), "PDFs")


main()

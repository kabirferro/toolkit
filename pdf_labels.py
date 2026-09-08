from _core import run, require_pip, setup_dirs, ask_int, ask_float, ask_text, OUT_DIR

require_pip(reportlab="reportlab")

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import getAscentDescent
from reportlab.pdfgen import canvas

MARGIN = 1 * mm          # 1mm on every A4 edge
CELL_PAD = 1.5 * mm      # inner padding so text never touches the cell edge
FONT = "Helvetica-Bold"  # bold, as requested
MIN_FONT = 4             # lower bound: below this the text is unreadable


def fit_font_size(c, text, max_w, max_h, start_size):
    """Font size (points) for `text` on one line inside a max_w x max_h box.
    Keeps `start_size` if it fits; otherwise shrinks down to MIN_FONT."""
    size = start_size
    while size > MIN_FONT:
        width = c.stringWidth(text, FONT, size)
        ascent, descent = getAscentDescent(FONT, size)  # descent is negative
        height = ascent - descent
        if width <= max_w and height <= max_h:
            return size
        size -= 0.5
    return MIN_FONT


def draw_cell(c, text, cx, cy, max_w, max_h, start_size):
    """Draw `text` bold, centred on (cx, cy). Returns the size actually used."""
    size = fit_font_size(c, text, max_w, max_h, start_size)
    ascent, descent = getAscentDescent(FONT, size)
    baseline = cy - (ascent + descent) / 2  # centre the glyph box on cy
    c.setFont(FONT, size)
    c.drawCentredString(cx, baseline, text)
    return size


@run("PDF LABELS")
def main():
    setup_dirs()

    print("Divide the A4 sheet into a regular grid (1mm margin on every edge).\n")
    rows = ask_int("How many rows?", min_value=1)
    cols = ask_int("How many columns?", min_value=1)
    per_page = rows * cols

    print()
    font_size = ask_float("Font size in points (shrinks automatically if it does not fit)",
                          default=48, min_value=0)

    print()
    raw = ask_text("Labels (comma-separated, one per cell)")
    labels = [part.strip() for part in raw.split(",") if part.strip()]
    if not labels:
        print("\n⚠  No labels entered.")
        return

    print()
    output_name = ask_text("Output filename (without extension)", default="labels")
    output_path = OUT_DIR / f"{output_name}.pdf"

    page_w, page_h = A4
    usable_w = page_w - 2 * MARGIN
    usable_h = page_h - 2 * MARGIN
    cell_w = usable_w / cols
    cell_h = usable_h / rows
    box_w = cell_w - 2 * CELL_PAD
    box_h = cell_h - 2 * CELL_PAD

    pages = (len(labels) + per_page - 1) // per_page
    print(f"\nGrid: {rows} rows x {cols} cols ({per_page} cells/page)")
    print(f"Font: {font_size:g}pt (auto-shrinks per cell when needed)")
    print(f"Labels: {len(labels)}  ->  {pages} page(s)\n")

    c = canvas.Canvas(str(output_path), pagesize=A4)
    for i, text in enumerate(labels):
        slot = i % per_page
        if i > 0 and slot == 0:
            c.showPage()
        r, col = divmod(slot, cols)
        cx = MARGIN + col * cell_w + cell_w / 2
        cy = page_h - MARGIN - r * cell_h - cell_h / 2
        used = draw_cell(c, text, cx, cy, box_w, box_h, font_size)
        note = "" if used == font_size else f"  (shrunk to {used:g}pt)"
        print(f"✓ {text}{note}")
    c.save()

    file_size = output_path.stat().st_size / 1024
    print(f"\n=== PDF created successfully! ===")
    print(f"File:   {output_path}")
    print(f"Size:   {file_size:.1f} KB")
    print(f"Labels: {len(labels)}")
    print(f"Pages:  {pages}")


main()

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
LINE_SPACING = 1.15      # line height as a multiple of the font size
BREAK = "|"              # forces a line break inside a label


def wrap_text(c, text, max_w, size):
    """Split `text` into lines that fit `max_w` at `size`. Honours the explicit
    BREAK character first, then wraps long lines on spaces. A single word that
    is still too wide is kept as is (the font size will shrink instead)."""
    lines = []
    for chunk in text.split(BREAK):
        words = chunk.strip().split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if c.stringWidth(candidate, FONT, size) <= max_w:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit_text(c, text, max_w, max_h, start_size):
    """Return (size, lines) for `text` inside a max_w x max_h box, keeping
    `start_size` if it fits and shrinking down to MIN_FONT otherwise."""
    size = start_size
    while size > MIN_FONT:
        lines = wrap_text(c, text, max_w, size)
        widest = max(c.stringWidth(line, FONT, size) for line in lines)
        height = size * LINE_SPACING * len(lines)
        if widest <= max_w and height <= max_h:
            return size, lines
        size -= 0.5
    return MIN_FONT, wrap_text(c, text, max_w, MIN_FONT)


def draw_cell(c, text, cx, cy, max_w, max_h, start_size):
    """Draw `text` bold, centred on (cx, cy), over as many lines as needed.
    Returns (size used, number of lines)."""
    size, lines = fit_text(c, text, max_w, max_h, start_size)
    ascent, descent = getAscentDescent(FONT, size)
    leading = size * LINE_SPACING
    block_h = leading * len(lines)
    # top baseline: centre the whole block on cy, then drop to the first baseline
    baseline = cy + block_h / 2 - (leading + ascent + descent) / 2
    c.setFont(FONT, size)
    for line in lines:
        c.drawCentredString(cx, baseline, line)
        baseline -= leading
    return size, len(lines)


def read_labels():
    """Read labels interactively: one per line, blank line to finish. Commas
    still split a line into several labels (backwards compatible)."""
    print(f"Labels: one per line, use '{BREAK}' inside a label to force a line break.")
    print("Commas also separate labels. Empty line when you are done.")
    labels = []
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            break
        labels.extend(part.strip() for part in line.split(",") if part.strip())
    return labels


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
    labels = read_labels()
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
        used, n_lines = draw_cell(c, text, cx, cy, box_w, box_h, font_size)
        notes = []
        if used != font_size:
            notes.append(f"shrunk to {used:g}pt")
        if n_lines > 1:
            notes.append(f"{n_lines} lines")
        note = f"  ({', '.join(notes)})" if notes else ""
        print(f"✓ {text}{note}")
    c.save()

    file_size = output_path.stat().st_size / 1024
    print(f"\n=== PDF created successfully! ===")
    print(f"File:   {output_path}")
    print(f"Size:   {file_size:.1f} KB")
    print(f"Labels: {len(labels)}")
    print(f"Pages:  {pages}")


main()

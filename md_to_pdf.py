from _core import ROOT, run, require_pip, iter_src, no_files_warning, done, ask_choice, OUT_DIR

THEMES_DIR = ROOT / "themes"

require_pip(markdown="markdown", xhtml2pdf="xhtml2pdf")

import re

import markdown
from xhtml2pdf import pisa

# Print-friendly CSS: readable body, boxed code, bordered tables
CSS_CLASSIC = """
@page { size: A4; margin: 2cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 4pt; margin: 0 0 12pt 0; }
h2 { font-size: 15pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; margin: 18pt 0 8pt 0; }
h3 { font-size: 12pt; margin: 14pt 0 6pt 0; }
h4 { font-size: 11pt; margin: 12pt 0 6pt 0; }
p { margin: 0 0 8pt 0; }
a { color: #1155cc; text-decoration: none; }
ul, ol { margin: 0 0 8pt 0; padding-left: 18pt; }
li { margin: 0 0 3pt 0; }
.inline { font-family: "Courier New", monospace; font-size: 9pt; background: #f2f2f2;
       padding: 1pt 3pt; border-radius: 2pt; }
pre { font-family: "Courier New", monospace; font-size: 8.5pt; background: #f6f8fa;
      border: 1px solid #ddd; border-radius: 3pt; padding: 8pt; margin: 0 0 10pt 0;
      white-space: pre; }
blockquote { border-left: 3px solid #ccc; margin: 0 0 8pt 0; padding: 2pt 0 2pt 10pt;
             color: #555; }
table { border-collapse: collapse; width: 100%; margin: 0 0 10pt 0; font-size: 9pt; }
th, td { border: 1px solid #bbb; padding: 4pt 6pt; text-align: left; vertical-align: top; }
th { background: #efefef; font-weight: bold; }
hr { border: none; border-top: 1px solid #ccc; margin: 12pt 0; }
"""

# Claude / Anthropic-inspired theme: warm cream page, ink text, coral accents,
# serif headings. Kept within what xhtml2pdf's CSS subset can render.
# xhtml2pdf ignores background-color on @page/body, so the cream page comes
# from a generated 1x1 PNG stretched via @page background-image ({bg} slot).
CSS_CLAUDE = """
@page { size: A4; margin: 2.2cm; background-image: url('{bg}'); }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.55;
       color: #141413; }
h1 { font-family: Georgia, "Times New Roman", serif; font-weight: normal; font-size: 22pt;
     color: #141413; border-bottom: 2pt solid #D97757; padding-bottom: 6pt; margin: 0 0 14pt 0; }
h2 { font-family: Georgia, "Times New Roman", serif; font-weight: normal; font-size: 15pt;
     color: #141413; border-bottom: 0.5pt solid #E8E6DC; padding-bottom: 3pt; margin: 20pt 0 8pt 0; }
h3 { font-family: Georgia, "Times New Roman", serif; font-size: 12pt; color: #3D3D3A;
     margin: 15pt 0 6pt 0; }
h4 { font-size: 10.5pt; color: #5E5D59; margin: 12pt 0 5pt 0; }
p { margin: 0 0 8pt 0; }
a { color: #D97757; text-decoration: none; }
strong { color: #141413; }
ul, ol { margin: 0 0 8pt 0; padding-left: 18pt; }
li { margin: 0 0 3pt 0; }
.inline { font-family: "Courier New", monospace; font-size: 9pt; color: #B3572E;
       background: #F0EEE5; padding: 1pt 3pt; border-radius: 2pt; }
pre { font-family: "Courier New", monospace; font-size: 8.5pt; color: #141413;
      background: #F0EEE5; border: 0.5pt solid #E0DED3; border-radius: 4pt;
      padding: 8pt; margin: 0 0 10pt 0; white-space: pre; }
blockquote { border-left: 3pt solid #D97757; margin: 0 0 8pt 0; padding: 2pt 0 2pt 10pt;
             color: #5E5D59; }
table { border-collapse: collapse; width: 100%; margin: 0 0 10pt 0; font-size: 9pt; }
th, td { border: 0.5pt solid #D9D7CC; padding: 5pt 7pt; text-align: left; vertical-align: top; }
th { background: #F0EEE5; color: #141413; font-weight: bold; }
hr { border: none; border-top: 0.5pt solid #D9D7CC; margin: 14pt 0; }
"""

CREAM_RGB = (250, 249, 245)  # #FAF9F5


def make_bg_png(rgb):
    """Write a 1x1 PNG of the given colour (stdlib only) and return its path."""
    import struct
    import tempfile
    import zlib

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00" + bytes(rgb))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    f.write(png)
    f.close()
    return f.name.replace("\\", "/")


def convert_to_pdf(in_path, out_path, css):
    try:
        text = in_path.read_text(encoding="utf-8")
        body = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "codehilite", "sane_lists", "toc"],
            extension_configs={"codehilite": {"noclasses": True}},
        )
        # xhtml2pdf ignores descendant selectors (e.g. "pre code"), so tag
        # inline <code> with a class themes can target without also hitting
        # code inside <pre> blocks.
        body = body.replace("<code>", '<code class="inline">')
        body = re.sub(r"(<pre[^>]*>)<code class=\"inline\">", r"\1<code>", body)
        # xhtml2pdf drops CSS padding on auto-sized cells (narrow columns get
        # clipped) but honours the HTML cellpadding attribute; empty cells
        # lose their borders unless they contain at least a &nbsp;.
        body = body.replace("<table>", '<table cellpadding="5">')
        body = re.sub(r"<(td|th)([^>]*)>\s*</\1>", r"<\1\2>&nbsp;</\1>", body)
        html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
        with open(out_path, "wb") as f:
            result = pisa.CreatePDF(html, dest=f, encoding="utf-8")
        if result.err:
            print(f"✗ Error rendering {in_path.name}")
            return False
        print(f"✓ {in_path.name} -> {out_path.name}")
        return True
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")
        return False


@run("MARKDOWN TO PDF")
def main():
    # Built-in themes + any custom .css design system dropped into themes/
    options = [
        "Classic (neutral print style, white page)",
        "Claude  (Anthropic-inspired: cream page, serif headings, coral accents)",
    ]
    THEMES_DIR.mkdir(exist_ok=True)
    custom_themes = sorted(THEMES_DIR.glob("*.css"), key=lambda p: p.name.lower())
    options += [f"{t.stem} (custom, themes/{t.name})" for t in custom_themes]

    theme = ask_choice("Theme", options, default=1)
    if theme == 1:
        css = CSS_CLASSIC
    elif theme == 2:
        css = CSS_CLAUDE.replace("{bg}", make_bg_png(CREAM_RGB))
    else:
        css = custom_themes[theme - 3].read_text(encoding="utf-8")
    print()

    md_files = iter_src({'.md'})
    if not md_files:
        no_files_warning(".md files", {'.md'})
        return
    processed = sum(convert_to_pdf(f, OUT_DIR / (f.stem + ".pdf"), css) for f in md_files)
    done(processed, len(md_files))


main()

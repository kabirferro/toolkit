import os
import sys
from pathlib import Path

# Windows console defaults to cp1252 and chokes on ✓/✗ — force UTF-8 output
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Check dependencies
missing_deps = []
try:
    import markdown
except ImportError:
    missing_deps.append("markdown")

try:
    from xhtml2pdf import pisa
except ImportError:
    missing_deps.append("xhtml2pdf")

if missing_deps:
    print("\n⚠  MISSING DEPENDENCIES\n")
    print("The following libraries are not installed:")
    for dep in missing_deps:
        print(f"  - {dep}")
    print("\nInstall with:")
    print("  py -m pip install markdown xhtml2pdf\n")
    input("Press ENTER to exit...")
    sys.exit(1)

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
SRC_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

# Print-friendly CSS: readable body, boxed code, bordered tables
CSS = """
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
code { font-family: "Courier New", monospace; font-size: 9pt; background: #f2f2f2;
       padding: 1pt 3pt; border-radius: 2pt; }
pre { font-family: "Courier New", monospace; font-size: 8.5pt; background: #f6f8fa;
      border: 1px solid #ddd; border-radius: 3pt; padding: 8pt; margin: 0 0 10pt 0;
      white-space: pre-wrap; word-wrap: break-word; }
pre code { background: transparent; padding: 0; }
blockquote { border-left: 3px solid #ccc; margin: 0 0 8pt 0; padding: 2pt 0 2pt 10pt;
             color: #555; }
table { border-collapse: collapse; width: 100%; margin: 0 0 10pt 0; font-size: 9pt; }
th, td { border: 1px solid #bbb; padding: 4pt 6pt; text-align: left; vertical-align: top; }
th { background: #efefef; font-weight: bold; }
hr { border: none; border-top: 1px solid #ccc; margin: 12pt 0; }
"""

print("\n=== MARKDOWN TO PDF ===\n")


def convert_to_pdf(in_path: Path, out_path: Path) -> bool:
    try:
        text = in_path.read_text(encoding="utf-8")
        body = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "codehilite", "sane_lists", "toc"],
            extension_configs={"codehilite": {"noclasses": True}},
        )
        html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
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


md_files = sorted(SRC_DIR.glob("*.md"), key=lambda p: p.name.lower())
if not md_files:
    print("⚠  No .md files found in src/\n")
    input("Press ENTER to exit...")
    sys.exit(0)

success = 0
for md_file in md_files:
    if convert_to_pdf(md_file, OUT_DIR / (md_file.stem + ".pdf")):
        success += 1

print(f"\n=== Done! {success}/{len(md_files)} files converted ===\n")
input("Press ENTER to exit...")

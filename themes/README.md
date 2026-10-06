# Custom themes for md_to_pdf.py

Drop one `.css` file per design system in this folder: `md_to_pdf.py` lists them
in the theme menu automatically (the file name becomes the theme name).

Start by copying `_template.css` and swapping in your brand tokens (colors, fonts).

## Renderer limits (xhtml2pdf)

- Supported: colors, borders, margins/padding, tables, `@page`, `@font-face` with local `.ttf` files.
- NOT supported: flexbox/grid, CSS variables (`var(--x)`), box-shadow, external URLs.
- Full-page background color: `background-color` on `@page`/`body` is ignored;
  use a solid-color image via `@page { background-image: url('themes/bg.png'); }` (stretched to full page).
- Code blocks never wrap on their own (`white-space: pre` turns every space into
  a NBSP): `md_to_pdf.py` soft-wraps `<pre>` lines itself, computing the width
  from the theme's `@page` size/margin and the `pre` font-size/padding. Keep the
  `pre` font monospaced, and declare those properties on a plain `pre` selector
  so they can be read.
- Custom fonts: put the `.ttf` next to the css and declare
  `@font-face { font-family: MyBrand; src: url('themes/MyBrand.ttf'); }`.

Paths in `url()` are relative to the toolkit root (scripts chdir there).

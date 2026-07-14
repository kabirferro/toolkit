# Toolkit

A collection of Python CLI scripts for batch processing images, PDFs, and videos.

Every root script is double-click friendly on Windows: it checks its own dependencies, asks settings interactively, processes `src/` into `out/`, prints a summary and waits for ENTER before closing (so errors stay visible). Shared plumbing lives in the `_core/` package.

---

## Setup

### Requirements

- Python 3.8+
- ffmpeg (for video scripts only)

### Install Python dependencies

```bash
py -m pip install Pillow pillow-heif pypdf pypdfium2 reportlab markdown xhtml2pdf
```

### Install ffmpeg (video scripts only)

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

---

## How it works

1. Place input files in the `src/` folder
2. Run the desired script: `py script_name.py`
3. Collect output from the `out/` folder

Both `src/` and `out/` are created automatically on first run.

> **For `hosts_add.py`:** copy `.env.example` to `.env` and fill in your IP presets (see [IP presets configuration](#ip-presets-configuration)).

---

## Structure

```
toolkit/
├── _core/                  # Shared runtime (deps check, prompts, src/out handling)
├── src/                    # Input files
├── out/                    # Output files (auto-created)
├── images_to_jpg.py
├── images_to_webp.py
├── images_compress.py
├── images_resize.py
├── images_merge_to_gif.py
├── images_remove_metadata.py
├── images_to_pdf.py
├── pdf_compress.py
├── pdf_merge.py
├── pdf_split.py
├── pdf_rotate.py
├── pdf_to_images.py
├── pdf_extract_text.py
├── md_to_pdf.py
├── videos_to_mp4.py
├── videos_compress.py
├── videos_resize.py
├── videos_to_audio.py
├── mov_to_mp4.py
├── hosts_add.py
├── .env.example            # Config template (commit this)
├── .env                    # Your local config (gitignored)
└── server-kit/
    ├── compress-jpgs.py
    ├── git-check.py
    └── video-optimizer.py
```

---

## Image scripts

### `images_to_jpg.py`
Converts images to JPG. Supports HEIC/HEIF (iPhone photos).
- **Input:** PNG, WebP, HEIC, BMP, GIF, TIFF, and more
- **Output:** JPG at quality 85
- **Dependencies:** Pillow, pillow-heif

### `images_to_webp.py`
Converts images to WebP format.
- **Input:** JPG, PNG, BMP, TIFF, GIF, HEIC
- **Output:** WebP at quality 80 (lossy)
- **Dependencies:** Pillow

### `images_compress.py`
Compresses images while keeping the original format.
- **Input:** JPG, PNG, WebP, BMP, TIFF
- **Output:** Same format, reduced file size
- **Modes (interactive):**
  1. Light -- high quality, minimal size reduction
  2. Medium -- balanced quality and compression
  3. Heavy -- maximum compression, lower quality
- **Dependencies:** Pillow

### `images_resize.py`
Resizes images. Three modes selectable at runtime.
- **Input:** JPG, PNG, WebP, BMP, TIFF
- **Output:** JPG
- **Modes (interactive):**
  1. **Cover** -- crop to exact dimensions with anchor point  
     Anchor grid (numpad layout):  
     `7=top-left  8=top-center    9=top-right`  
     `4=left      5=center        6=right`  
     `1=bot-left  2=bot-center    3=bot-right`
  2. **Percentage** -- proportional resize by percentage (e.g. 50 = half)
  3. **Fixed side** -- set width or height, scale the other proportionally
- **Dependencies:** Pillow

### `images_merge_to_gif.py`
Merges multiple images into an animated GIF.
- **Input:** JPG, PNG, WebP, BMP, TIFF (all files in `src/`)
- **Output:** `animation.gif`
- **Parameters (interactive):** FPS (frames per second)
- **Note:** Images are sorted alphabetically to determine frame order
- **Dependencies:** Pillow

### `images_remove_metadata.py`
Strips EXIF metadata from images (removes GPS, camera info, etc.).
- **Input:** JPG, PNG, WebP, BMP, TIFF
- **Output:** Same format, no metadata
- **Dependencies:** Pillow

### `images_to_pdf.py`
Converts images to a single PDF file. Two modes available.
- **Input:** JPG, PNG, WebP, BMP, TIFF (mode 1) / same + GIF, HEIC (mode 2)
- **Output:** `images.pdf`
- **Modes (interactive):**
  1. **Single page** -- one image per page  
     - Layout: Fit / Fill / Original  
     - Page size: A4 / Letter / Custom
  2. **Thumbnails** -- grid layout with filenames  
     - Configurable images per row (1-10, default 5)  
     - Auto page breaks, multi-page support
- **Dependencies:** Pillow, reportlab

---

## PDF scripts

### `pdf_compress.py`
Reduces PDF file size by recompressing content.
- **Input:** PDF files in `src/`
- **Output:** Compressed PDF
- **Levels (interactive):** Light / Medium / Heavy
- **Dependencies:** pypdf

### `pdf_merge.py`
Merges multiple PDF files into one.
- **Input:** PDF files in `src/` (sorted alphabetically)
- **Output:** Single merged PDF (name chosen interactively)
- **Dependencies:** pypdf

### `pdf_split.py`
Splits a PDF into individual pages.
- **Input:** One PDF in `src/`
- **Output:** One file per page (e.g. `document_page001.pdf`, `document_page002.pdf`)
- **Dependencies:** pypdf

### `pdf_rotate.py`
Rotates pages in a PDF.
- **Input:** One PDF in `src/`
- **Output:** Rotated PDF
- **Parameters (interactive):** Page selection (all / range / specific pages), rotation angle (90 / 180 / 270)
- **Dependencies:** pypdf

### `pdf_to_images.py`
Renders each PDF page to an image file.
- **Input:** PDF files in `src/`
- **Output:** One image per page (e.g. `document-01.jpg`)
- **Parameters (interactive):** Format (JPG / PNG), resolution in DPI (default 150)
- **Dependencies:** pypdfium2

### `pdf_extract_text.py`
Extracts the text layer from PDFs to plain text files (no OCR: scanned PDFs yield empty text).
- **Input:** PDF files in `src/`
- **Output:** One `.txt` per PDF
- **Parameters (interactive):** Plain text or with `--- Page N ---` markers
- **Dependencies:** pypdf

### `md_to_pdf.py`
Converts Markdown files to PDF (tables and code blocks styled for print).
- **Input:** `.md` files in `src/`
- **Output:** One PDF per file
- **Themes (interactive):**
  1. **Classic** -- neutral print style, white page
  2. **Claude** -- Anthropic-inspired: cream page, serif headings, coral accents
  3. **Custom** -- any `.css` file in `themes/` is listed automatically (see `themes/README.md`; start from `themes/_template.css`)
- **Dependencies:** markdown, xhtml2pdf

---

## Video scripts

### `videos_to_mp4.py`
Converts videos to MP4 (H.264 + AAC).
- **Input:** MOV, AVI, MKV, WebM, FLV, WMV, M4V
- **Output:** MP4
- **Dependencies:** ffmpeg

### `videos_compress.py`
Compresses videos to reduce file size.
- **Input:** MP4, MOV, AVI, MKV, WebM
- **Output:** Compressed MP4
- **Levels (interactive):**
  1. Light -- CRF 23, fast encode
  2. Medium -- CRF 28, medium preset
  3. Heavy -- CRF 35, slow preset (smallest file)
- **Dependencies:** ffmpeg

### `videos_resize.py`
Resizes videos. Two modes available.
- **Input:** MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V
- **Output:** MP4 (H.264, AAC 128k)
- **Modes (interactive):**
  1. **Fit** -- scale to target dimensions, pad to fill with blur / black / white background
  2. **Percentage** -- proportional resize by percentage
- **Dependencies:** ffmpeg, ffprobe

### `videos_to_audio.py`
Extracts the audio track from videos.
- **Input:** MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V
- **Output (interactive):** MP3 (192k) / M4A-AAC (192k) / WAV (uncompressed)
- **Dependencies:** ffmpeg

### `mov_to_mp4.py`
Converts MOV files to MP4 stripping the audio track (H.264, no audio).
- **Input:** MOV files in `src/`
- **Output:** MP4 without audio
- **Dependencies:** ffmpeg

---

## Other scripts

### `hosts_add.py`
Adds entries to the Windows hosts file. Requires administrator privileges (auto-elevates).
- **Features:**
  - IP presets loaded dynamically from `.env` (one per line, any number)
  - Always includes `127.0.0.1` (localhost) and a Custom option
  - Duplicate detection with optional overwrite
  - Automatic backup saved to `../config/hosts.txt`
  - Loop to add multiple hosts in one session
- **Platform:** Windows only
- **Dependencies:** none (stdlib only)

#### IP presets configuration

Copy `.env.example` to `.env` (gitignored) and add your presets:

```ini
HOSTS_ADD_PRESET_1=192.168.1.50|custom.local
```

Format: `HOSTS_ADD_PRESET_N=ip|label` -- add as many as needed, numbered sequentially.  
`.env.example` is the template to commit; `.env` stays local.

---

## Server-kit scripts

Scripts in `server-kit/` are designed to run directly on a server (or any machine) against a target directory passed as an argument. They do **not** use `src/` / `out/` folders.

### `server-kit/compress-jpgs.py`
Recursively scans a directory and recompresses JPEG files older than a given age using ffmpeg. Replaces the original only if the compressed file is smaller.
- **Usage:** `py server-kit/compress-jpgs.py <workdir> [--quality N] [--age-days N]`
- **Options:**
  - `--quality` — ffmpeg JPEG quality scale (1 = best, 31 = worst, default: `2`)
  - `--age-days` — skip files newer than this many days (default: `180`)
- **Dependencies:** ffmpeg

### `server-kit/git-check.py`
Recursively finds Git repositories under a root directory and reports any that are not aligned: uncommitted changes, commits to push, or (optionally) commits to pull from remote.
- **Usage:** `py server-kit/git-check.py <workdir> [--fetch] [--depth N]`
- **Options:**
  - `--fetch` — run `git fetch` on each repo before checking (slower, enables pull detection)
  - `--depth` — max directory depth to search (default: `2`)
- **Dependencies:** git

### `server-kit/video-optimizer.py`
Recursively scans a directory for MP4 files and re-encodes them with H.264 + AAC (`-movflags faststart`) if they are not already optimized. Skips files below a minimum size.
- **Usage:** `py server-kit/video-optimizer.py <workdir> [--min-size MB]`
- **Options:**
  - `--min-size` — skip files smaller than this many MB (default: `50`)
- **Dependencies:** ffmpeg, ffprobe
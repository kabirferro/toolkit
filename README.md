# Toolkit

A collection of Python CLI scripts for batch processing images, PDFs, and videos.

---

## Setup

### Requirements

- Python 3.8+
- ffmpeg (for video scripts only)

### Install Python dependencies

```bash
py -m pip install Pillow pillow-heif pypdf reportlab
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

> **For `hosts_add.py`:** copy `hosts_add.env.example` to `hosts_add.env` and fill in your IP presets (see [IP presets configuration](#ip-presets-configuration)).

---

## Structure

```
toolkit/
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
├── videos_to_mp4.py
├── videos_compress.py
├── videos_resize.py
├── hosts_add.py
├── hosts_add.env.example   # IP presets template (commit this)
└── hosts_add.env           # Your local presets (gitignored)
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

---

## Other scripts

### `hosts_add.py`
Adds entries to the Windows hosts file. Requires administrator privileges (auto-elevates).
- **Features:**
  - IP presets loaded dynamically from `hosts_add.env` (one per line, any number)
  - Always includes `127.0.0.1` (localhost) and a Custom option
  - Duplicate detection with optional overwrite
  - Automatic backup saved to `../config/hosts.txt`
  - Loop to add multiple hosts in one session
- **Platform:** Windows only
- **Dependencies:** none (stdlib only)

#### IP presets configuration

Copy `hosts_add.env.example` to `hosts_add.env` (gitignored) and add your presets:

```ini
PRESET_1=192.168.1.50|custom.local
```

Format: `PRESET_N=ip|label` -- add as many as needed, numbered sequentially.  
`hosts_add.env.example` is the template to commit; `hosts_add.env` stays local.
import os
import sys
from pathlib import Path

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    print("\n⚠  MISSING DEPENDENCY\n")
    print("Pillow is not installed.\n")
    print("Install with:")
    print("  py -m pip install Pillow\n")
    input("Press ENTER to exit...")
    sys.exit(1)

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
OUT_DIR.mkdir(exist_ok=True)

QUALITY = 90

print("\n=== IMAGE RESIZE ===\n")
print("Choose resize mode:")
print("1. Cover     (resize + crop with anchor point, like CSS cover)")
print("2. Percentage (resize proportionally by percentage)")
print("3. Fixed side (fix one dimension, scale the other keeping ratio)")
resize_type = input("\nYour choice (1/2/3): ").strip()

# Parametri specifici per ogni tipo
if resize_type == "1":  # COVER
    print("\n--- COVER ---")
    target_width = int(input("Target width (px): "))
    target_height = int(input("Target height (px): "))

    print("\nAnchor point (like a numpad):")
    print("7 8 9  (top-left, top-center, top-right)")
    print("4 5 6  (middle-left, center, middle-right)")
    print("1 2 3  (bottom-left, bottom-center, bottom-right)")
    anchor_input = input("\nEnter number (default 5 = center): ").strip()
    anchor = int(anchor_input) if anchor_input else 5

    if anchor not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        print("⚠  Invalid value, defaulting to center (5)")
        anchor = 5

    anchor_names = {
        7: "top-left", 8: "top-center", 9: "top-right",
        4: "middle-left", 5: "center", 6: "middle-right",
        1: "bottom-left", 2: "bottom-center", 3: "bottom-right",
    }

    print(f"\nCover {target_width}x{target_height} — anchor: {anchor_names[anchor]}\n")

elif resize_type == "2":  # PERCENTAGE
    print("\n--- PERCENTAGE ---")
    percentage = float(input("Percentage (e.g. 50 = half size, 200 = double): "))
    print(f"\nProcessing at {percentage}%...\n")

elif resize_type == "3":  # FIXED SIDE
    print("\n--- FIXED SIDE ---")
    print("Which dimension to fix?")
    print("1. Width")
    print("2. Height")
    fixed_dimension = input("\nYour choice (1/2): ").strip()

    if fixed_dimension == "1":
        fixed_width = int(input("Fixed width (px): "))
        print(f"\nProcessing with fixed width {fixed_width}px...\n")
    elif fixed_dimension == "2":
        fixed_height = int(input("Fixed height (px): "))
        print(f"\nProcessing with fixed height {fixed_height}px...\n")
    else:
        print("⚠  Invalid choice, exiting.")
        sys.exit(1)
else:
    print("⚠  Invalid choice, exiting.")
    sys.exit(1)


def resize_cover(in_path: Path, out_path: Path, target_w, target_h, anchor_pos=5, quality=QUALITY):
    try:
        with Image.open(in_path) as im:
            ext = in_path.suffix.lower()
            original_mode = im.mode
            has_transparency = original_mode in ("RGBA", "LA", "P") and ("transparency" in im.info or original_mode in ("RGBA", "LA"))

            # Flatten transparency for JPEG
            if ext in ('.jpg', '.jpeg') and im.mode in ("RGBA", "LA"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[-1])
                im = background
            elif ext in ('.jpg', '.jpeg') and im.mode != "RGB":
                im = im.convert("RGB")
            elif im.mode == "P":
                im = im.convert("RGBA" if has_transparency else "RGB")
            
            original_width = im.width
            original_height = im.height
            
            # Calcola i ratio per effetto cover
            img_ratio = im.width / im.height
            target_ratio = target_w / target_h
            
            # Ridimensiona l'immagine mantenendo le proporzioni
            # In modo che copra completamente l'area target
            if img_ratio > target_ratio:
                # Immagine più larga: ridimensiona in base all'altezza
                new_height = target_h
                new_width = int(new_height * img_ratio)
            else:
                # Immagine più alta: ridimensiona in base alla larghezza
                new_width = target_w
                new_height = int(new_width / img_ratio)
            
            # Ridimensiona
            im_resized = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop anchor: horizontal
            # 1,4,7 = left | 2,5,8 = center | 3,6,9 = right
            if anchor_pos in [1, 4, 7]:  # left
                left = 0
            elif anchor_pos in [3, 6, 9]:  # right
                left = new_width - target_w
            else:  # center (2, 5, 8)
                left = (new_width - target_w) // 2

            # Vertical: 7,8,9 = top | 4,5,6 = center | 1,2,3 = bottom
            if anchor_pos in [7, 8, 9]:  # top
                top = 0
            elif anchor_pos in [1, 2, 3]:  # bottom
                top = new_height - target_h
            else:  # center (4, 5, 6)
                top = (new_height - target_h) // 2
            
            right = left + target_w
            bottom = top + target_h
            
            # Crop
            im_cropped = im_resized.crop((left, top, right, bottom))
            
            # Salva nel formato originale
            if ext in ('.jpg', '.jpeg'):
                im_cropped.save(out_path, format="JPEG", quality=quality, optimize=True)
            elif ext == '.png':
                im_cropped.save(out_path, format="PNG", optimize=True)
            elif ext == '.webp':
                im_cropped.save(out_path, format="WEBP", quality=quality, method=6)
            else:
                im_cropped.save(out_path, quality=quality, optimize=True)
            
        print(f"✓ {in_path.name} -> {out_path.name} ({original_width}x{original_height} → {target_w}x{target_h})")
        
    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")


def resize_by_percentage(in_path: Path, out_path: Path, percent, quality=QUALITY):
    try:
        with Image.open(in_path) as im:
            # Determina formato e modalità colore originale
            ext = in_path.suffix.lower()
            original_mode = im.mode
            has_transparency = original_mode in ("RGBA", "LA", "P") and ("transparency" in im.info or original_mode in ("RGBA", "LA"))
            
            # Converti in RGB solo per formati che non supportano trasparenza (JPEG)
            if ext in ('.jpg', '.jpeg') and im.mode in ("RGBA", "LA"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[-1])
                im = background
            elif ext in ('.jpg', '.jpeg') and im.mode != "RGB":
                im = im.convert("RGB")
            elif im.mode == "P":
                im = im.convert("RGBA" if has_transparency else "RGB")
            
            # Calcola nuove dimensioni
            original_width = im.width
            original_height = im.height
            new_width = int(original_width * percent / 100)
            new_height = int(original_height * percent / 100)
            
            # Ridimensiona mantenendo il ratio
            im_resized = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Salva nel formato originale
            if ext in ('.jpg', '.jpeg'):
                im_resized.save(out_path, format="JPEG", quality=quality, optimize=True)
            elif ext == '.png':
                im_resized.save(out_path, format="PNG", optimize=True)
            elif ext == '.webp':
                im_resized.save(out_path, format="WEBP", quality=quality, method=6)
            else:
                im_resized.save(out_path, quality=quality, optimize=True)
            
        print(f"✓ {in_path.name} -> {out_path.name} ({original_width}x{original_height} → {new_width}x{new_height})")

    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")


def resize_fixed_size(in_path: Path, out_path: Path, fixed_w=None, fixed_h=None, quality=QUALITY):
    try:
        with Image.open(in_path) as im:
            # Determina formato e modalità colore originale
            ext = in_path.suffix.lower()
            original_mode = im.mode
            has_transparency = original_mode in ("RGBA", "LA", "P") and ("transparency" in im.info or original_mode in ("RGBA", "LA"))
            
            # Converti in RGB solo per formati che non supportano trasparenza (JPEG)
            if ext in ('.jpg', '.jpeg') and im.mode in ("RGBA", "LA"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[-1])
                im = background
            elif ext in ('.jpg', '.jpeg') and im.mode != "RGB":
                im = im.convert("RGB")
            elif im.mode == "P":
                im = im.convert("RGBA" if has_transparency else "RGB")
            
            original_width = im.width
            original_height = im.height
            
            # Calcola le nuove dimensioni mantenendo il ratio
            if fixed_w is not None:
                # Fixed width, calculate height
                new_width = fixed_w
                new_height = int(original_height * (fixed_w / original_width))
            else:
                # Fixed height, calculate width
                new_height = fixed_h
                new_width = int(original_width * (fixed_h / original_height))
            
            # Ridimensiona mantenendo il ratio
            im_resized = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Salva nel formato originale
            if ext in ('.jpg', '.jpeg'):
                im_resized.save(out_path, format="JPEG", quality=quality, optimize=True)
            elif ext == '.png':
                im_resized.save(out_path, format="PNG", optimize=True)
            elif ext == '.webp':
                im_resized.save(out_path, format="WEBP", quality=quality, method=6)
            else:
                im_resized.save(out_path, quality=quality, optimize=True)
            
        print(f"✓ {in_path.name} -> {out_path.name} ({original_width}x{original_height} → {new_width}x{new_height})")

    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")


processed = 0

for file_path in SRC_DIR.iterdir():
    if file_path.is_file():
        original_ext = file_path.suffix
        if resize_type == "2":
            out_file = OUT_DIR / f"{file_path.stem}-{int(percentage)}{original_ext}"
        else:
            out_file = OUT_DIR / f"{file_path.stem}{original_ext}"

        if resize_type == "1":
            resize_cover(file_path, out_file, target_width, target_height, anchor)
        elif resize_type == "2":
            resize_by_percentage(file_path, out_file, percentage)
        elif resize_type == "3":
            if fixed_dimension == "1":
                resize_fixed_size(file_path, out_file, fixed_w=fixed_width)
            else:
                resize_fixed_size(file_path, out_file, fixed_h=fixed_height)

        processed += 1

print(f"\n=== Done! {processed} images processed ===\n")

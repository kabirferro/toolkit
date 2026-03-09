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

print("\n=== IMAGE COMPRESS ===\n")
print("Compression level:")
print("1. High quality  (light compression, preserves colours)")
print("2. Balanced      (medium compression, good trade-off)")
print("3. Max compact   (smallest files, possible quality loss)")
level_input = input("\nChoose level (1-3, default 1): ").strip()
level = int(level_input) if level_input in ('1', '2', '3') else 1

# Per-level compression settings
compression_settings = {
    1: {'quality': 95, 'optimize': True, 'subsampling': 0},  # 4:4:4
    2: {'quality': 85, 'optimize': True, 'subsampling': 1},  # 4:2:2
    3: {'quality': 75, 'optimize': True, 'subsampling': 2},  # 4:2:0
}

settings = compression_settings[level]
QUALITY = settings['quality']
OPTIMIZE = settings['optimize']
SUBSAMPLING = settings['subsampling']

subsampling_labels = ['4:4:4 (max quality)', '4:2:2 (balanced)', '4:2:0 (max compression)']
print(f"\nLevel {level} — JPEG quality {QUALITY}/100, subsampling {subsampling_labels[SUBSAMPLING]}\n")

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif'}


def compress_image(in_path: Path, out_path: Path, quality=QUALITY, optimize=OPTIMIZE, subsampling=SUBSAMPLING):
    try:
        with Image.open(in_path) as im:
            ext = in_path.suffix.lower()

            if ext in {'.jpg', '.jpeg'}:
                if im.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', im.size, (255, 255, 255))
                    if im.mode == 'P':
                        im = im.convert('RGBA')
                    background.paste(im, mask=im.split()[-1] if im.mode in ('RGBA', 'LA') else None)
                    im = background
                elif im.mode != 'RGB':
                    im = im.convert('RGB')
                im.save(out_path, format='JPEG', quality=quality, optimize=optimize, subsampling=subsampling)

            elif ext == '.png':
                if im.mode not in ('RGB', 'RGBA', 'P', 'L'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                compress_level = 9 if subsampling == 2 else (6 if subsampling == 1 else 3)
                im.save(out_path, format='PNG', optimize=optimize, compress_level=compress_level)

            elif ext == '.webp':
                if im.mode not in ('RGB', 'RGBA'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                method = 4 if subsampling == 2 else 6
                im.save(out_path, format='WEBP', quality=quality, optimize=optimize, method=method)

            elif ext in {'.bmp', '.tiff', '.tif', '.gif'}:
                format_name = 'TIFF' if ext in {'.tiff', '.tif'} else ext[1:].upper()
                save_kwargs = {'format': format_name}
                if ext == '.gif':
                    im.save(out_path, **save_kwargs, save_all=True, optimize=optimize)
                else:
                    if optimize:
                        save_kwargs['optimize'] = optimize
                    im.save(out_path, **save_kwargs)
            else:
                print(f"Unsupported format: {ext}")
                return

        original_size = in_path.stat().st_size
        compressed_size = out_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100
        print(f"✓ {in_path.name} -> {out_path.name} (reduction: {reduction:.1f}%)")

    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error compressing {in_path.name}: {e}")


for file_path in SRC_DIR.iterdir():
    if file_path.is_file():
        ext = file_path.suffix.lower()
        if ext in SUPPORTED_FORMATS:
            compress_image(file_path, OUT_DIR / file_path.name)
        else:
            print(f"Skipped (unsupported extension): {file_path.name}")


def compress_image(in_path: Path, out_path: Path, quality=QUALITY, optimize=OPTIMIZE, subsampling=SUBSAMPLING):
    try:
        with Image.open(in_path) as im:
            # Determina il formato dall'estensione del file
            ext = in_path.suffix.lower()
            
            # Conversione modalità colore se necessario
            if ext in {'.jpg', '.jpeg'}:
                if im.mode in ('RGBA', 'LA', 'P'):
                    # JPEG non supporta trasparenza, converti in RGB
                    background = Image.new('RGB', im.size, (255, 255, 255))
                    if im.mode == 'P':
                        im = im.convert('RGBA')
                    background.paste(im, mask=im.split()[-1] if im.mode in ('RGBA', 'LA') else None)
                    im = background
                elif im.mode != 'RGB':
                    im = im.convert('RGB')
                
                # Salva JPEG con compressione e subsampling specificato
                im.save(out_path, format='JPEG', quality=quality, optimize=optimize, subsampling=subsampling)
                
            elif ext == '.png':
                # PNG supporta trasparenza
                if im.mode not in ('RGB', 'RGBA', 'P', 'L'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                
                # Salva PNG ottimizzato (compress_level da 0 a 9, default 6)
                compress_level = 9 if subsampling == 2 else (6 if subsampling == 1 else 3)
                im.save(out_path, format='PNG', optimize=optimize, compress_level=compress_level)
                
            elif ext == '.webp':
                # WebP supporta trasparenza
                if im.mode not in ('RGB', 'RGBA'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                
                # Salva WebP con compressione (method 6 = migliore qualità/tempo)
                method = 4 if subsampling == 2 else 6
                im.save(out_path, format='WEBP', quality=quality, optimize=optimize, method=method)
                
            elif ext in {'.bmp', '.tiff', '.tif', '.gif'}:
                # Per altri formati, salva con ottimizzazione se disponibile
                format_name = 'TIFF' if ext in {'.tiff', '.tif'} else ext[1:].upper()
                save_kwargs = {'format': format_name}
                
                if ext == '.gif':
                    # Mantieni l'animazione per GIF se presente
                    im.save(out_path, **save_kwargs, save_all=True, optimize=optimize)
                else:
                    if optimize:
                        save_kwargs['optimize'] = optimize
                    im.save(out_path, **save_kwargs)
            else:
                print(f"Formato non supportato: {ext}")
                return
                
        # Calcola la riduzione dimensione
        original_size = in_path.stat().st_size
        compressed_size = out_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"{in_path.name} -> {out_path.name} (riduzione: {reduction:.1f}%)")
        
    except UnidentifiedImageError:
        print(f"Non è un'immagine valida: {in_path.name}")
    except Exception as e:
        print(f"Errore durante la compressione di {in_path.name}: {e}")

# Ciclo su tutti i file della cartella src
for file_path in SRC_DIR.iterdir():
    if file_path.is_file():
        ext = file_path.suffix.lower()
        if ext in SUPPORTED_FORMATS:
            out_file = OUT_DIR / file_path.name
            compress_image(file_path, out_file)
        else:
            print(f"Estensione non supportata, file ignorato: {file_path.name}")

import os
import sys
import subprocess
from pathlib import Path

# Check ffmpeg dependency
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
    subprocess.run(['ffprobe', '-version'], capture_output=True, check=True, timeout=5)
except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
    print("\n⚠  MISSING DEPENDENCY\n")
    print("ffmpeg is not installed or not in the system PATH.\n")
    print("Installation:")
    print("  Windows: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
    print("           Extract and add the 'bin' folder to the system PATH")
    print("  Linux:   sudo apt install ffmpeg")
    print("  macOS:   brew install ffmpeg\n")
    input("Press ENTER to exit...")
    sys.exit(1)

script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

SRC_DIR = script_dir / "src"
OUT_DIR = script_dir / "out"
SRC_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

try:
    test_file = OUT_DIR / ".test_write"
    test_file.touch()
    test_file.unlink()
except Exception as e:
    print(f"\n⚠  Cannot write to 'out/': {e}\n")
    input("Press ENTER to exit...")
    sys.exit(1)

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}

CRF = 23
PRESET = "medium"

print("\n=== VIDEO RESIZE ===\n")
print("Choose resize mode:")
print("1. Fit        (scale and centre inside the target frame, adds letterbox/pillarbox)")
print("2. Percentage (scale proportionally by percentage)")
resize_type = input("\nYour choice (1/2): ").strip()

if resize_type == "1":
    print("\n--- FIT ---")
    target_width = int(input("Target width (px): "))
    target_height = int(input("Target height (px): "))
    print("\nBackground colour for letterbox bands:")
    print("1. Black (default)")
    print("2. White")
    print("3. Blur (blurred version of the video itself)")
    bg_choice = input("\nYour choice (1/2/3, default 1): ").strip()
    bg_choice = bg_choice if bg_choice in ('1', '2', '3') else '1'
    bg_names = {'1': 'black', '2': 'white', '3': 'blur'}
    print(f"\nProcessing at {target_width}x{target_height} — background: {bg_names[bg_choice]}\n")

elif resize_type == "2":
    print("\n--- PERCENTAGE ---")
    percentage = float(input("Percentage (e.g. 50 = half size, 200 = double): "))
    print(f"\nProcessing at {percentage}%...\n")

else:
    print("⚠  Invalid choice, exiting.")
    sys.exit(1)


def get_video_dimensions(video_path):
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split(','))
        return width, height
    except Exception as e:
        print(f"⚠  Could not read dimensions: {e}")
        return None, None


# Funzione di resize fit (con bande o blur)
def resize_fit(in_path: Path, out_path: Path, target_w, target_h, bg_type='1'):
    try:
        # Ottieni dimensioni originali
        original_width, original_height = get_video_dimensions(in_path)
        if not original_width or not original_height:
            print(f"✗ Impossibile leggere dimensioni: {in_path.name}")
            return False
        
        # Calcola il ratio per il fit (mantiene tutto il video visibile)
        img_ratio = original_width / original_height
        target_ratio = target_w / target_h
        
        # Scale video to fit inside target frame
        if img_ratio > target_ratio:
            # Wider video: scale by width
            scale_width = target_w
            scale_height = int(target_w / img_ratio)
        else:
            # Taller video: scale by height
            scale_height = target_h
            scale_width = int(target_h * img_ratio)
        
        # Ensure scale dimensions are multiples of 2 (ffmpeg requirement)
        scale_width = scale_width if scale_width % 2 == 0 else scale_width - 1
        scale_height = scale_height if scale_height % 2 == 0 else scale_height - 1
        
        # Calculate letterbox/pillarbox padding
        pad_x = (target_w - scale_width) // 2
        pad_y = (target_h - scale_height) // 2
        
        # Use absolute paths for ffmpeg
        in_path_str = str(in_path.resolve())
        out_path_str = str(out_path.resolve())
        
        # Build ffmpeg command based on background type
        if bg_type == '3':  # BLUR background
            filter_complex = (
                f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},boxblur=20[bg];"
                f"[0:v]scale={scale_width}:{scale_height}[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
            )
            cmd = [
                'ffmpeg',
                '-i', in_path_str,
                '-filter_complex', filter_complex,
                '-c:v', 'libx264',
                '-crf', str(CRF),
                '-preset', PRESET,
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                out_path_str
            ]
        else:  # Black or white letterbox bands
            bg_color = 'black' if bg_type == '1' else 'white'
            vf = f"scale={scale_width}:{scale_height},pad={target_w}:{target_h}:{pad_x}:{pad_y}:{bg_color}"
            cmd = [
                'ffmpeg',
                '-i', in_path_str,
                '-vf', vf,
                '-c:v', 'libx264',
                '-crf', str(CRF),
                '-preset', PRESET,
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                out_path_str
            ]
        
        # Esegui ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ ffmpeg error on {in_path.name}:")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                relevant = [l for l in error_lines if any(k in l.lower() for k in ('error', 'invalid', 'failed'))]
                for line in (relevant[-5:] if relevant else error_lines[-3:]):
                    print(f"    {line}")
            return False
        
        print(f"✓ {in_path.name} -> {out_path.name} ({original_width}x{original_height} → {target_w}x{target_h}, scaled to {scale_width}x{scale_height})")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ ffmpeg error on {in_path.name}")
        if e.stderr:
            print(f"    {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {str(e)}")
        return False


# Resize by percentage
def resize_by_percentage(in_path: Path, out_path: Path, percent):
    try:
        original_width, original_height = get_video_dimensions(in_path)
        if not original_width or not original_height:
            print(f"✗ Cannot read dimensions: {in_path.name}")
            return False

        new_width = int(original_width * percent / 100)
        new_height = int(original_height * percent / 100)
        
        # Ensure dimensions are multiples of 2 (ffmpeg requirement)
        new_width = new_width if new_width % 2 == 0 else new_width - 1
        new_height = new_height if new_height % 2 == 0 else new_height - 1
        
        # Use absolute paths for ffmpeg
        in_path_str = str(in_path.resolve())
        out_path_str = str(out_path.resolve())
        
        cmd = [
            'ffmpeg',
            '-i', in_path_str,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:v', 'libx264',
            '-crf', str(CRF),
            '-preset', PRESET,
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',  # overwrite output file
            out_path_str
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ ffmpeg error on {in_path.name}:")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                relevant = [l for l in error_lines if any(k in l.lower() for k in ('error', 'invalid', 'failed'))]
                for line in (relevant[-5:] if relevant else error_lines[-3:]):
                    print(f"    {line}")
            return False
        
        print(f"✓ {in_path.name} -> {out_path.name} ({original_width}x{original_height} → {new_width}x{new_height})")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ ffmpeg error on {in_path.name}")
        if e.stderr:
            print(f"    {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {str(e)}")
        return False


processed = 0
found = 0

for file_path in SRC_DIR.iterdir():
    if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
        found += 1
        if resize_type == "2":
            out_file = OUT_DIR / f"{file_path.stem}-{int(percentage)}.mp4"
        else:
            out_file = OUT_DIR / f"{file_path.stem}.mp4"
        success = False
        if resize_type == "1":
            success = resize_fit(file_path, out_file, target_width, target_height, bg_choice)
        elif resize_type == "2":
            success = resize_by_percentage(file_path, out_file, percentage)
        if success:
            processed += 1

if found == 0:
    print("⚠  No videos found in 'src/'")
    print("   Supported formats: MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V\n")
else:
    print(f"\n=== Done! {processed}/{found} videos resized ===\n")

input("Press ENTER to exit...")

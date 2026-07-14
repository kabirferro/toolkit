import subprocess

from _core import run, require_bin, run_ffmpeg, iter_src, no_files_warning, done, ask_choice, ask_int, ask_float, OUT_DIR

require_bin("ffmpeg", "ffprobe")

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
CRF = 23
PRESET = "medium"
BG_NAMES = {1: 'black', 2: 'white', 3: 'blur'}


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


def even(n):
    # ffmpeg requires even dimensions for libx264
    return n if n % 2 == 0 else n - 1


def encode_args(out_path):
    return ['-c:v', 'libx264', '-crf', str(CRF), '-preset', PRESET,
            '-c:a', 'aac', '-b:a', '128k', '-y', str(out_path.resolve())]


def resize_fit(in_path, out_path, target_w, target_h, bg_type):
    original_width, original_height = get_video_dimensions(in_path)
    if not original_width or not original_height:
        print(f"✗ Cannot read dimensions: {in_path.name}")
        return False

    # Scale video to fit inside target frame
    img_ratio = original_width / original_height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        scale_width = target_w
        scale_height = int(target_w / img_ratio)
    else:
        scale_height = target_h
        scale_width = int(target_h * img_ratio)
    scale_width, scale_height = even(scale_width), even(scale_height)

    pad_x = (target_w - scale_width) // 2
    pad_y = (target_h - scale_height) // 2
    in_str = str(in_path.resolve())

    if bg_type == 3:  # blurred background
        filter_complex = (
            f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},boxblur=20[bg];"
            f"[0:v]scale={scale_width}:{scale_height}[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )
        cmd = ['ffmpeg', '-i', in_str, '-filter_complex', filter_complex] + encode_args(out_path)
    else:
        bg_color = 'black' if bg_type == 1 else 'white'
        vf = f"scale={scale_width}:{scale_height},pad={target_w}:{target_h}:{pad_x}:{pad_y}:{bg_color}"
        cmd = ['ffmpeg', '-i', in_str, '-vf', vf] + encode_args(out_path)

    if not run_ffmpeg(cmd, in_path.name):
        return False
    print(f"✓ {in_path.name} -> {out_path.name} ({original_width}x{original_height} → {target_w}x{target_h}, scaled to {scale_width}x{scale_height})")
    return True


def resize_by_percentage(in_path, out_path, percent):
    original_width, original_height = get_video_dimensions(in_path)
    if not original_width or not original_height:
        print(f"✗ Cannot read dimensions: {in_path.name}")
        return False

    new_width = even(int(original_width * percent / 100))
    new_height = even(int(original_height * percent / 100))
    cmd = ['ffmpeg', '-i', str(in_path.resolve()), '-vf', f'scale={new_width}:{new_height}'] + encode_args(out_path)

    if not run_ffmpeg(cmd, in_path.name):
        return False
    print(f"✓ {in_path.name} -> {out_path.name} ({original_width}x{original_height} → {new_width}x{new_height})")
    return True


@run("VIDEO RESIZE")
def main():
    mode = ask_choice("Choose resize mode", [
        "Fit        (scale and centre inside the target frame, adds letterbox/pillarbox)",
        "Percentage (scale proportionally by percentage)",
    ], default=1)

    if mode == 1:
        print("\n--- FIT ---")
        target_width = ask_int("Target width (px)", min_value=2)
        target_height = ask_int("Target height (px)", min_value=2)
        print()
        bg_choice = ask_choice("Background colour for letterbox bands", [
            "Black",
            "White",
            "Blur (blurred version of the video itself)",
        ], default=1)
        print(f"\nProcessing at {target_width}x{target_height} — background: {BG_NAMES[bg_choice]}\n")
    else:
        print("\n--- PERCENTAGE ---")
        percentage = ask_float("Percentage (e.g. 50 = half size, 200 = double)", min_value=0)
        print(f"\nProcessing at {percentage}%...\n")

    files = iter_src(VIDEO_EXTENSIONS)
    if not files:
        no_files_warning("videos", VIDEO_EXTENSIONS)
        return

    processed = 0
    for f in files:
        if mode == 1:
            out_file = OUT_DIR / f"{f.stem}.mp4"
            success = resize_fit(f, out_file, target_width, target_height, bg_choice)
        else:
            out_file = OUT_DIR / f"{f.stem}-{int(percentage)}.mp4"
            success = resize_by_percentage(f, out_file, percentage)
        if success:
            processed += 1

    done(processed, len(files), "videos")


main()

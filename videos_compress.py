from _core import run, require_bin, run_ffmpeg, iter_src, no_files_warning, done, ask_choice, OUT_DIR

require_bin("ffmpeg", "ffprobe")

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}

COMPRESSION_SETTINGS = {
    1: {'crf': 20, 'preset': 'slow'},
    2: {'crf': 28, 'preset': 'medium'},
    3: {'crf': 35, 'preset': 'fast'},
}


def compress_video(in_path, out_path, crf, preset):
    cmd = [
        'ffmpeg', '-y', '-i', str(in_path),
        '-vcodec', 'libx264', '-crf', str(crf), '-preset', preset,
        '-acodec', 'aac', '-b:a', '128k',
        str(out_path)
    ]
    if not run_ffmpeg(cmd, in_path.name):
        return False
    original_size = in_path.stat().st_size
    compressed_size = out_path.stat().st_size
    reduction = ((original_size - compressed_size) / original_size) * 100
    print(f"✓ {in_path.name} -> {out_path.name} (reduction: {reduction:.1f}%)")
    return True


@run("VIDEO COMPRESS")
def main():
    level = ask_choice("Compression level", [
        "High quality  (light compression)",
        "Balanced      (medium compression)",
        "Max compact   (smallest files)",
    ], default=1)
    crf, preset = COMPRESSION_SETTINGS[level]['crf'], COMPRESSION_SETTINGS[level]['preset']
    print(f"\nLevel {level} — CRF {crf} (lower = better quality), preset {preset}\n")

    files = iter_src(VIDEO_EXTENSIONS)
    if not files:
        no_files_warning("videos", VIDEO_EXTENSIONS)
        return
    processed = sum(compress_video(f, OUT_DIR / f"{f.stem}.mp4", crf, preset) for f in files)
    done(processed, len(files), "videos")


main()

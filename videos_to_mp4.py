from _core import run, require_bin, run_ffmpeg, iter_src, no_files_warning, done, OUT_DIR

require_bin("ffmpeg", "ffprobe")

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}


def convert_to_mp4(in_path, out_path):
    cmd = [
        'ffmpeg', '-y', '-i', str(in_path),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        str(out_path)
    ]
    if run_ffmpeg(cmd, in_path.name):
        print(f"✓ {in_path.name} -> {out_path.name}")
        return True
    return False


@run("VIDEOS TO MP4")
def main():
    files = iter_src(VIDEO_EXTENSIONS)
    if not files:
        no_files_warning("videos", VIDEO_EXTENSIONS)
        return
    processed = sum(convert_to_mp4(f, OUT_DIR / f"{f.stem}.mp4") for f in files)
    done(processed, len(files), "videos")


main()

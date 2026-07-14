from _core import run, require_bin, run_ffmpeg, iter_src, no_files_warning, done, ask_choice, OUT_DIR

require_bin("ffmpeg", "ffprobe")

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}

FORMATS = {
    1: {'ext': 'mp3', 'args': ['-c:a', 'libmp3lame', '-b:a', '192k']},
    2: {'ext': 'm4a', 'args': ['-c:a', 'aac', '-b:a', '192k']},
    3: {'ext': 'wav', 'args': ['-c:a', 'pcm_s16le']},
}


def extract_audio(in_path, out_path, codec_args):
    cmd = ['ffmpeg', '-y', '-i', str(in_path), '-vn'] + codec_args + [str(out_path)]
    if run_ffmpeg(cmd, in_path.name):
        size_kb = out_path.stat().st_size / 1024
        print(f"✓ {in_path.name} -> {out_path.name} ({size_kb:.0f} KB)")
        return True
    return False


@run("VIDEOS TO AUDIO")
def main():
    choice = ask_choice("Audio format", [
        "MP3 (192 kbps, universal)",
        "M4A / AAC (192 kbps, better quality at same bitrate)",
        "WAV (uncompressed, large files)",
    ], default=1)
    fmt = FORMATS[choice]
    print(f"\nExtracting audio as {fmt['ext'].upper()}\n")

    files = iter_src(VIDEO_EXTENSIONS)
    if not files:
        no_files_warning("videos", VIDEO_EXTENSIONS)
        return
    processed = sum(extract_audio(f, OUT_DIR / f"{f.stem}.{fmt['ext']}", fmt['args']) for f in files)
    done(processed, len(files), "videos")


main()

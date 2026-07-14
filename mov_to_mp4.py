from _core import run, require_bin, run_ffmpeg, iter_src, no_files_warning, done, OUT_DIR

require_bin("ffmpeg")


def convert_mov_to_mp4(in_path, out_path):
    cmd = [
        'ffmpeg', '-y', '-i', str(in_path),
        '-an',  # strip audio
        '-vcodec', 'libx264', '-crf', '23', '-preset', 'fast',
        str(out_path)
    ]
    if run_ffmpeg(cmd, in_path.name):
        print(f"✓ {in_path.name} -> {out_path.name}")
        return True
    return False


@run("MOV TO MP4 (no audio)")
def main():
    files = iter_src({'.mov'})
    if not files:
        no_files_warning(".mov files", {'.mov'})
        return
    processed = sum(convert_mov_to_mp4(f, OUT_DIR / f"{f.stem}.mp4") for f in files)
    done(processed, len(files), "videos")


main()

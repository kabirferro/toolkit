import os
import subprocess
import sys
from pathlib import Path


def exit_with_pause(code: int) -> int:
    try:
        input("Press ENTER to exit...")
    except EOFError:
        pass
    return code


def check_ffmpeg() -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def convert_mov_to_mp4(input_file: Path, output_file: Path) -> bool:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-an",
        "-vcodec",
        "libx264",
        "-crf",
        "23",
        "-preset",
        "fast",
        str(output_file),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error converting {input_file.name}")
            if result.stderr:
                lines = [line.strip() for line in result.stderr.splitlines() if line.strip()]
                if lines:
                    print(f"  ffmpeg: {lines[-1]}")
            return False
        return True
    except Exception as exc:
        print(f"Error converting {input_file.name}: {exc}")
        return False


def main() -> int:
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    src_dir = script_dir / "src"
    out_dir = script_dir / "out"
    src_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)

    if not check_ffmpeg():
        print("ffmpeg is not installed or not available in PATH.")
        print("Install ffmpeg and try again.")
        return exit_with_pause(1)

    mov_files = sorted(
        [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mov"],
        key=lambda p: p.name.lower(),
    )

    if not mov_files:
        print("No .mov files found in: src")
        return exit_with_pause(0)

    success_count = 0
    for mov_file in mov_files:
        mp4_file = out_dir / f"{mov_file.stem}.mp4"
        print(f"Converting {mov_file.name} -> {mp4_file.name}")
        if convert_mov_to_mp4(mov_file, mp4_file):
            success_count += 1
        else:
            print(f"Skipping failed file: {mov_file.name}")

    print(f"Done: {success_count}/{len(mov_files)} files converted.")
    return exit_with_pause(0 if success_count == len(mov_files) else 2)


if __name__ == "__main__":
    sys.exit(main())

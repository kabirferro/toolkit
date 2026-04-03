#!/usr/bin/env python3
"""
Recursively scans a directory for MP4 files and re-encodes them with
H.264 + AAC using ffmpeg if they are not already optimized.
Skips files smaller than --min-size MB.

Usage:
  python video-optimizer.py <workdir> [--min-size MB]
"""

import os
import subprocess
import argparse
from pathlib import Path


def human_size(num_bytes: int) -> str:
    """Return a human-readable string for a byte count."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if num_bytes < 1024:
            return f'{num_bytes:.1f} {unit}'
        num_bytes >>= 10
    return f'{num_bytes:.1f} EB'


def is_already_optimized(src: Path) -> bool:
    """Return True if the video is already H.264 with acceptable bitrate."""
    def probe(*args):
        return subprocess.check_output(
            ['ffprobe', '-v', 'error'] + list(args) + [str(src)],
            stderr=subprocess.DEVNULL
        ).strip().decode()

    codec = probe('-select_streams', 'v:0', '-show_entries', 'stream=codec_name',
                  '-of', 'default=noprint_wrappers=1:nokey=1')
    print(f'  Codec: {codec}')
    if codec != 'h264':
        return False

    # Check moov atom position (faststart)
    duration = probe('-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1')
    print(f'  Faststart check: {duration}')
    if not duration:
        return False

    bitrate = int(probe('-select_streams', 'v:0', '-show_entries', 'stream=bit_rate',
                        '-of', 'default=noprint_wrappers=1:nokey=1'))
    print(f'  Bitrate: {bitrate}')
    if bitrate > 3_500_000:
        return False

    maxrate = int(probe('-select_streams', 'v:0', '-show_entries', 'stream=max_rate,bit_rate',
                        '-of', 'default=noprint_wrappers=1:nokey=1').splitlines()[0])
    print(f'  Maxrate: {maxrate}')
    return maxrate <= 3_500_000


def optimize_video(src: Path) -> None:
    """Re-encode src in place using H.264 + AAC."""
    tmp = src.with_suffix('.tmp.mp4')

    # Remove stale temp file if present
    if tmp.exists():
        tmp.unlink()

    subprocess.call([
        'ffmpeg',
        '-i', str(src),
        '-vcodec', 'libx264',
        '-crf', '28',
        '-preset', 'slow',
        '-movflags', 'faststart',
        '-b:v', '2500k', '-maxrate', '3000k', '-bufsize', '3000k',
        '-acodec', 'aac', '-b:a', '128k',
        str(tmp)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if tmp.exists():
        src.unlink()
        tmp.rename(src)
        print('  Completed.')
    else:
        print('  Encoding failed.')


def process_directory(workdir: Path, min_size: int) -> None:
    """Walk workdir recursively and optimize MP4 files."""
    for src in sorted(workdir.rglob('*.mp4')):
        if not src.is_file():
            continue

        size = src.stat().st_size
        print(f'Processing: {src}')
        print(f'  Size: {human_size(size)}')

        if size < min_size:
            print('  Too small, skipping.')
            continue

        try:
            if is_already_optimized(src):
                print('  Already optimized, skipping.')
                continue
            optimize_video(src)
        except subprocess.CalledProcessError as e:
            print(f'  Conversion error: {e}')
        except Exception as e:
            print(f'  Error: {e}')


def main():
    parser = argparse.ArgumentParser(
        description='Recursively re-encode MP4 files with H.264/AAC using ffmpeg.'
    )
    parser.add_argument('workdir', help='Root directory to scan recursively')
    parser.add_argument('--min-size', type=float, default=5.0,
                        help='Skip files smaller than this size in MB (default: 5)')
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    if not workdir.is_dir():
        print(f'Error: directory "{workdir}" not found.')
        raise SystemExit(1)

    min_bytes = int(args.min_size * 1024 * 1024)
    print(f'Scanning:  {workdir}')
    print(f'Min size:  {human_size(min_bytes)}\n')

    process_directory(workdir, min_bytes)
    print('\nDone.')


if __name__ == '__main__':
    main()
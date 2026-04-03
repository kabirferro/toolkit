#!/usr/bin/env python3
"""
Recursively scans a directory and compresses JPEG files older than a given age
using ffmpeg. Replaces the original only if the compressed file is smaller.

Usage:
  python compress-jpgs.py <workdir> [--quality N] [--age-days N]
"""

import os
import subprocess
import time
import argparse
from pathlib import Path


def compress_jpgs(directory: Path, quality: int = 2, age_days: int = 180) -> None:
    """Compress JPEG files in directory older than age_days."""
    if not directory.is_dir():
        print(f'Directory not found: {directory}')
        return

    cutoff = time.time() - (age_days * 24 * 60 * 60)

    for path in sorted(directory.rglob('*.jpg')):
        if not path.is_file():
            continue

        # Skip files newer than the cutoff
        if path.stat().st_mtime >= cutoff:
            continue

        tmp_path = path.with_name('temp_' + path.name)
        original_size = path.stat().st_size

        cmd = [
            'ffmpeg', '-y',
            '-i', str(path),
            '-c:v', 'mjpeg',
            '-q:v', str(quality),
            '-pix_fmt', 'yuvj444p',
            str(tmp_path)
        ]
        subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if tmp_path.exists():
            if tmp_path.stat().st_size < original_size:
                tmp_path.replace(path)
                print(f'Compressed: {path}')
            else:
                # Compressed file is not smaller, discard it
                tmp_path.unlink()


def main():
    parser = argparse.ArgumentParser(
        description='Compress JPEG files older than a given age using ffmpeg.'
    )
    parser.add_argument('workdir', help='Root directory to scan recursively')
    parser.add_argument('--quality', type=int, default=2,
                        help='ffmpeg JPEG quality scale (1=best, 31=worst, default: 2)')
    parser.add_argument('--age-days', type=int, default=180,
                        help='Only compress files older than this many days (default: 180)')
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    if not workdir.is_dir():
        print(f'Error: directory "{workdir}" not found.')
        raise SystemExit(1)

    print(f'Scanning:  {workdir}')
    print(f'Quality:   {args.quality}')
    print(f'Min age:   {args.age_days} days\n')

    compress_jpgs(workdir, quality=args.quality, age_days=args.age_days)
    print('Done.')


if __name__ == '__main__':
    main()
"""Shared runtime for toolkit root scripts.

Every double-click script follows the same flow:
UTF-8 console fix -> banner -> dependency check -> src/out setup ->
interactive prompts -> batch processing -> summary -> final pause.

The banner and the guaranteed final pause live in `run()`; dependency
checks in `require_pip()` / `require_bin()`; folder setup and file
iteration in `iter_src()`; prompts in the `ask_*` helpers.
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path

# Windows console defaults to cp1252 and chokes on the check/cross marks
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
OUT_DIR = ROOT / "out"


def pause():
    try:
        input("\nPress ENTER to exit...")
    except EOFError:
        pass


def run(title):
    """Decorator for a script's main(): banner first, final pause always
    (even when main() crashes), so the console window never closes on an
    unread error."""
    def decorator(main):
        def wrapper():
            print(f"\n=== {title} ===\n")
            try:
                main()
            except SystemExit:
                raise
            except KeyboardInterrupt:
                print("\n⚠  Interrupted.")
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
            finally:
                pause()
        return wrapper
    return decorator


def require_pip(**modules):
    """require_pip(PIL="Pillow", pypdf="pypdf") — keys are import names,
    values are pip package names. Exits with install instructions if any
    are missing."""
    missing = []
    for import_name, pip_name in modules.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print("⚠  MISSING DEPENDENCIES\n")
        print("The following libraries are not installed:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with:")
        print(f"  py -m pip install {' '.join(missing)}")
        pause()
        sys.exit(1)


def require_bin(*names):
    """Check external binaries (ffmpeg, ffprobe, ...) are on PATH."""
    missing = []
    for name in names:
        try:
            subprocess.run([name, "-version"], capture_output=True, check=True, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            missing.append(name)
    if missing:
        print("⚠  MISSING DEPENDENCY\n")
        print(f"Not installed or not in the system PATH: {', '.join(missing)}\n")
        print("Installation (ffmpeg bundle includes ffprobe):")
        print("  Windows: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
        print("           Extract and add the 'bin' folder to the system PATH")
        print("  Linux:   sudo apt install ffmpeg")
        print("  macOS:   brew install ffmpeg")
        pause()
        sys.exit(1)


def setup_dirs():
    """Create src/ and out/ next to the scripts and verify out/ is writable."""
    os.chdir(ROOT)
    SRC_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    try:
        probe = OUT_DIR / ".write_test"
        probe.touch()
        probe.unlink()
    except Exception as e:
        print(f"⚠  Cannot write to 'out/': {e}")
        pause()
        sys.exit(1)


def iter_src(extensions=None):
    """Sorted files in src/ filtered by extension set (e.g. {'.jpg', '.png'}).
    Calls setup_dirs() so scripts don't have to."""
    setup_dirs()
    files = []
    for f in sorted(SRC_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not f.is_file():
            continue
        if extensions is None or f.suffix.lower() in extensions:
            files.append(f)
    return files


def no_files_warning(what, extensions=None):
    print(f"⚠  No {what} found in 'src/'")
    if extensions:
        print(f"   Supported formats: {', '.join(sorted(e.lstrip('.').upper() for e in extensions))}")


def done(processed, total, noun="files"):
    print(f"\n=== Done! {processed}/{total} {noun} processed ===")


# ---------------------------------------------------------------- prompts

def ask_choice(prompt, options, default=1):
    """Numbered menu; returns the 1-based index. Invalid input -> default."""
    print(f"{prompt}:")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    raw = input(f"\nChoose (1-{len(options)}, default {default}): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return int(raw)
    return default


def ask_int(prompt, default=None, min_value=None, max_value=None):
    suffix = f" (default {default})" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            print("⚠  Enter a whole number.")
            continue
        if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
            print(f"⚠  Value out of range ({min_value}-{max_value}).")
            continue
        return value


def ask_float(prompt, default=None, min_value=None):
    suffix = f" (default {default})" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            value = float(raw)
        except ValueError:
            print("⚠  Enter a number.")
            continue
        if min_value is not None and value <= min_value:
            print(f"⚠  Value must be greater than {min_value}.")
            continue
        return value


def ask_text(prompt, default=""):
    suffix = f" (default: {default})" if default else ""
    return input(f"{prompt}{suffix}: ").strip() or default


def ask_yes_no(prompt, default=True):
    hint = "Y/n" if default else "y/N"
    raw = input(f"{prompt} ({hint}): ").strip().lower()
    if raw == "":
        return default
    return raw in ("y", "yes", "s", "si")


# ----------------------------------------------------------------- ffmpeg

def run_ffmpeg(cmd, name):
    """Run an ffmpeg command; on failure print only the relevant stderr
    lines. Returns True on success."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ ffmpeg error on {name}:")
        if result.stderr:
            lines = result.stderr.strip().split("\n")
            relevant = [l for l in lines if any(k in l.lower() for k in ("error", "invalid", "failed"))]
            for line in (relevant[-5:] if relevant else lines[-3:]):
                print(f"    {line}")
        return False
    return True

import os
import sys
import ctypes
from pathlib import Path
from datetime import datetime
import shutil

# Hosts file path
HOSTS_FILE = Path("C:/Windows/System32/drivers/etc/hosts")

# Backup directory (relative to script)
script_dir = Path(__file__).parent.resolve()

def load_env(env_path):
    """Parse a .env file and return a dict (no external dependencies)."""
    env = {}
    if env_path.exists():
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env[key.strip()] = value.strip()
    return env

ENV = load_env(script_dir / ".env")

def load_presets():
    """Read HOSTS_ADD_PRESET_N=ip|label lines from ENV and return an ordered list of (ip, label)."""
    presets = []
    i = 1
    while True:
        value = ENV.get(f'HOSTS_ADD_PRESET_{i}')
        if value is None:
            break
        parts = value.split('|', 1)
        ip = parts[0].strip()
        label = parts[1].strip() if len(parts) > 1 else ip
        if ip:
            presets.append((ip, label))
        i += 1
    return presets

PRESETS = load_presets()

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with administrator privileges."""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join([f'"{arg}"' for arg in sys.argv]), 
            None, 
            1
        )
    except:
        print("⚠  Could not obtain administrator privileges.")
        input("\nPress ENTER to exit...")
        sys.exit(1)

def read_hosts_file():
    """Read the contents of the hosts file."""
    try:
        with open(HOSTS_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"✗ Error reading hosts file: {e}")
        return None

def write_hosts_file(content):
    """Write content to the hosts file."""
    try:
        with open(HOSTS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"✗ Error writing hosts file: {e}")
        return False

def backup_hosts_file():
    """Create a backup of the hosts file."""
    try:
        backup_file = script_dir / "hosts.txt"
        shutil.copy2(HOSTS_FILE, backup_file)
        print(f"✓ Backup saved: {backup_file}")
        return True
    except Exception as e:
        print(f"⚠  Backup error: {e}")
        return False

def add_host_entry(ip, hostname):
    """Add a new entry to the hosts file."""
    content = read_hosts_file()
    if content is None:
        return False

    new_entry = f"{ip} {hostname}"

    # Check if hostname already exists
    lines = content.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and not line_stripped.startswith('#'):
            parts = line_stripped.split()
            if len(parts) >= 2 and parts[1] == hostname:
                print(f"\n⚠  Hostname '{hostname}' already exists in the hosts file:")
                print(f"    {line_stripped}")

                overwrite = input("\nOverwrite? (y/n, default n): ").strip().lower()
                if overwrite != 'y':
                    print("Operation cancelled.")
                    return False

                content = '\n'.join([l for l in lines if not (l.strip() and hostname in l)])
                break

    if not content.endswith('\n'):
        content += '\n'
    content += new_entry + '\n'

    if write_hosts_file(content):
        print(f"\n✓ Entry added successfully!")
        print(f"  {new_entry}")
        print("\nCreating backup...")
        backup_hosts_file()
        return True

    return False

def add_new_host():
    """Interactive prompt to add a new host entry."""
    print("\nChoose IP address:")
    print("1. 127.0.0.1   (localhost)")
    for i, (ip, label) in enumerate(PRESETS, start=2):
        print(f"{i}. {ip:<14} ({label})")
    custom_n = len(PRESETS) + 2
    print(f"{custom_n}. Custom        (enter manually)")

    prompt = f"\nChoose (1-{custom_n}, default 1): "
    ip_choice = input(prompt).strip()

    try:
        choice_n = int(ip_choice)
    except ValueError:
        choice_n = 1

    if 2 <= choice_n <= len(PRESETS) + 1:
        ip_address = PRESETS[choice_n - 2][0]
    elif choice_n == custom_n:
        ip_address = input("Enter IP address: ").strip()
        if not ip_address:
            print("⚠  Invalid IP.")
            return
    else:
        ip_address = "127.0.0.1"

    hostname = input("\nEnter hostname (e.g. example.test): ").strip()

    if not hostname:
        print("⚠  Invalid hostname.")
        return

    print(f"\nAbout to add:")
    print(f"  IP:       {ip_address}")
    print(f"  Hostname: {hostname}")

    confirm = input("\nConfirm? (y/n, default y): ").strip().lower()
    if confirm == 'n':
        print("Operation cancelled.")
        return

    if add_host_entry(ip_address, hostname):
        print("\n" + "=" * 60)
        print("Host added successfully!")
        print("=" * 60)
    else:
        print("\n✗ Operation failed.")

def main():
    print("\n" + "=" * 60)
    print("VIRTUAL HOSTS MANAGER")
    print("=" * 60)

    if not is_admin():
        print("\n⚠  This script requires administrator privileges.")
        print("Restarting with elevated privileges...\n")
        run_as_admin()
        sys.exit(0)

    print("\nAdministrator privileges: ✓")
    print(f"Hosts file: {HOSTS_FILE}")
    print(f"Backup:     {script_dir / 'hosts.txt'}\n")

    while True:
        add_new_host()

        print()
        another = input("Add another host? (y/n, default y): ").strip().lower()
        if another == 'n':
            break

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    input("\nPress ENTER to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        input("\nPress ENTER to exit...")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        input("\nPress ENTER to exit...")


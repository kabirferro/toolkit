#!/usr/bin/env python3
"""
Recursively scans a root directory and reports Git repositories that are not aligned:
  - uncommitted changes / untracked files
  - local commits not yet pushed to remote
  - remote commits not yet pulled (requires --fetch)

Usage:
  python git-check.py <workdir>                    # local check only
  python git-check.py <workdir> --fetch            # also check remote
  python git-check.py <workdir> --fetch --depth 3  # deeper search
"""

import subprocess
import argparse
from pathlib import Path


def run(cmd, cwd):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30
    )
    return result.stdout.decode('utf-8', errors='replace').strip(), \
           result.stderr.decode('utf-8', errors='replace').strip(), \
           result.returncode


def find_git_repos(root, max_depth=2):
    """Find directories containing .git up to max_depth levels below root."""
    repos = []
    root = Path(root).resolve()

    def _walk(path, depth):
        if depth > max_depth:
            return
        try:
            entries = list(path.iterdir())
        except PermissionError:
            return
        if (path / '.git').exists():
            repos.append(path)
            return  # do not recurse inside the repo itself
        for entry in entries:
            if entry.is_dir() and not entry.name.startswith('.'):
                _walk(entry, depth + 1)

    _walk(root, 0)
    return sorted(repos)


def check_repo(repo_path, do_fetch=False):
    issues = []

    # 1. Optional fetch
    if do_fetch:
        _, err, rc = run(['git', 'fetch', '--quiet'], repo_path)
        if rc != 0:
            issues.append(f'  [!] git fetch failed: {err}')

    # 2. Current branch and tracking info
    branch_out, _, _ = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], repo_path)
    branch = branch_out or 'HEAD detached'

    # 3. Local changes (staged, unstaged, untracked)
    porcelain, _, _ = run(['git', 'status', '--porcelain'], repo_path)
    if porcelain:
        lines = porcelain.splitlines()
        staged    = sum(1 for l in lines if l[0] not in (' ', '?', '!'))
        unstaged  = sum(1 for l in lines if l[1] not in (' ', '?', '!'))
        untracked = sum(1 for l in lines if l[:2] == '??')
        parts = []
        if staged:    parts.append(f'{staged} staged')
        if unstaged:  parts.append(f'{unstaged} unstaged')
        if untracked: parts.append(f'{untracked} untracked')
        issues.append(f'  [M] Local changes: {", ".join(parts)}')

    # 4. Commits to push
    ahead, _, rc_ahead = run(['git', 'log', '@{u}..HEAD', '--oneline'], repo_path)
    if rc_ahead == 0 and ahead:
        count = len(ahead.splitlines())
        issues.append(f'  [↑] {count} commit(s) to push ({branch})')

    # 5. Commits to pull (only if fetch was performed)
    if do_fetch:
        behind, _, rc_behind = run(['git', 'log', 'HEAD..@{u}', '--oneline'], repo_path)
        if rc_behind == 0 and behind:
            count = len(behind.splitlines())
            issues.append(f'  [↓] {count} remote commit(s) to pull ({branch})')

    # 6. No remote configured
    if rc_ahead != 0:
        issues.append(f'  [-] No remote / tracking branch configured ({branch})')

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Recursively find Git repositories and report unaligned ones.'
    )
    parser.add_argument('workdir', help='Root directory to scan recursively')
    parser.add_argument('--fetch', action='store_true', help='Run git fetch on each repo before checking (slower)')
    parser.add_argument('--depth', type=int, default=2, help='Max directory depth to search (default: 2)')
    args = parser.parse_args()

    root = Path(args.workdir).resolve()
    if not root.is_dir():
        print(f'Error: directory "{root}" not found.')
        raise SystemExit(1)

    print(f'Scanning: {root}')
    if args.fetch:
        print('Mode: with git fetch (may be slow)\n')
    else:
        print('Mode: local only (use --fetch to also check remote)\n')

    repos = find_git_repos(root, max_depth=args.depth)
    if not repos:
        print('No Git repositories found.')
        return

    print(f'Repositories found: {len(repos)}\n')
    print('=' * 60)
    not_aligned = []

    for repo in repos:
        rel = repo.relative_to(root.resolve()) if root.resolve() != repo else repo
        issues = check_repo(repo, do_fetch=args.fetch)
        if issues:
            not_aligned.append((rel, issues))

    if not not_aligned:
        print('All repositories are aligned.')
    else:
        print(f'Unaligned repositories: {len(not_aligned)}\n')
        for rel, issues in not_aligned:
            print(f'  {rel}')
            for issue in issues:
                print(issue)
            print()

    print('=' * 60)
    print(f'Total: {len(not_aligned)}/{len(repos)} unaligned.')


if __name__ == '__main__':
    main()

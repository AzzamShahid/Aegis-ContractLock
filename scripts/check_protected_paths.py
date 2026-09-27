from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath


PROTECTED_EXACT = {
    "aegis_contract.yaml",
    "verify_submission.ps1",
    "security_preflight.ps1",
    "scripts/check_protected_paths.py",
    ".github/workflows/aegis-pr-gate.yml",
    ".github/workflows/aegis-protected-boundary.yml",
}

PROTECTED_PREFIXES = (
    "baseline/",
    "legacy_app/",
    "aegis/",
    "tests/",
)


def git_changed_files(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        PurePosixPath(line.strip()).as_posix()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def is_protected(path: str) -> bool:
    return path in PROTECTED_EXACT or any(
        path == prefix.rstrip("/") or path.startswith(prefix)
        for prefix in PROTECTED_PREFIXES
    )


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: check_protected_paths.py <base_sha> <head_sha>")
        return 2

    base, head = sys.argv[1], sys.argv[2]
    changed = git_changed_files(base, head)
    protected = sorted(path for path in changed if is_protected(path))

    print("Aegis ContractLock — Protected Acceptance Boundary")
    print(f"Base: {base}")
    print(f"Head: {head}")
    print()

    if protected:
        print("BLOCKED — protected acceptance-boundary files changed:")
        for path in protected:
            print(f"  - {path}")
        print()
        print("The candidate may change. The acceptance boundary may not.")
        return 1

    print("PASS — no protected acceptance-boundary files changed.")
    print()
    print("The candidate may change. The acceptance boundary may not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

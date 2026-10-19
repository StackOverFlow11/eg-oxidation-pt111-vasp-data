#!/usr/bin/env python3
"""Rebuild a job's POTCAR from a licensed local potpaw library and verify it.

Usage:
    python fetch/make_potcar.py <job_id> /path/to/potpaw_PBE

<job_id> is the path relative to the repository root, e.g.
production/_ch2ohcoo_p_h/0.4V/fine_opt
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    job_id = sys.argv[1].strip("/")
    potpaw = Path(sys.argv[2])
    manifest = ROOT / "manifest" / "potcar.csv"
    with manifest.open() as fh:
        rows = list(csv.DictReader(fh))
    row = next((r for r in rows if r["job_id"] == job_id), None)
    if row is None:
        print(f"job not found in manifest/potcar.csv: {job_id}", file=sys.stderr)
        return 1

    elements = row["elements"].split()
    chunks = []
    for element in elements:
        path = potpaw / element / "POTCAR"
        if not path.is_file():
            print(f"missing POTCAR for element {element}: {path}", file=sys.stderr)
            return 1
        chunks.append(path.read_bytes())
    data = b"".join(chunks)
    job_dir = ROOT / job_id
    if not job_dir.is_dir():
        print(f"job directory not found: {job_dir}", file=sys.stderr)
        return 1
    (job_dir / "POTCAR").write_bytes(data)

    actual = hashlib.sha256(data).hexdigest()
    expected = row["sha256"]
    if actual != expected:
        print(
            f"checksum mismatch for {job_id}\n  expected {expected}\n  actual   {actual}",
            file=sys.stderr,
        )
        return 1

    sha_file = job_dir / "POTCAR.sha256"
    if sha_file.is_file():
        recorded = sha_file.read_text().split()[0]
        if recorded != expected:
            print(
                f"POTCAR.sha256 in {job_id} does not match manifest",
                file=sys.stderr,
            )
            return 1
    print(f"OK: rebuilt and verified {job_id}/POTCAR ({actual})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

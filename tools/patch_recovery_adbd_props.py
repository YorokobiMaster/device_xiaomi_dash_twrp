#!/usr/bin/env python3
"""Patch only the two adbd privilege properties in a recovery CPIO fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


NEWC_MAGICS = {b"070701", b"070702"}
LZ4_LEGACY_MAGIC = bytes.fromhex("02214c18")
PROPERTY_PATCHES = (
    (b"ro.secure=1", b"ro.secure=0", "ro.secure"),
    (b"ro.debuggable=0", b"ro.debuggable=1", "ro.debuggable"),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aligned(value: int, alignment: int = 4) -> int:
    return (value + alignment - 1) // alignment * alignment


def parse_newc(blob: bytes) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    offset = 0
    trailer_found = False
    while offset < len(blob):
        if offset + 110 > len(blob):
            raise RuntimeError(f"truncated newc header at {offset}")
        header = blob[offset : offset + 110]
        if header[:6] not in NEWC_MAGICS:
            raise RuntimeError(f"invalid newc magic at {offset}: {header[:6]!r}")
        try:
            fields = [int(header[index : index + 8], 16) for index in range(6, 110, 8)]
        except ValueError as error:
            raise RuntimeError(f"invalid newc numeric field at {offset}") from error
        (
            inode,
            mode,
            uid,
            gid,
            nlink,
            mtime,
            size,
            device_major,
            device_minor,
            rdevice_major,
            rdevice_minor,
            name_size,
            check,
        ) = fields
        name_start = offset + 110
        name_end = name_start + name_size
        if name_size < 1 or name_end > len(blob) or blob[name_end - 1] != 0:
            raise RuntimeError(f"invalid newc name at {offset}")
        name = blob[name_start : name_end - 1].decode("utf-8", errors="strict")
        data_start = aligned(name_end)
        data_end = data_start + size
        if data_end > len(blob):
            raise RuntimeError(f"truncated newc data for {name}")
        next_offset = aligned(data_end)
        entry = {
            "path": name,
            "type": stat.S_IFMT(mode),
            "mode": mode,
            "uid": uid,
            "gid": gid,
            "nlink": nlink,
            "mtime": mtime,
            "size": size,
            "device_major": device_major,
            "device_minor": device_minor,
            "rdevice_major": rdevice_major,
            "rdevice_minor": rdevice_minor,
            "check": check,
            "header_start": offset,
            "data_start": data_start,
            "data_end": data_end,
        }
        if name == "TRAILER!!!":
            if size != 0:
                raise RuntimeError("newc trailer contains data")
            trailer_found = True
            offset = next_offset
            break
        entries.append(entry)
        offset = next_offset
    if not trailer_found:
        raise RuntimeError("newc trailer not found")
    if any(byte != 0 for byte in blob[offset:]):
        raise RuntimeError("non-zero data follows aligned newc trailer")
    return entries


def decode_fragment(path: Path, lz4: Path) -> bytes:
    decoded = subprocess.run(
        [str(lz4), "-dc", "--", str(path)],
        capture_output=True,
        check=True,
    )
    return decoded.stdout


def count_exact_lines(data: bytes, wanted: bytes) -> list[int]:
    hits: list[int] = []
    cursor = 0
    for line in data.splitlines(keepends=True):
        if line.rstrip(b"\r\n") == wanted:
            hits.append(cursor)
        cursor += len(line)
    return hits


def patch_properties(cpio: bytes) -> tuple[bytes, dict[str, object]]:
    entries = parse_newc(cpio)
    targets = [entry for entry in entries if entry["path"] == "prop.default"]
    if len(targets) != 1:
        raise RuntimeError(f"expected exactly one prop.default entry, found {len(targets)}")
    entry = targets[0]
    if entry["type"] != stat.S_IFREG:
        raise RuntimeError("prop.default is not a regular file")

    data_start = int(entry["data_start"])
    data_end = int(entry["data_end"])
    before = cpio[data_start:data_end]
    output = bytearray(cpio)
    changed_properties: list[str] = []
    changed_offsets: list[int] = []
    for old_line, new_line, property_name in PROPERTY_PATCHES:
        hits = count_exact_lines(before, old_line)
        if len(hits) != 1:
            raise RuntimeError(
                f"expected exactly one {old_line.decode()} line, found {len(hits)}"
            )
        line_start = data_start + hits[0]
        output[line_start : line_start + len(old_line)] = new_line
        changed_properties.append(property_name)

    changed_offsets = [
        index for index, (old, new) in enumerate(zip(cpio, output)) if old != new
    ]
    if len(changed_offsets) != len(PROPERTY_PATCHES):
        raise RuntimeError(
            f"unexpected archive change count: {len(changed_offsets)} "
            f"(expected {len(PROPERTY_PATCHES)})"
        )

    after = bytes(output[data_start:data_end])
    for old_line, new_line, _ in PROPERTY_PATCHES:
        if count_exact_lines(after, old_line):
            raise RuntimeError(f"old property line survived: {old_line.decode()}")
        if len(count_exact_lines(after, new_line)) != 1:
            raise RuntimeError(f"new property line is not unique: {new_line.decode()}")

    report = {
        "entry": "prop.default",
        "entry_size": len(before),
        "entry_sha256_before": sha256_bytes(before),
        "entry_sha256_after": sha256_bytes(after),
        "changed_properties": changed_properties,
        "changed_byte_count": len(changed_offsets),
        "changed_offsets": changed_offsets,
        "preservation": "all decompressed CPIO bytes outside the two property value bytes are unchanged",
    }
    return bytes(output), report


def compress_fragment(cpio: bytes, output: Path, lz4: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        subprocess.run(
            [str(lz4), "-l", "-12", "--favor-decSpeed"],
            input=cpio,
            stdout=stream,
            check=True,
        )
    if output.read_bytes()[:4] != LZ4_LEGACY_MAGIC:
        raise RuntimeError("patched fragment is not legacy LZ4")
    tested = subprocess.run(
        [str(lz4), "-t", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    if tested.returncode != 0:
        raise RuntimeError(f"legacy LZ4 validation failed: {tested.stderr.strip()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-fragment", type=Path, required=True)
    parser.add_argument("--output-fragment", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--lz4", type=Path, default=Path("lz4"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input_fragment.is_file():
        raise RuntimeError(f"input fragment missing: {args.input_fragment}")
    if not args.lz4.is_file() and os.path.sep in str(args.lz4):
        raise RuntimeError(f"lz4 executable missing: {args.lz4}")
    if args.output_fragment.resolve() == args.input_fragment.resolve():
        raise RuntimeError("input and output fragments must be different")
    for path in (args.output_fragment, args.report):
        if os.path.lexists(path):
            raise RuntimeError(f"refusing to overwrite: {path}")

    input_cpio = decode_fragment(args.input_fragment, args.lz4)
    output_cpio, patch_report = patch_properties(input_cpio)
    compress_fragment(output_cpio, args.output_fragment, args.lz4)
    if decode_fragment(args.output_fragment, args.lz4) != output_cpio:
        raise RuntimeError("recompressed fragment does not decode to the patched CPIO")

    report = {
        "schema_version": 1,
        "status": "ADBD_RECOVERY_PROPS_PATCH_VALID",
        "input_fragment": {
            "path": str(args.input_fragment.resolve()),
            "size": args.input_fragment.stat().st_size,
            "sha256": sha256_file(args.input_fragment),
        },
        "output_fragment": {
            "path": str(args.output_fragment.resolve()),
            "size": args.output_fragment.stat().st_size,
            "sha256": sha256_file(args.output_fragment),
            "format": "legacy-lz4-level-12-favor-decSpeed",
        },
        "input_cpio": {
            "size": len(input_cpio),
            "sha256": sha256_bytes(input_cpio),
        },
        "output_cpio": {
            "size": len(output_cpio),
            "sha256": sha256_bytes(output_cpio),
        },
        "patch": patch_report,
        "write_approval": "NOT_GRANTED",
        "device_write_allowed": "NO",
        "warning": "Host-only staging candidate. No device write is approved.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(report["status"])
    print(f"changed_byte_count={patch_report['changed_byte_count']}")
    print(f"output_fragment_size={report['output_fragment']['size']}")
    print(f"output_fragment_sha256={report['output_fragment']['sha256']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)

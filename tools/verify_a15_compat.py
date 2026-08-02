#!/usr/bin/env python3
"""Verify the pinned, source-built dash A15 compatibility bridge."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


DEVICE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = DEVICE_ROOT.parents[2]
LOCK_PATH = DEVICE_ROOT / "prebuilt/a15-aidl/SOURCE_LOCK.json"

PROJECT_PATHS = {
    "platform/hardware/interfaces": "hardware/interfaces",
    "platform/system/tools/aidl": "system/tools/aidl",
    "platform/build/soong": "build/soong",
    "platform/build": "build/make",
    "platform/prebuilts/clang/host/linux-x86": "prebuilts/clang/host/linux-x86",
    "platform/frameworks/native": "frameworks/native",
}

AIDL_TREES = {
    "android.hardware.gatekeeper-V1":
        "hardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1",
    "android.hardware.security.keymint-V3":
        "hardware/interfaces/security/keymint/aidl/aidl_api/android.hardware.security.keymint/3",
    "android.hardware.security.secureclock-V1":
        "hardware/interfaces/security/secureclock/aidl/aidl_api/android.hardware.security.secureclock/1",
}

BUILT_LIBRARIES = {
    "android.hardware.security.secureclock-V1-ndk-twrp-a15-build":
        ("android.hardware.security.secureclock-V1-ndk-twrp-a15-build.so",
         "android.hardware.security.secureclock-V1-ndk.so"),
    "android.hardware.security.keymint-V3-ndk-twrp-a15":
        ("android.hardware.security.keymint-V3-ndk-twrp-a15.so",
         "android.hardware.security.keymint-V3-ndk.so"),
    "android.hardware.gatekeeper-V1-ndk-twrp-a15":
        ("android.hardware.gatekeeper-V1-ndk-twrp-a15.so",
         "android.hardware.gatekeeper-V1-ndk.so"),
    "lib_android_keymaster_keymint_utils-twrp-a15":
        ("lib_android_keymaster_keymint_utils-twrp-a15.so",
         "lib_android_keymaster_keymint_utils.so"),
    "libkeymint_support-twrp-a15":
        ("libkeymint_support-twrp-a15.so", "libkeymint_support.so"),
}


def git_head(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def aidl_tree_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for source in sorted(item for item in path.rglob("*") if item.is_file()):
        file_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        relative = source.relative_to(path).as_posix()
        digest.update(f"{file_digest}  {relative}\n".encode())
    return digest.hexdigest()


def dynamic_entries(path: Path, kind: str) -> set[str]:
    output = subprocess.run(
        ["readelf", "-d", str(path)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    marker = f"({kind})"
    return {
        line.split("[", 1)[1].split("]", 1)[0]
        for line in output.splitlines()
        if marker in line and "[" in line
    }


def exported_symbols(path: Path) -> set[str]:
    output = subprocess.run(
        ["readelf", "--dyn-syms", "--wide", str(path)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    symbols = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[3] in {"FUNC", "OBJECT"} and fields[6] != "UND":
            symbols.add(fields[7].split("@@", 1)[0])
    return symbols


def undefined_symbols(path: Path) -> set[str]:
    output = subprocess.run(
        ["readelf", "--dyn-syms", "--wide", str(path)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    symbols = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[6] == "UND":
            symbols.add(fields[7])
    return symbols


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-built",
        action="store_true",
        help="also validate staged recovery ELF outputs and their ABI",
    )
    args = parser.parse_args()
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    failures = []

    for project, expected in lock["build_toolchain"].items():
        actual = git_head(SOURCE_ROOT / PROJECT_PATHS[project])
        if actual != expected:
            failures.append(f"revision {project}: expected {expected}, got {actual}")

    for interface, relative in AIDL_TREES.items():
        actual = aidl_tree_sha256(SOURCE_ROOT / relative)
        expected = lock["frozen_aidl"][interface]["tree_sha256"]
        if actual != expected:
            failures.append(f"AIDL tree {interface}: expected {expected}, got {actual}")

    forbidden = list((DEVICE_ROOT / "prebuilt/a15-aidl").rglob("*.so"))
    if forbidden:
        failures.append(f"stock/prebuilt compatibility ELFs remain: {forbidden}")
    for old_generated_dir in (
        DEVICE_ROOT / "prebuilt/a15-aidl/include/gatekeeper",
        DEVICE_ROOT / "prebuilt/a15-aidl/include/keymint-v3",
    ):
        if old_generated_dir.exists() and any(item.is_file() for item in old_generated_dir.rglob("*")):
            failures.append(f"checked-in generated AIDL headers remain: {old_generated_dir}")

    if args.check_built:
        contract = lock["contract"]
        for module, (filename, baseline_filename) in BUILT_LIBRARIES.items():
            output = (SOURCE_ROOT / "out/target/product/dash/recovery/root/system/lib64" /
                      filename)
            if not output.is_file():
                failures.append(f"missing staged recovery output for {module}: {output}")
                continue
            sonames = dynamic_entries(output, "SONAME")
            if sonames != {filename}:
                failures.append(f"SONAME {filename}: got {sorted(sonames)}")
            needed = dynamic_entries(output, "NEEDED")
            if contract["forbidden_dependency"] in needed:
                failures.append(f"{filename} links forbidden KeyMint V4")
            android_36_binder = sorted(
                symbol for symbol in undefined_symbols(output)
                if "@LIBBINDER_NDK36" in symbol
            )
            if android_36_binder:
                failures.append(
                    f"{filename} requires Android 36 Binder symbols: {android_36_binder}"
                )
            required_path = (DEVICE_ROOT / "prebuilt/a15-aidl/abi" /
                             f"{baseline_filename}.required-symbols.txt")
            if required_path.is_file():
                required = set(required_path.read_text(encoding="utf-8").splitlines())
                missing = sorted(required - exported_symbols(output))
                if missing:
                    failures.append(f"{filename} lost {len(missing)} required symbols: {missing[:5]}")
        gatekeeper = (SOURCE_ROOT / "out/target/product/dash/recovery/root/system/lib64" /
                      "android.hardware.gatekeeper-V1-ndk-twrp-a15.so")
        if gatekeeper.is_file():
            needed = dynamic_entries(gatekeeper, "NEEDED")
            if contract["gatekeeper_must_link_keymint"] not in needed:
                failures.append("Gatekeeper V1 does not link the required KeyMint V3 SONAME")
        keymint = (SOURCE_ROOT / "out/target/product/dash/recovery/root/system/lib64" /
                   "android.hardware.security.keymint-V3-ndk-twrp-a15.so")
        if keymint.is_file():
            needed = dynamic_entries(keymint, "NEEDED")
            if contract["keymint_must_link_secureclock"] not in needed:
                failures.append("KeyMint V3 does not link the required SecureClock V1 SONAME")

    result = {
        "schema_version": 1,
        "status": "A15_COMPAT_VALID" if not failures else "A15_COMPAT_INVALID",
        "check_built": args.check_built,
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

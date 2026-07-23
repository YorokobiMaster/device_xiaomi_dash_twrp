#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "evidence" / "artifacts.json"
PREBUILT_HASHES = ROOT / "evidence" / "a15-prebuilts.sha256"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def result(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": passed, "detail": detail}


def main() -> int:
    checks = []
    manifest = json.loads(ARTIFACTS.read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        path = ROOT / artifact["destination"]
        exists = path.is_file()
        checks.append(result(f"exists:{artifact['destination']}", exists, str(path)))
        if not exists:
            continue
        checks.append(result(
            f"size:{artifact['destination']}",
            path.stat().st_size == artifact["size"],
            f"expected={artifact['size']} actual={path.stat().st_size}",
        ))
        actual_hash = sha256(path)
        checks.append(result(
            f"sha256:{artifact['destination']}",
            actual_hash == artifact["sha256"],
            f"expected={artifact['sha256']} actual={actual_hash}",
        ))

    expected_prebuilts = {}
    for line_number, line in enumerate(
            PREBUILT_HASHES.read_text(encoding="utf-8").splitlines(), start=1):
        fields = line.split()
        if len(fields) != 2 or len(fields[0]) != 64:
            checks.append(result(
                f"prebuilt-manifest:line:{line_number}",
                False,
                f"malformed line: {line}",
            ))
            continue
        digest, relative_path = fields
        if not relative_path.startswith("prebuilt/a15-aidl/"):
            checks.append(result(
                f"prebuilt-manifest:path:{line_number}",
                False,
                f"path outside compatibility tree: {relative_path}",
            ))
            continue
        expected_prebuilts[relative_path] = digest

    actual_prebuilts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "prebuilt" / "a15-aidl").rglob("*")
        if path.is_file()
    }
    checks.append(result(
        "prebuilt-manifest:complete",
        actual_prebuilts == set(expected_prebuilts),
        "missing="
        f"{sorted(set(expected_prebuilts) - actual_prebuilts)} "
        "unexpected="
        f"{sorted(actual_prebuilts - set(expected_prebuilts))}",
    ))
    for relative_path, expected_hash in sorted(expected_prebuilts.items()):
        path = ROOT / relative_path
        if not path.is_file():
            continue
        actual_hash = sha256(path)
        checks.append(result(
            f"prebuilt-sha256:{relative_path}",
            actual_hash == expected_hash,
            f"expected={expected_hash} actual={actual_hash}",
        ))

    extract_script = (ROOT / "extract-files.sh").read_text(encoding="utf-8")
    checks.append(result(
        "extract:stock-fstab-is-evidence-only",
        '"$DEVICE_ROOT/evidence/stock-recovery.fstab"' in extract_script
        and '"$DEVICE_ROOT/recovery.fstab"' not in extract_script,
        "stock extraction must not overwrite the recovery-specific fstab",
    ))

    board = (ROOT / "BoardConfig.mk").read_text(encoding="utf-8")
    required = [
        "BOARD_BOOT_HEADER_VERSION := 4",
        "BOARD_KERNEL_PAGESIZE := 4096",
        "BOARD_KERNEL_BASE := 0x00000000",
        "BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2",
        "BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true",
        "BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true",
        "BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864",
        "BOARD_RAMDISK_USE_LZ4 := true",
        "TW_INCLUDE_CRYPTO := true",
    ]
    for token in required:
        checks.append(result(f"board-required:{token}", token in board, token))

    forbidden = [
        "BOARD_RECOVERYIMAGE_PARTITION_SIZE :=",
        "BOARD_USES_RECOVERY_AS_BOOT := true",
        "BOARD_SUPER_PARTITION_SIZE :=",
        "TW_EXCLUDE_MTP := true",
        "TW_EXTRA_LANGUAGES := true",
    ]
    for token in forbidden:
        checks.append(result(f"board-forbidden:{token}", token not in board, token))

    fstab = (ROOT / "recovery.fstab").read_text(encoding="utf-8")
    rows = [line.split() for line in fstab.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    logical = {
        "system", "system_ext", "vendor", "product", "odm", "vendor_dlkm",
        "odm_dlkm", "system_dlkm", "mi_ext",
    }
    for name in sorted(logical):
        matching = [row for row in rows if row[0] == name]
        filesystems = {row[2] for row in matching if len(row) == 5}
        flags_ok = all(row[3] == "ro" and row[4] == "wait,slotselect,logical" for row in matching)
        checks.append(result(
            f"fstab:logical:{name}",
            len(matching) == 2 and filesystems == {"erofs", "ext4"} and flags_ok,
            f"rows={matching}",
        ))

    metadata = [row for row in rows if len(row) > 1 and row[1] == "/metadata"]
    checks.append(result(
        "fstab:metadata",
        len(metadata) == 1 and metadata[0][0] == "/dev/block/by-name/metadata" and metadata[0][2] == "f2fs",
        f"rows={metadata}",
    ))
    userdata = [row for row in rows if len(row) > 1 and row[1] == "/data"]
    userdata_flags = userdata[0][4].split(",") if len(userdata) == 1 and len(userdata[0]) == 5 else []
    required_userdata_flags = {
        "fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized",
        "keydirectory=/metadata/vold/metadata_encryption",
        "storage",
        "settingsstorage",
        "userdataencryptbackup",
    }
    checks.append(result(
        "fstab:userdata",
        len(userdata) == 1
        and userdata[0][0] == "/dev/block/by-name/userdata"
        and userdata[0][2] == "f2fs"
        and required_userdata_flags.issubset(userdata_flags),
        f"rows={userdata}",
    ))

    cache = [row for row in rows if len(row) > 1 and row[1] == "/cache"]
    checks.append(result(
        "fstab:cache-rescue",
        len(cache) == 1
        and cache[0][0] == "/dev/block/by-name/rescue"
        and cache[0][2] == "ext4"
        and cache[0][4] == "wait,check,formattable",
        f"rows={cache}",
    ))

    external = [row for row in rows if row[0].startswith("/devices/")]
    checks.append(result(
        "fstab:single-usb-otg",
        len(external) == 1
        and external[0][0] == "/devices/platform/soc/16701000.usb0/16700000.xhci*"
        and "storagename=USB-OTG" in external[0][4].split(","),
        f"rows={external}",
    ))

    allowed_by_name = {
        "metadata", "userdata", "rescue", "misc", "boot", "init_boot",
        "vendor_boot", "dtbo", "vbmeta", "vbmeta_system", "vbmeta_vendor",
    }
    by_name = {row[0].rsplit("/", 1)[-1] for row in rows if row[0].startswith("/dev/block/by-name/")}
    checks.append(result("fstab:by-name-allowlist", by_name == allowed_by_name, f"partitions={sorted(by_name)}"))
    for name in ("vbmeta", "vbmeta_system", "vbmeta_vendor"):
        matching = [row for row in rows if len(row) == 5 and row[1] == f"/{name}"]
        checks.append(result(
            f"fstab:slotselect:{name}",
            len(matching) == 1
            and matching[0][0] == f"/dev/block/by-name/{name}"
            and matching[0][4] == "slotselect",
            f"rows={matching}",
        ))

    stock_fstab = (ROOT / "evidence" / "stock-recovery.fstab").read_text(encoding="utf-8")
    stock_rows = [
        line.split() for line in stock_fstab.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    stock_logical = {
        row[0] for row in stock_rows
        if len(row) == 5 and "logical" in row[4].split(",")
    }
    actual_logical = {
        row[0] for row in rows
        if len(row) == 5 and "logical" in row[4].split(",")
    }
    checks.append(result(
        "fstab:logical-set-matches-stock",
        actual_logical == stock_logical,
        f"expected={sorted(stock_logical)} actual={sorted(actual_logical)}",
    ))

    forbidden_fstab = [" avb", "overlay ", "by-name/lk"]
    for token in forbidden_fstab:
        checks.append(result(f"fstab:forbidden:{token}", token not in fstab, token))

    usb_rc = (ROOT / "rootdir" / "init.recovery.mt6991.rc").read_text(encoding="utf-8")
    checks.append(result("usb:configfs", "setprop sys.usb.configfs 1" in usb_rc, "stock configfs property"))
    checks.append(result("usb:controller", "16701000.usb0" in usb_rc, "stock MT6991 controller"))

    passed = all(check["passed"] for check in checks)
    output = {
        "schema_version": 1,
        "status": "TREE_STATIC_VALID" if passed else "TREE_STATIC_INVALID",
        "checks": checks,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

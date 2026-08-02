#!/usr/bin/env python3
import hashlib
import json
import shlex
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "evidence" / "artifacts.json"
PREBUILT_HASHES = ROOT / "evidence" / "a15-prebuilts.sha256"
DASH_LOGICAL_PARTITIONS = {
    "mi_ext",
    "odm",
    "odm_dlkm",
    "product",
    "system",
    "system_dlkm",
    "system_ext",
    "vendor",
    "vendor_dlkm",
}


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
    for artifact in manifest["local_inputs"]:
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
        "extract:dtb-is-local-input",
        '"$DEVICE_ROOT/local-inputs/dash-stock.dtb"' in extract_script
        and '"$DEVICE_ROOT/prebuilt/dash-stock.dtb"' not in extract_script,
        "the verified stock DTB must be written only to the ignored local-input directory",
    ))
    checks.append(result(
        "extract:stock-configs-not-copied",
        "stock-recovery.fstab" not in extract_script
        and "stock/trees/recovery/init.recovery.mt6991.rc" not in extract_script
        and '"$DEVICE_ROOT/recovery.fstab"' not in extract_script,
        "stock configuration files must not be copied into the source tree",
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
        "TW_NO_REBOOT_FASTBOOT := true",
        "RECOVERY_SDCARD_ON_DATA := true",
        'TW_INTERNAL_STORAGE_MOUNT_POINT := "/data/media/0"',
        "ALLOW_MISSING_DEPENDENCIES := true",
    ]
    for token in required:
        checks.append(result(
            f"board-required:{token}",
            any(line.strip() == token for line in board.splitlines()),
            token,
        ))

    forbidden = [
        "BOARD_RECOVERYIMAGE_PARTITION_SIZE :=",
        "BOARD_USES_RECOVERY_AS_BOOT := true",
        "BOARD_SUPER_PARTITION_SIZE :=",
        "TW_EXCLUDE_MTP := true",
        "TW_EXTRA_LANGUAGES := true",
        "DASH_TWRP16_BOOTSTRAP_NO_CRYPTO",
    ]
    for token in forbidden:
        checks.append(result(f"board-forbidden:{token}", token not in board, token))

    fstab = (ROOT / "recovery.fstab").read_text(encoding="utf-8")
    rows = [
        shlex.split(line, comments=False, posix=True)
        for line in fstab.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
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
    cache_flags = cache[0][4].split(",") if len(cache) == 1 and len(cache[0]) == 5 else []
    required_cache_flags = {
        "wait",
        "check",
        "formattable",
        "wipeduringfactoryreset=0",
        "display=Cache (Rescue)",
    }
    checks.append(result(
        "fstab:cache-rescue",
        len(cache) == 1
        and cache[0][0] == "/dev/block/by-name/rescue"
        and cache[0][2] == "ext4"
        and required_cache_flags.issubset(cache_flags),
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

    actual_logical = {
        row[0] for row in rows
        if len(row) == 5 and "logical" in row[4].split(",")
    }
    checks.append(result(
        "fstab:logical-set-matches-device-baseline",
        actual_logical == DASH_LOGICAL_PARTITIONS,
        f"expected={sorted(DASH_LOGICAL_PARTITIONS)} actual={sorted(actual_logical)}",
    ))

    forbidden_fstab = [" avb", "overlay ", "by-name/lk"]
    for token in forbidden_fstab:
        checks.append(result(f"fstab:forbidden:{token}", token not in fstab, token))

    usb_rc = (ROOT / "rootdir" / "init.recovery.mt6991.rc").read_text(encoding="utf-8")
    project_rc = (ROOT / "rootdir" / "init.recovery.project.rc").read_text(encoding="utf-8")
    checks.append(result("usb:configfs", "setprop sys.usb.configfs 1" in project_rc, "configfs property"))
    checks.append(result("usb:controller", "16701000.usb0" in project_rc, "observed MT6991 controller"))
    checks.append(result(
        "storage:direct-path",
        "export EXTERNAL_STORAGE /data/media/0" in project_rc
        and "rmdir /sdcard" in project_rc,
        "dash removes the generic /sdcard directory and exports direct storage",
    ))

    source_root = ROOT.parents[2]
    for theme_name in ("portrait.xml", "landscape.xml", "watch.xml"):
        theme = source_root / "bootable" / "recovery" / "gui" / "theme" / "common" / theme_name
        theme_text = theme.read_text(encoding="utf-8")
        checks.append(result(
            f"theme:{theme_name}:direct-storage-defaults",
            'default="/sdcard"' not in theme_text
            and "tw_zip_location=/sdcard" not in theme_text
            and "tw_filecheck=/sdcard" not in theme_text,
            "theme file selectors must start at /data/media/0",
        ))

    project_required = [
        "setprop sys.usb.config adb",
        "service dash-touch-bridge /system/bin/touch_report_debug",
        "setenv LD_LIBRARY_PATH /odm/lib64:/system/lib64",
        "insmod /lib/modules/xiaomi_touch_dash.ko",
        "insmod /lib/modules/nt38771_touch_dash.ko",
        "wait /dev/xiaomi-touch 10",
        "start dash-touch-bridge",
        "service tee-supplicant /vendor/bin/tee-supplicant",
        "service vendor.keymint-mitee /vendor/bin/hw/android.hardware.security.keymint@3.0-service.mitee",
        "service vendor.gatekeeper_mitee /vendor/bin/hw/android.hardware.gatekeeper-service.mitee",
        "on property:fstab.additional=1",
        "start tee-supplicant",
        "on property:init.svc.tee-ready-delay=stopped",
        "start vendor.keymint-mitee",
        "start vendor.gatekeeper_mitee",
    ]
    checks.append(result(
        "project-init:imported",
        "import /init.recovery.project.rc" in usb_rc,
        "MT6991 init imports the project hook",
    ))
    direct_vendor_mounts = (
        "/dev/block/mapper/vendor_a /vendor",
        "/dev/block/mapper/vendor_b /vendor",
    )
    checks.append(result(
        "project-init:vendor-mount-is-slot-neutral",
        all(token not in project_rc for token in direct_vendor_mounts),
        "recovery.fstab slotselect must own the /vendor mount",
    ))
    for token in project_required:
        checks.append(result(
            f"project-init:required:{token}",
            token in project_rc,
            token,
        ))
    bridge_block = project_rc.split(
        "service dash-touch-bridge /system/bin/touch_report_debug", 1
    )[1].split("# Load the device-exact", 1)[0]
    checks.append(result(
        "project-init:bridge-is-retryable",
        "    oneshot\n" not in bridge_block
        and "on boot\n    wait /dev/xiaomi-touch 10" in project_rc,
        "bridge must wait for its device node and remain restartable",
    ))
    common_touch = project_rc.find("insmod /lib/modules/xiaomi_touch_dash.ko")
    panel_touch = project_rc.find("insmod /lib/modules/nt38771_touch_dash.ko")
    checks.append(result(
        "project-init:touch-module-order",
        common_touch >= 0 and panel_touch > common_touch,
        "xiaomi_touch_dash.ko must load before nt38771_touch_dash.ko",
    ))

    android_mk = (ROOT / "Android.mk").read_text(encoding="utf-8")
    device_mk = (ROOT / "device.mk").read_text(encoding="utf-8")
    checks.append(result(
        "project-init:built",
        "LOCAL_MODULE := init.recovery.project.rc" in android_mk
        and "LOCAL_SRC_FILES := rootdir/init.recovery.project.rc" in android_mk,
        "project hook has a root prebuilt module",
    ))
    checks.append(result(
        "project-init:packaged",
        "init.recovery.project.rc" in device_mk,
        "project hook is selected by the product",
    ))

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

# Unofficial TWRP for Redmi Turbo 5 Max

ENGLISH / [简体中文](README_CN.md)

This repository provides an unofficial TeamWin Recovery Project (TWRP) build for the Redmi Turbo 5 Max.

AI tools were used during development, but all architectural decisions, code reviews, device testing, regression analysis, integration work, and final quality decisions remain the maintainer's responsibility. No suggestion is included in a release without review and device testing.

## Device scope

This project supports only the following device:

- Product name: Redmi Turbo 5 Max
- Device codename: `dash`
- Platform: MediaTek MT6991
- SoC: MediaTek Dimensity 9500s
- Sales region: Mainland China

Poco X8 Pro Max is not currently covered by testing. Do not flash images from this project on that device.

On `dash`, recovery is stored in `vendor_boot`. The `m recovery` target updates the recovery contents, while `m vendorbootimage` generates `out/target/product/dash/vendor_boot.img`. That generated image is not the final flashable image; the required repacking procedure is described below.

### Known limitations

- MTP transfers larger than 4 GiB may cause the host PC to stop responding. Use `adb push` for files of this size and wait for the transfer to finish.
- USB-OTG requires libraries that do not fit within the available `recovery_ramdisk` space, so USB-OTG support is not currently planned.

## Differences from upstream TWRP

- **Internal storage**: Uses `/data/media/0` as the internal storage path and does not create a `/sdcard` compatibility path.

- **Root adb**: Current test images include root adb. The validated integration baseline provides the required recovery properties in `prop.default`; a normal `m recovery` build does not generate an equivalent root-adb fragment on its own.

- **SELinux**: Uses the stock sepolicy. Device logs show that recovery runs in permissive mode. This applies only to recovery and does not indicate the SELinux state of the Android system.

- **Format Data**: Uses Xiaomi's device-mapper handling. In the tested official full-OTA environment, Format Data works directly after installing an OTA package, without requiring another full wipe in Xiaomi recovery.

- **Cache (Rescue)**: Xiaomi maps `/cache` to the `/rescue` partition, so the interface labels it `Cache (Rescue)`. Factory Reset does not erase this partition, but Wipe Cache (Rescue) and Advanced Wipe can remove its data.

- **Upstream**: Includes fixes for upstream limitations and defects found during device bring-up.

## Design notes

### Android 15 vendor compatibility layer

TWRP 16 builds recovery with the Android 16 toolchain, while this device's vendor and odm components come from Android 15.

`prebuilt/a15-aidl` contains pinned Android 15 headers and source files. The build system uses them to generate the required compatibility libraries. It does not contain compatibility ELF files taken from Xiaomi's stock recovery.

`SOURCE_LOCK.json` records the AOSP source revisions and toolchain versions used for these compatibility sources.

The Android 16 AIDL generator references an optional Binder transaction-name API that is not available in the Android 15 Binder runtime. This project provides a narrowly scoped compatibility function that ignores only the optional transaction-name mapping.

### FBE decryption

The current decryption path uses the stock Android 15 KeyMint and Gatekeeper services. Recovery loads these services and their dependencies from vendor and odm.

`TW_KEEP_VENDOR_MOUNTED` and `TW_KEEP_ODM_MOUNTED` keep the required partitions available. Recovery does not relink the stock vendor binaries.

Weaver may be involved in some credential flows, but the current recovery does not start it automatically. This avoids invoking unreviewed TEE, eSE, or APDU code paths during startup.

The decryption code reads the keystore2 schema version from the `version` table using the following query:

```sql
SELECT version FROM version WHERE id=0;
```

Do not use `PRAGMA user_version`. Keystore2 attaches the database file to an in-memory database, and the two databases report different version values.

Recovery first copies the stock SQLite database to `/tmp`, after which `SqliteSnapshot` opens the copy in read-only mode.

### Touch input

Touch input uses the following `vendor_dlkm` modules:

- `xiaomi_touch_dash.ko`
- `nt38771_touch_dash.ko`

Recovery init loads these modules in a fixed order.

Xiaomi's touch reporting also depends on the `touch_report_debug` host-touch loop, which is managed by the `dash-touch-bridge` init service. The service uses `/odm/lib64:/system/lib64` as its `LD_LIBRARY_PATH`.

This design avoids starting the full Android Binder HAL in recovery.

## Source composition

`local_manifest.xml` replaces the following projects with personal forks:

- [bootable/recovery](https://github.com/YorokobiMaster/android_bootable_recovery)
- [system/core](https://github.com/YorokobiMaster/android_system_core)
- [system/vold](https://github.com/YorokobiMaster/android_system_vold)
- [vendor/twrp](https://github.com/YorokobiMaster/android_vendor_twrp)

The manifest also syncs this repository to `device/xiaomi/dash` and adds the following repacking tool:

- [repack](https://github.com/YorokobiMaster/dash_vendor_boot_repack)

The `vendor/twrp` fork exports `TW_DASH_FS3002_HAPTICS` to Soong. Without this fork, the build does not enable the device-specific haptic backend.

The manifest tracks the `twrp-16.0` and `main` branches, both of which may change over time.

`prebuilt/a15-aidl/SOURCE_LOCK.json` pins only the Android 15 compatibility sources. It does not pin the entire Android source tree.

## Build recovery

Run the following commands from the root of the Android source tree. The examples below use `source-twrp16` as the source directory.

### 1. Sync the source

```sh
cd /path/to/source-twrp16
repo init -u https://github.com/TWRP-Test/platform_manifest_twrp_aosp -b twrp-16.0
mkdir -p .repo/local_manifests
curl -L -o .repo/local_manifests/dash.xml \
    https://raw.githubusercontent.com/YorokobiMaster/device_xiaomi_dash_twrp/twrp-16.0/local_manifest.xml
repo sync
```

### 2. Provide the stock DTB

Extract the stock `vendor_boot` from the official firmware for your device and prepare the following input file:

```text
/path/to/stock/vendor_boot/aosp_unpack/dtb
```

Run the extraction script:

```sh
DASH_STOCK_ROOT=/path/to/stock device/xiaomi/dash/extract-files.sh
```

The script verifies the DTB SHA-256 hash, then copies the DTB into the Git-ignored `local-inputs` directory.

### 3. Build

```sh
source build/envsetup.sh
lunch twrp_dash-bp2a-eng
m recovery vendorbootimage -j4
```

`m recovery` primarily updates the recovery binary. `vendorbootimage` also refreshes the staging directory used for the recovery ramdisk.

The device BoardConfig sets `BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true`, so final integration must use the updated staging directory produced by `vendorbootimage`.

### 4. Check the build output

```sh
python3 device/xiaomi/dash/evidence/verify_tree.py >/dev/null
python3 device/xiaomi/dash/tools/verify_a15_compat.py --check-built
cmp device/xiaomi/dash/recovery.fstab \
    out/target/product/dash/recovery/root/system/etc/recovery.fstab
test -x out/target/product/dash/recovery/root/system/bin/recovery
```

If any command fails, stop before repacking.

## Repack vendor_boot

### Integration baseline

Final repacking requires a minimal runtime tree that has already passed device testing. This document refers to that directory as `VALIDATED_RUNTIME_TREE`.

Do not use the stock type-2 recovery fragment as the runtime tree, because it usually does not contain `system/bin/recovery`.

Do not use an unfiltered full build staging directory either. Mixing shared libraries from different API generations can prevent recovery from starting at the linker stage.

This source repository does not distribute the stock-derived runtime tree. Do not continue unless you already have a suitable baseline that has been validated on the device.

### 1. Create a work directory

```sh
VALIDATED_RUNTIME_TREE=/path/to/validated-runtime-tree
test -x "$VALIDATED_RUNTIME_TREE/system/bin/recovery"

DASH_BUILD_WORK="$(mktemp -d)"
RUNTIME_TREE="$DASH_BUILD_WORK/runtime-tree"
REPLACEMENT_CPIO="$DASH_BUILD_WORK/dash-recovery.cpio"
REPLACEMENT_LZ4="$DASH_BUILD_WORK/dash-recovery.cpio.lz4"
FINAL_FRAGMENT="$REPLACEMENT_LZ4"

mkdir "$RUNTIME_TREE"
cp -a --reflink=auto "$VALIDATED_RUNTIME_TREE"/. "$RUNTIME_TREE"/
```

`mktemp` creates a fresh directory for this integration, so these commands do not overwrite previous output files.

### 2. Update the checked files

```sh
cp out/target/product/dash/recovery/root/system/bin/recovery \
    "$RUNTIME_TREE/system/bin/recovery"
cp out/target/product/dash/recovery/root/system/etc/recovery.fstab \
    "$RUNTIME_TREE/system/etc/recovery.fstab"
cp out/target/product/dash/recovery/root/twres/languages/en.xml \
    "$RUNTIME_TREE/twres/languages/en.xml"
cp out/target/product/dash/recovery/root/init.recovery.mt6991.rc \
    "$RUNTIME_TREE/init.recovery.mt6991.rc"
cp out/target/product/dash/recovery/root/init.recovery.project.rc \
    "$RUNTIME_TREE/init.recovery.project.rc"

for library in \
    android.hardware.gatekeeper-V1-ndk-twrp-a15.so \
    android.hardware.security.keymint-V3-ndk-twrp-a15.so \
    android.hardware.security.secureclock-V1-ndk-twrp-a15-build.so \
    lib_android_keymaster_keymint_utils-twrp-a15.so \
    libkeymint_support-twrp-a15.so; do
    cp "out/target/product/dash/recovery/root/system/lib64/$library" \
        "$RUNTIME_TREE/system/lib64/$library"
done
```

Do not use `rsync` to overwrite the entire runtime tree. Replace only the files explicitly checked for this integration.

Before updating theme files, verify the device-specific paths. The internal storage path must remain `/data/media/0`.

### 3. Create the recovery fragment

```sh
out/host/linux-x86/bin/mkbootfs \
    -d out/target/product/dash \
    "$RUNTIME_TREE" > "$REPLACEMENT_CPIO"
out/host/linux-x86/bin/lz4 \
    -l -12 --favor-decSpeed "$REPLACEMENT_CPIO" "$REPLACEMENT_LZ4"
```

### 4. Check the recovery fragment

```sh
CPIO_LIST="$DASH_BUILD_WORK/cpio-list.txt"
lz4 -dc "$FINAL_FRAGMENT" | cpio -t > "$CPIO_LIST"

grep -Fx 'system/bin/recovery' "$CPIO_LIST"
grep -Fx 'init.recovery.mt6991.rc' "$CPIO_LIST"
grep -Fx 'init.recovery.project.rc' "$CPIO_LIST"

for library in \
    android.hardware.gatekeeper-V1-ndk-twrp-a15.so \
    android.hardware.security.keymint-V3-ndk-twrp-a15.so \
    android.hardware.security.secureclock-V1-ndk-twrp-a15-build.so \
    lib_android_keymaster_keymint_utils-twrp-a15.so \
    libkeymint_support-twrp-a15.so; do
    grep -Fx "system/lib64/$library" "$CPIO_LIST"
done

lz4 -dc "$FINAL_FRAGMENT" | \
    cpio -i --to-stdout system/etc/recovery.fstab | \
    grep -F 'wipeduringfactoryreset=0' | \
    grep -F 'display="Cache (Rescue)"'

lz4 -dc "$FINAL_FRAGMENT" | cpio -i --to-stdout prop.default | \
    grep -Fx 'ro.secure=0'
lz4 -dc "$FINAL_FRAGMENT" | cpio -i --to-stdout prop.default | \
    grep -Fx 'ro.debuggable=1'
```

If any command fails, do not use the fragment.

### 5. Create the vendor_boot image

Provide the stock `vendor_boot` image and its corresponding vbmeta owner file from your official firmware. The `repack/inputs` directory is ignored by Git.

```sh
FINAL_IMAGE="$DASH_BUILD_WORK/dash-UNTESTED-vendor_boot.img"
REPACK_REPORT="$DASH_BUILD_WORK/repack-report.json"

repack/stock_aware_repack_tool \
    --template repack/inputs/dash-a15/stock-vendor_boot.img \
    --vbmeta-owner repack/inputs/dash-a15/template-local-vbmeta.img \
    --replacement "$FINAL_FRAGMENT" \
    --output "$FINAL_IMAGE" \
    --report "$REPACK_REPORT" \
    --budget-output "$DASH_BUILD_WORK/size-budget.json"

python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["status"] == "PACKAGING_VALID"' \
    "$REPACK_REPORT"
sha256sum "$FINAL_IMAGE"
```

The repacking tool replaces only the type-2 fragment named `recovery`. It preserves all non-target payloads and their entry metadata.

The tool recalculates the affected layout fields and AVB footer, and it verifies both the local AVB descriptor and the final image size.

Without a private key, the output image uses an algorithm-NONE footer. As a result, the top-level stock vbmeta descriptor no longer matches the modified image.

`UNTESTED` means that the image has passed host-side validation but has not yet been tested on a device. Only a successful device test should change that status.

## Flash

Check the current slot and set the path to the image:

```sh
fastboot getvar current-slot
FINAL_IMAGE=/path/to/dash-UNTESTED-vendor_boot.img
```

If the command returns `current-slot: a`, run:

```sh
fastboot flash vendor_boot_a "$FINAL_IMAGE"
```

If the command returns `current-slot: b`, run:

```sh
fastboot flash vendor_boot_b "$FINAL_IMAGE"
```

During bring-up, development builds were successfully flashed and booted from both `vendor_boot` slots.

Before flashing, keep a backup copy of the original `vendor_boot` image so that you can restore it if necessary.

## Distribution boundary for source and images

This source repository does not directly include Xiaomi vendor or system runtime components. It also does not include the stock DTB or complete stock configuration files; extract these inputs from the official firmware for your device.

`THIRD_PARTY_NOTICES.md` records the origin and Apache-2.0 license information for AOSP-derived files. The complete Apache-2.0 license text is available in `LICENSES/Apache-2.0.txt`.

## Acknowledgments

- [TeamWin Recovery Project](https://github.com/TeamWin/android_bootable_recovery)
- [TWRP-Test](https://github.com/TWRP-Test)
- Community members who reported issues and helped test changes
- Models used during development: GPT 5.6, Kimi K3, GLM 5.2, and Claude Opus 4.8

## Licenses

Each file is governed by the license declared in that file. Preserve all upstream copyright and license notices.

TWRP-derived files generally use GPL-3.0-or-later, while AOSP-derived files primarily use Apache-2.0.

Original project files use the license declared by the relevant file or repository. The repository root contains the full GPL-3.0-or-later text in `COPYING`.

## Disclaimer

This source repository is not affiliated with Xiaomi and does not represent Xiaomi or TeamWin.

The software is provided as-is, without any warranty. Users assume all risks associated with flashing, including device damage, data loss, and possible effects on warranty service.

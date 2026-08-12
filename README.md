# Unofficial TWRP for Redmi Turbo 5 Max

ENGLISH / [简体中文](README_CN.md)

This project provides an unofficial TWRP build for the Redmi Turbo 5 Max. AI tools were used during development. The maintainer remains responsible for architectural decisions, code review, device testing, regression analysis, integration, and final quality, and evaluates every change against results from physical-device testing. Suggestions that have not been reviewed and tested are not included in releases.

## Device scope

This project supports only the following device:

- Product name: Redmi Turbo 5 Max
- Device codename: `dash`
- Platform: MediaTek MT6991
- SoC: MediaTek Dimensity 9500s

Poco X8 Pro Max is outside the current test scope. Do not use images produced by this project on that device. ~~Unless you really want to.~~

### Working

- Touch input
- Decryption, including single-user and multi-user setups; tested on HyperOS and LineageOS 23.2
- Safe unmounting of `/vendor`
- Haptics
- Screenshots
- USB OTG

### Known issues / TODO

- The host PC may stop responding during MTP transfers larger than 4 GiB. Use `adb push` instead and wait patiently for the transfer to finish.

## Differences from upstream TWRP

- **Internal storage**: Uses `/data/media/0` as the internal storage path and does not create a `/sdcard` compatibility path.

- **Root adb**: Current test images include root adb. The validated integration baseline provides the required properties in the recovery fragment's `prop.default`. A normal `m recovery` command does not automatically produce an equivalent root-adb fragment.

- **SELinux**: Uses the stock sepolicy. Device logs show that recovery runs in permissive mode. This applies only to recovery and does not indicate the SELinux state of the Android system.

- **Format Data**: Uses Xiaomi's device-mapper handling. After installing an official full OTA package, Format Data can be used directly without returning to Xiaomi recovery to wipe data.

- **Cache (Rescue)**: Xiaomi maps `/cache` to the `/rescue` partition, so the interface explicitly labels it `Cache (Rescue)`, and Factory Reset no longer erases it. Wipe Cache (Rescue) and Advanced Wipe can still delete the data on this partition.

## Build recovery

Run the following commands from the root of the Android source tree. The example directory name is `source-twrp16`.

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

Extract the stock `vendor_boot.img` from your own official firmware.

```sh
mkdir -p device/xiaomi/dash/local-inputs
python3 system/tools/mkbootimg/unpack_bootimg.py \
    --boot_img /path/to/stock/vendor_boot.img \
    --out device/xiaomi/dash/local-inputs
```

### 3. Build

```sh
source build/envsetup.sh
lunch twrp_dash-bp2a-eng
m recovery vendorbootimage
```

`m recovery` primarily updates the recovery binary. `vendorbootimage` also refreshes the recovery ramdisk staging directory.

The device BoardConfig sets `BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true`. Final integration must therefore use the updated vendorboot staging directory.

### 4. Check the build output

```sh
cmp device/xiaomi/dash/recovery.fstab \
    out/target/product/dash/recovery/root/system/etc/recovery.fstab
test -x out/target/product/dash/recovery/root/system/bin/recovery
```

## Repack vendor_boot

[Repacking tool](https://github.com/YorokobiMaster/dash_twrp_repack)

## Flash

Check the current slot and set the image path:

```sh
fastboot getvar current-slot
FINAL_IMAGE=/path/to/vendor_boot.img
fastboot flash vendor_boot_<a|b> "$FINAL_IMAGE"
```

## Distribution boundary for source and images

This source repository does not directly include Xiaomi vendor or system runtime components, the stock DTB, or complete stock configuration files. Extract these inputs from official firmware that you own.

The source and Apache-2.0 license mapping for AOSP-derived files is provided in `THIRD_PARTY_NOTICES.md`. The complete Apache-2.0 license text is provided in `LICENSES/Apache-2.0.txt`.

## Credits

- [TeamWin Recovery Project](https://github.com/TeamWin/android_bootable_recovery)
- [TWRP-Test](https://github.com/TWRP-Test)
- Community members who reported issues and were willing to test fixes
- Models used during development: GPT 5.6, Kimi K3, GLM 5.2, and Claude Opus 4.8

## License

Each file is licensed under the terms declared by that file. Preserve copyright and license notices from upstream files.

TWRP-derived files generally use GPL-3.0-or-later. AOSP-derived files primarily use Apache-2.0.

Original project files use the license declared by the relevant file or repository. The repository-root `COPYING` file provides the GPL-3.0-or-later text.

## Disclaimer

This source repository is not affiliated with Xiaomi and does not represent Xiaomi or TeamWin.

The software is provided “as is,” without warranty of any kind. You assume all risks associated with flashing, device damage, data loss, and warranty or service implications.

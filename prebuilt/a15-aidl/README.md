# Android 15 KeyMint V3 compatibility bridge

This directory no longer contains shared-library binaries or checked-in AIDL
generator output. The five runtime libraries (four original compatibility
libraries plus their SecureClock dependency) are generated and compiled by
Soong from AOSP source.

`SOURCE_LOCK.json` records two layers:

- `android-15.0.0_r1` is the source/ABI baseline. The frozen Gatekeeper V1,
  KeyMint V3, and SecureClock V1 AIDL trees in the build checkout are
  byte-identical to this baseline.
- `build_toolchain` records the exact TWRP 16 checkout used to run AIDL, Clang,
  and Soong. Reproduction is fail-closed when one of these revisions differs.

The non-generated A15 headers and the five small AOSP implementation sources
are vendored so the compatibility intent is reviewable. Their per-file hashes
are recorded in `../../evidence/a15-prebuilts.sha256`.

## Rebuild and verify

From the Android source root:

```sh
python3 device/xiaomi/dash/tools/verify_a15_compat.py

source build/envsetup.sh
lunch twrp_dash-bp2a-eng
SOONG_GOMEMLIMIT=8GiB SOONG_GOGC=20 m recovery vendorbootimage -j4

python3 device/xiaomi/dash/tools/verify_a15_compat.py --check-built
python3 device/xiaomi/dash/evidence/verify_tree.py
```

The ELF check validates the exact recovery variants staged for the recovery
ramdisk. It enforces the project-specific compatibility SONAMEs, rejects any
KeyMint V4 dependency, requires Gatekeeper V1 to link KeyMint V3, and verifies
that the source-built libraries retain every exported symbol recorded from the
previously validated API-34 compatibility set.

## Refresh policy

Do not copy libraries or generated headers from a stock recovery. To update the
baseline, change `SOURCE_LOCK.json`, refresh the vendored AOSP source/header
files from the named projects, regenerate `evidence/a15-prebuilts.sha256`, build,
run the ELF ABI check, and complete an actual recovery decryption regression.

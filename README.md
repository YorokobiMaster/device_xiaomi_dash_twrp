# Xiaomi dash TWRP content tree

This is a size-gated, first bring-up tree for Redmi Turbo 5 Max (`dash`). It
builds TWRP recovery content as a header-v4 vendor ramdisk table fragment with
type `RECOVERY` and name `recovery`. The Android build's complete
`vendor_boot.img` is middleware only and is never a dash flashable artifact.

## Proven stock inputs

- Page size: 4096 bytes.
- Header version: 4.
- Vendor cmdline: `bootopt=64S3,32N2,64N2`.
- Vendor boot partition: 67108864 bytes.
- DTB: exact stock bytes recorded in `evidence/artifacts.json`.
- Stock recovery fstab is preserved verbatim under `evidence/`; the active
  recovery fstab is a TWRP-specific, statically checked derivation.
- MT6991 USB controller rc: exact stock bytes.

The Android 15 AIDL headers and shared libraries under `prebuilt/a15-aidl/`
form a link-only platform compatibility set. Every file is content-addressed
by `evidence/a15-prebuilts.sha256`, and `evidence/verify_tree.py` rejects a
missing, changed, or unexpected file. The exact Android 15 source revisions
and build command that generated this set must still be recorded before a
public source release.

Run `./extract-files.sh` from this directory to re-materialize and hash-check
the three stock-derived inputs. It does not overwrite the active derived
`recovery.fstab`. No phone access is used.

## Packaging constraints

Crypto and MTP are enabled. Extra languages, NTFS/exFAT and optional utilities
remain excluded to protect the recovery-fragment size budget. The stock
platform fragment, including its modules and MTK boot services, is preserved by
the stock-aware repacker and must not be duplicated in a flashable candidate.

The active fstab maps TWRP's `/cache` volume to Xiaomi's `rescue` partition.
Manual **Wipe Cache**, or an install workflow that requests an automatic cache
wipe, destroys MIUI rescue data and must not be presented as a harmless cleanup.

The expected build target on the pinned TWRP 16 root is:

```sh
source build/envsetup.sh
lunch twrp_dash-bp2a-eng
m recovery -j4
```

Keep this checkout's default `out/` directory dedicated to the BP2A target.
When checking another release, set a different `OUT_DIR` before `lunch`; mixing
release targets in one output directory invalidates the full Soong graph.
For the audited 6 GiB-RAM cgroup, a full graph regeneration succeeded with
`SOONG_GOMEMLIMIT=8GiB`, `SOONG_GOGC=20`, and a 10 GiB swap allowance.

Use `m vendorbootimage -j4` only to materialize and inspect the complete
recovery ramdisk. Its `vendor_boot.img` is build middleware and is not a dash
flashable image.

Only the generated type-2/name=`recovery` fragment may pass to the stock-aware
repacker. Until a separately approved device test succeeds, every final image
and report remains `UNTESTED` and `BOOTABILITY_NOT_TESTED`.

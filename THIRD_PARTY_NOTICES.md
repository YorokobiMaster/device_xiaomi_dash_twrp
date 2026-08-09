# Third-party notices

This repository is an aggregate. Files retain their own licenses; the presence
of a repository-level `COPYING` file does not replace upstream notices.

## Android Open Source Project — Apache License 2.0

The following material is derived from the Android Open Source Project and is
licensed under Apache-2.0. The complete license text is in
[`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt).

| Local material | Upstream project | Pinned source |
|---|---|---|
| Frozen Gatekeeper V1, KeyMint V3, and SecureClock V1 AIDL-generated build inputs | `platform/hardware/interfaces` | A15 source `android-15.0.0_r1` / `488942f82bd1bc9ad1cb65a02c71421dc3a6a3d6` |
| `prebuilt/a15-aidl/include/keymaster-ng/` and `prebuilt/a15-aidl/include/keymaster/` | `platform/system/keymaster` | `android-15.0.0_r1` / `8fecfe9ee2e46c3b7017be66cbdb4f080266e1c4` |
| `prebuilt/a15-aidl/include/keymint-support/` | `platform/hardware/interfaces` | `android-15.0.0_r1` / `488942f82bd1bc9ad1cb65a02c71421dc3a6a3d6` |
| `prebuilt/a15-aidl/src/` | `platform/system/keymaster` and `platform/hardware/interfaces` | same A15 revisions above |
| `rootdir/logd.recovery.rc` | `platform/system/logging`, `logd/logd.rc` | modified recovery-specific copy; retain AOSP copyright and Apache-2.0 terms |

`prebuilt/a15-aidl/include/keymaster/keymaster/key_blob_utils/ae.h` carries
its own explicit public-domain dedication rather than Apache-2.0.

The AIDL shared libraries are generated and compiled from source during the
Android build. Xiaomi stock-recovery copies of those libraries are not inputs.

## TeamWin Recovery Project and project-authored material

TWRP-derived and project-authored GPL-covered material is distributed under
GPL-3.0-or-later where identified by the applicable source file or project
documentation. See `COPYING`.

## Not covered by the AOSP notice

The AOSP notice above does not grant rights to the Xiaomi/MediaTek stock DTB.
That DTB is not tracked by this repository: a local build must extract its own
hash-verified copy into the ignored `local-inputs/` directory. The stock fstab
and init files used during bring-up are also not distributed.

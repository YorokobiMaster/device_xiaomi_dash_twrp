# Android 15 KeyMint V3 compatibility bridge

This directory contains the Android 15 headers and implementation sources used
by the KeyMint V3 compatibility libraries in `Android.bp`. Soong generates the
AIDL sources and builds the runtime libraries as part of the recovery build.

It does not contain shared libraries copied from Xiaomi's stock recovery or
checked-in AIDL generator output. See `../../THIRD_PARTY_NOTICES.md` for source
provenance and licensing information.

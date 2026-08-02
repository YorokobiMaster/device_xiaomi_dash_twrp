#!/usr/bin/env bash
set -euo pipefail

DEVICE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$DEVICE_ROOT/../../../..")"
STOCK_ROOT="${DASH_STOCK_ROOT:-$PROJECT_ROOT/stock}"

copy_verified() {
    local source_path="$1"
    local expected_sha256="$2"
    local destination_path="$3"
    local actual_sha256

    actual_sha256="$(sha256sum "$source_path" | awk '{print $1}')"
    if [[ "$actual_sha256" != "$expected_sha256" ]]; then
        printf 'hash mismatch: %s\nexpected: %s\nactual:   %s\n' \
            "$source_path" "$expected_sha256" "$actual_sha256" >&2
        return 1
    fi

    install -D -m 0644 "$source_path" "$destination_path"
    printf '%s  %s\n' "$actual_sha256" "$destination_path"
}

copy_verified \
    "$STOCK_ROOT/vendor_boot/aosp_unpack/dtb" \
    2636d5a861e909f5bf32fb3b5c80b25824fbb6591e31a21b6b1326b6dc52d7e3 \
    "$DEVICE_ROOT/local-inputs/dash-stock.dtb"

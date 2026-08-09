#!/usr/bin/env bash
set -euo pipefail

DEVICE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$DEVICE_ROOT/../../../..")"
STOCK_ROOT="${DASH_STOCK_ROOT:-$PROJECT_ROOT/stock}"
SOURCE_DTB="$STOCK_ROOT/vendor_boot/aosp_unpack/dtb"
DESTINATION_DTB="$DEVICE_ROOT/local-inputs/dash-stock.dtb"

install -D -m 0644 "$SOURCE_DTB" "$DESTINATION_DTB"
printf 'Copied %s to %s\n' "$SOURCE_DTB" "$DESTINATION_DTB"

DEVICE_PATH := device/xiaomi/dash

# Architecture: the stock recovery userspace and supplied platform fragment are arm64.
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := generic
TARGET_SUPPORTS_32_BIT_APPS := false
TARGET_SUPPORTS_64_BIT_APPS := true

TARGET_BOOTLOADER_BOARD_NAME := mt6991
TARGET_BOARD_PLATFORM := mt6991
TARGET_NO_BOOTLOADER := true
TARGET_NO_KERNEL := true

# The pinned recovery manifest intentionally omits test and host-tool dependency
# closures. Soong still parses their remaining Android.bp files; selected
# recovery modules must satisfy their dependencies when Ninja executes.
ALLOW_MISSING_DEPENDENCIES := true

# Stock dash vendor_boot v4 facts. The build output is content-only middleware.
BOARD_USES_GENERIC_KERNEL_IMAGE := true
BOARD_BOOT_HEADER_VERSION := 4
BOARD_KERNEL_BASE := 0x00000000
BOARD_KERNEL_PAGESIZE := 4096
BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2
BOARD_RAMDISK_USE_LZ4 := true
BOARD_INCLUDE_DTB_IN_BOOTIMG := true
BOARD_PREBUILT_DTBIMAGE_DIR := $(DEVICE_PATH)/prebuilt

BOARD_MKBOOTIMG_ARGS += --header_version 4
BOARD_MKBOOTIMG_ARGS += --kernel_offset 0x80000000
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset 0xa6f00000
BOARD_MKBOOTIMG_ARGS += --tags_offset 0x87c80000
BOARD_MKBOOTIMG_ARGS += --dtb_offset 0x87c80000
BOARD_MKBOOTIMG_ARGS += --board ""

# Recovery is a distinct type-2/name=recovery vendor ramdisk table entry.
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864
TARGET_NO_RECOVERY := true
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery.fstab

# No standalone recovery, recovery-as-boot, or unproven super size is defined.
BOARD_FLASH_BLOCK_SIZE := 262144
BOARD_HAS_LARGE_FILESYSTEM := true
BOARD_HAS_NO_SELECT_BUTTON := true
BOARD_SUPPRESS_SECURE_ERASE := true

# ADB, fastbootd, and the read-only FBE path are always part of release builds.
TW_THEME := portrait_hdpi
TW_BRIGHTNESS_PATH := "/sys/class/leds/lcd-backlight/brightness"
TW_MAX_BRIGHTNESS := 16383
TW_DEFAULT_BRIGHTNESS := 8192
TW_USE_NEW_MINADBD := true
TW_EXCLUDE_DEFAULT_USB_INIT := true
TW_INCLUDE_FASTBOOTD := true
TW_EXCLUDE_APEX := true
TW_INCLUDE_CRYPTO := true
TW_EXCLUDE_TZDATA := true
TW_EXCLUDE_NANO := true
TW_EXCLUDE_BASH := true
TW_EXCLUDE_ZIP := true
TW_EXCLUDE_LPDUMP := true
TW_EXCLUDE_LPTOOLS := true
TW_NO_EXFAT := true
TW_NO_EXFAT_FUSE := true
TW_NO_NETWORK := true
TW_NO_LEGACY_PROPS := true
TW_NO_BIND_SYSTEM := true
# The stock A15 TEE/KeyMint/Gatekeeper executables run directly from vendor.
# Keep its read-only mount alive after parsing the additional vendor fstab.
TW_KEEP_VENDOR_MOUNTED := true
# The stock Weaver binary links its Xiaomi AuthSecret AIDL interface from ODM.
TW_KEEP_ODM_MOUNTED := true
# TWRP maps metadata-encrypted userdata before user authentication. Tear that
# mapping down through TWRP's native dmctl path before formatting the raw block.
TW_USE_DMCTL := true
# Keep user-0 credential entry explicit; hardware throttling governs retries.
TW_SKIP_FBE_DEFAULT_PASSWORD := true

# RGB565 is the format proven by the v7-v9 runtime tests. Touch and the stock
# host bridge remain a separately audited recovery overlay.

DEVICE_PATH := device/xiaomi/dash

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota.mk)
$(call inherit-product, vendor/twrp/config/common.mk)

PRODUCT_SHIPPING_API_LEVEL := 36
PRODUCT_TARGET_VNDK_VERSION := 36

AB_OTA_UPDATER := true
ENABLE_VIRTUAL_AB := true
PRODUCT_USE_DYNAMIC_PARTITIONS := true

PRODUCT_PROPERTY_OVERRIDES += \
    ro.twrp.vendor_boot=true

PRODUCT_PACKAGES += \
    init.recovery.mt6991.rc \
    task_profiles.json

# Remove optional utilities inherited by TWRP common.mk for the size-gated first build.
PRODUCT_PACKAGES -= \
    bash \
    fsck.exfat \
    htop \
    lsof \
    mkfs.ntfs \
    mount.exfat \
    mount.ntfs \
    nano \
    openvpn \
    powertop \
    fsck.ntfs \
    vim

PRODUCT_SOONG_NAMESPACES += $(DEVICE_PATH)

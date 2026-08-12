# Unofficial TWRP for Redmi Turbo 5 Max

简体中文 / [ENGLISH](README.md)

本项目为 Redmi Turbo 5 Max 提供非官方 TWRP。开发过程中使用 AI 辅助。维护者负责架构决策、代码审查、设备测试、回归分析、集成和最终质量，并根据实机测试结果评估每项变更。未经审查和测试的建议不会进入发布版本。

## 设备范围

本项目仅适配以下设备：

- 产品名称：Redmi Turbo 5 Max
- 设备代号：`dash`
- 平台：MediaTek MT6991
- SoC：MediaTek Dimensity 9500s

Poco X8 Pro Max 不在当前测试范围内，不要在该设备上使用本项目产生的镜像。~~如果你想的话也不是不行。~~

### 功能正常的

- 触摸
- 解密（单用户，多用户均可。测试系统为 HyperOS / LineageOS 23.2）
- `/vendor` 安全卸载
- 震动
- 截图
- OTG

### 已知问题 / TODO

- MTP 传输大于 4 GiB 的文件时，PC 端可能会停止响应。请使用 `adb push` 传输，并耐心等待传输完成。

## 与上游 TWRP 的差异

- **内部存储**： 使用 `/data/media/0` 作为内部存储路径，不创建 `/sdcard` 兼容路径。

- **Root adb**: 当前测试镜像包含 root adb。已验证的集成基线在 recovery fragment 的 `prop.default` 中提供所需属性。普通的 `m recovery` 命令不会自动生成相同的 root adb fragment。

- **SELinux**: 使用 stock sepolicy。实机日志显示 recovery 处于 permissive 状态。此状态仅适用于 recovery。它不代表 Android 系统的 SELinux 状态。

- **Format Data** : 使用小米的 dm 映射处理。卡刷官方完整 OTA 后可直接使用 Format Data，无需再回到小米 recovery 做清除数据。

- **Cache (Rescue)**: 小米的 `/cache` 实际对应 `/rescue` 分区，故显式修改文案为 `Cache (Rescue)`，且 Factory Reset 不再清理该分区。Wipe Cache (Rescue) 和 Advanced Wipe 依然可以删除该分区的数据。

## 构建 recovery

以下步骤在 Android 源码树的根目录中运行。示例目录名称为 `source-twrp16`。

### 1. 同步源码

```sh
cd /path/to/source-twrp16
repo init -u https://github.com/TWRP-Test/platform_manifest_twrp_aosp -b twrp-16.0
mkdir -p .repo/local_manifests
curl -L -o .repo/local_manifests/dash.xml \
    https://raw.githubusercontent.com/YorokobiMaster/device_xiaomi_dash_twrp/twrp-16.0/local_manifest.xml
repo sync
```

### 2. 提供 stock DTB

从你自己的官方固件中提取 stock `vendor_boot.img`。

```sh
mkdir -p device/xiaomi/dash/local-inputs
python3 system/tools/mkbootimg/unpack_bootimg.py \
    --boot_img /path/to/stock/vendor_boot.img \
    --out device/xiaomi/dash/local-inputs
```

### 3. 编译

```sh
source build/envsetup.sh
lunch twrp_dash-bp2a-eng
m recovery vendorbootimage
```

`m recovery` 主要更新 recovery 二进制文件。`vendorbootimage` 还会刷新 recovery ramdisk staging。

本设备的 BoardConfig 包含 `BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true`。因此，最终集成必须使用新的 vendorboot staging。

### 4. 检查构建结果

```sh
cmp device/xiaomi/dash/recovery.fstab \
    out/target/product/dash/recovery/root/system/etc/recovery.fstab
test -x out/target/product/dash/recovery/root/system/bin/recovery
```

## 重打包 vendor_boot

[传送门](https://github.com/YorokobiMaster/dash_twrp_repack)

## 刷入

检查当前槽位，并设置镜像路径：

```sh
fastboot getvar current-slot
FINAL_IMAGE=/path/to/vendor_boot.img
fastboot flash vendor_boot_<a|b> "$FINAL_IMAGE"
```

## 源码和镜像的分发边界

源码仓库不直接收录 Xiaomi vendor/system 运行时组件，也不收录 stock DTB 或完整 stock 配置文件。你要从自己手上的官方固件中提取这些输入。

AOSP 衍生文件的来源和 Apache-2.0 许可映射位于 `THIRD_PARTY_NOTICES.md`。完整 Apache-2.0 文本位于 `LICENSES/Apache-2.0.txt`。

## 致谢

- [TeamWin Recovery Project](https://github.com/TeamWin/android_bootable_recovery)
- [TWRP-Test](https://github.com/TWRP-Test)
- 提出问题并愿意尝试的机友
- 开发过程中使用的模型：GPT 5.6、Kimi K3、GLM 5.2 和 Claude Opus 4.8

## 许可证

每个文件使用该文件所声明的许可证。保留上游文件中的版权和许可证声明。

TWRP 衍生文件通常使用 GPL-3.0-or-later。AOSP 衍生文件主要使用 Apache-2.0。

项目原创文件使用对应文件或仓库声明的许可证。仓库根目录的 `COPYING` 提供 GPL-3.0-or-later 文本。

## 免责声明

本源码仓库与 Xiaomi 无关。本源码仓库不代表 Xiaomi 或 TeamWin。

软件按“现状”提供，不提供任何担保。使用者承担刷机、设备损坏、数据丢失和售后影响的风险。

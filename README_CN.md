# Unofficial TWRP for Redmi Turbo 5 Max

简体中文 / [ENGLISH](README.md)

本项目为 Redmi Turbo 5 Max 提供非官方 TeamWin Recovery Project（TWRP）。

本项目在开发过程中使用 AI 辅助。维护者负责架构决策、代码审查、设备测试、回归分析、集成和最终质量，并根据实机测试结果评估每项变更。未经审查和测试的建议不会进入发布版本。

## 设备范围

本项目仅适配以下设备：

- 产品名称：Redmi Turbo 5 Max
- 设备代号：`dash`
- 平台：MediaTek MT6991
- SoC：MediaTek Dimensity 9500s
- 销售地区：中国大陆

Poco X8 Pro Max 不在当前测试范围内。不要在该设备上使用本项目的镜像。

`dash` 把 recovery 放在 `vendor_boot` 中。`m recovery` 更新 recovery 内容，`m vendorbootimage` 生成 `out/target/product/dash/vendor_boot.img`。该镜像不是最终刷入产物，下文提供重打包方法。

### 已知限制

- MTP 传输大于 4 GiB 的文件时，PC 端可能会停止响应。请使用 `adb push` 传输这些文件，并等待传输完成。
- USB-OTG 依赖的库太大，超出 `recovery_ramdisk` 容量范围，故暂无支持计划。

## 与上游 TWRP 的差异

- **内部存储**： 使用 `/data/media/0` 作为内部存储路径，不创建 `/sdcard` 兼容路径。

- **Root adb**: 当前测试镜像包含 root adb。已验证的集成基线在 recovery fragment 的 `prop.default` 中提供所需属性。普通的 `m recovery` 命令不会自动生成相同的 root adb fragment。

- **SELinux**: 使用 stock sepolicy。实机日志显示 recovery 处于 permissive 状态。此状态仅适用于 recovery。它不代表 Android 系统的 SELinux 状态。

- **Format Data** : 使用小米的 dm 映射处理。在已测试的官方完整 OTA 环境中，可以直接卡刷 OTA 后使用 Format Data，无需再回到小米 recovery 做一次全局清除。

- **Cache (Rescue)**: 小米的 `/cache` 实际对应 `/rescue` 分区，故显式修改文案为 `Cache (Rescue)`，且 Factory Reset 不再清理该分区。Wipe Cache (Rescue) 和 Advanced Wipe 可以删除该分区的数据。

- **上游**: 修复了设备适配过程中发现的若干上游不足与缺陷。

## 设计说明

### Android 15 vendor 兼容层

TWRP 16 使用 Android 16 工具链编译 recovery。设备的 vendor 和 odm 来自 Android 15。

`prebuilt/a15-aidl` 包含固定版本的 Android 15 头文件和源码，构建系统从这些源码生成兼容库。

该目录不包含 Xiaomi stock recovery 的兼容 ELF 文件。`SOURCE_LOCK.json` 记录 AOSP 源码版本和生成工具链版本。

Android 16 AIDL 生成器引用一个可选的 Binder transaction-name API，Android 15 Binder runtime 不提供该 API。

本项目提供一个窄范围兼容函数。该函数仅忽略可选的 transaction-name 映射。

### FBE 解密

当前解密路径使用原厂 Android 15 KeyMint 和 Gatekeeper 服务。Recovery 从 vendor 和 odm 加载这些服务及其依赖库。

`TW_KEEP_VENDOR_MOUNTED` 和 `TW_KEEP_ODM_MOUNTED` 保持所需分区可用。Recovery 不重新链接原厂 vendor 二进制文件。

Weaver 可以参与特定凭证路径，但当前 recovery 不自动启动 Weaver，该限制防止启动过程进入未经审计的 TEE、eSE 或 APDU 路径。

解密代码从 keystore2 的 `version` 表读取 schema 版本，正确的查询是：

```sql
SELECT version FROM version WHERE id=0;
```

不要使用 `PRAGMA user_version`。Keystore2 把数据库文件附加到内存数据库，两个数据库的版本值不同。

Recovery 先把原厂 SQLite 数据库复制到 `/tmp`。然后，`SqliteSnapshot` 以只读方式打开该副本。

### 触摸输入

触摸输入使用以下 vendor_dlkm 模块：

- `xiaomi_touch_dash.ko`
- `nt38771_touch_dash.ko`

Recovery init 按固定顺序加载这两个模块。

小米的触摸上报还需要 `touch_report_debug` 的 host-touch 循环，`dash-touch-bridge` init service 管理该循环。

该 service 使用 `/odm/lib64:/system/lib64` 作为 `LD_LIBRARY_PATH`。此设计不要求 recovery 启动完整 Android Binder HAL。

## 源码组成

`local_manifest.xml` 使用个人 fork 替换以下项目：

- [bootable/recovery](https://github.com/YorokobiMaster/android_bootable_recovery)
- [system/core](https://github.com/YorokobiMaster/android_system_core)
- [system/vold](https://github.com/YorokobiMaster/android_system_vold)
- [vendor/twrp](https://github.com/YorokobiMaster/android_vendor_twrp)

该 manifest 还会将本仓库同步到 `device/xiaomi/dash`，并添加以下重打包工具：

- [repack](https://github.com/YorokobiMaster/dash_vendor_boot_repack)

`vendor/twrp` 把 `TW_DASH_FS3002_HAPTICS` 导出给 Soong。没有该 fork 时，构建不会启用设备专属震动后端。

Manifest 跟踪 `twrp-16.0` 和 `main` 分支。这些分支可以变化。

`prebuilt/a15-aidl/SOURCE_LOCK.json` 只固定 Android 15 兼容源码。它不固定完整 Android 源码树。

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

从你自己的官方固件中提取 stock `vendor_boot`。准备以下输入文件：

```text
/path/to/stock/vendor_boot/aosp_unpack/dtb
```

运行提取脚本：

```sh
DASH_STOCK_ROOT=/path/to/stock device/xiaomi/dash/extract-files.sh
```

脚本校验 DTB 的 SHA-256。然后，脚本把 DTB 写入 Git 忽略的 `local-inputs` 目录。

### 3. 编译

```sh
source build/envsetup.sh
lunch twrp_dash-bp2a-eng
m recovery vendorbootimage -j4
```

`m recovery` 主要更新 recovery 二进制文件。`vendorbootimage` 还会刷新 recovery ramdisk staging。

本设备的 BoardConfig 包含 `BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true`。因此，最终集成必须使用新的 vendorboot staging。

### 4. 检查构建结果

```sh
python3 device/xiaomi/dash/evidence/verify_tree.py >/dev/null
python3 device/xiaomi/dash/tools/verify_a15_compat.py --check-built
cmp device/xiaomi/dash/recovery.fstab \
    out/target/product/dash/recovery/root/system/etc/recovery.fstab
test -x out/target/product/dash/recovery/root/system/bin/recovery
```

如果任一命令失败，请停止重打包流程。

## 重打包 vendor_boot

### 集成基线

最终重打包需要一个已通过实机测试的精简 runtime tree。该目录称为 `VALIDATED_RUNTIME_TREE`。

该目录不能直接来自 stock type-2 recovery fragment。该 fragment 通常不包含 `system/bin/recovery`；也不能是未经筛选的完整构建 staging，不同 API 世代的共享库会使 recovery 在 linker 阶段停止。

源码仓库不分发该目录中的 stock-derived runtime。如果你没有合格基线，请停止重打包流程。

### 1. 创建工作目录

```sh
VALIDATED_RUNTIME_TREE=/path/to/validated-runtime-tree
test -x "$VALIDATED_RUNTIME_TREE/system/bin/recovery"

DASH_BUILD_WORK="$(mktemp -d)"
RUNTIME_TREE="$DASH_BUILD_WORK/runtime-tree"
REPLACEMENT_CPIO="$DASH_BUILD_WORK/dash-recovery.cpio"
REPLACEMENT_LZ4="$DASH_BUILD_WORK/dash-recovery.cpio.lz4"
FINAL_FRAGMENT="$REPLACEMENT_LZ4"

mkdir "$RUNTIME_TREE"
cp -a --reflink=auto "$VALIDATED_RUNTIME_TREE"/. "$RUNTIME_TREE"/
```

`mktemp` 为本次集成创建新目录。工具不会覆盖以前的输出文件。

### 2. 更新已检查文件

```sh
cp out/target/product/dash/recovery/root/system/bin/recovery \
    "$RUNTIME_TREE/system/bin/recovery"
cp out/target/product/dash/recovery/root/system/etc/recovery.fstab \
    "$RUNTIME_TREE/system/etc/recovery.fstab"
cp out/target/product/dash/recovery/root/twres/languages/en.xml \
    "$RUNTIME_TREE/twres/languages/en.xml"
cp out/target/product/dash/recovery/root/init.recovery.mt6991.rc \
    "$RUNTIME_TREE/init.recovery.mt6991.rc"
cp out/target/product/dash/recovery/root/init.recovery.project.rc \
    "$RUNTIME_TREE/init.recovery.project.rc"

for library in \
    android.hardware.gatekeeper-V1-ndk-twrp-a15.so \
    android.hardware.security.keymint-V3-ndk-twrp-a15.so \
    android.hardware.security.secureclock-V1-ndk-twrp-a15-build.so \
    lib_android_keymaster_keymint_utils-twrp-a15.so \
    libkeymint_support-twrp-a15.so; do
    cp "out/target/product/dash/recovery/root/system/lib64/$library" \
        "$RUNTIME_TREE/system/lib64/$library"
done
```

不要用 `rsync` 覆盖完整 runtime tree。只更新本轮已经检查的文件。

如果你要更新主题文件，先检查设备专属路径。内部存储路径必须保持为 `/data/media/0`。

### 3. 创建 recovery fragment

```sh
out/host/linux-x86/bin/mkbootfs \
    -d out/target/product/dash \
    "$RUNTIME_TREE" > "$REPLACEMENT_CPIO"
out/host/linux-x86/bin/lz4 \
    -l -12 --favor-decSpeed "$REPLACEMENT_CPIO" "$REPLACEMENT_LZ4"
```

### 4. 检查 recovery fragment

```sh
CPIO_LIST="$DASH_BUILD_WORK/cpio-list.txt"
lz4 -dc "$FINAL_FRAGMENT" | cpio -t > "$CPIO_LIST"

grep -Fx 'system/bin/recovery' "$CPIO_LIST"
grep -Fx 'init.recovery.mt6991.rc' "$CPIO_LIST"
grep -Fx 'init.recovery.project.rc' "$CPIO_LIST"

for library in \
    android.hardware.gatekeeper-V1-ndk-twrp-a15.so \
    android.hardware.security.keymint-V3-ndk-twrp-a15.so \
    android.hardware.security.secureclock-V1-ndk-twrp-a15-build.so \
    lib_android_keymaster_keymint_utils-twrp-a15.so \
    libkeymint_support-twrp-a15.so; do
    grep -Fx "system/lib64/$library" "$CPIO_LIST"
done

lz4 -dc "$FINAL_FRAGMENT" | \
    cpio -i --to-stdout system/etc/recovery.fstab | \
    grep -F 'wipeduringfactoryreset=0' | \
    grep -F 'display="Cache (Rescue)"'

lz4 -dc "$FINAL_FRAGMENT" | cpio -i --to-stdout prop.default | \
    grep -Fx 'ro.secure=0'
lz4 -dc "$FINAL_FRAGMENT" | cpio -i --to-stdout prop.default | \
    grep -Fx 'ro.debuggable=1'
```

如果任一命令失败，不要使用该 fragment。

### 5. 创建 vendor_boot 镜像

从你自己的官方固件中提供 stock `vendor_boot` 和对应的 vbmeta owner 文件。`repack/inputs` 目录受 Git 忽略。

```sh
FINAL_IMAGE="$DASH_BUILD_WORK/dash-UNTESTED-vendor_boot.img"
REPACK_REPORT="$DASH_BUILD_WORK/repack-report.json"

repack/stock_aware_repack_tool \
    --template repack/inputs/dash-a15/stock-vendor_boot.img \
    --vbmeta-owner repack/inputs/dash-a15/template-local-vbmeta.img \
    --replacement "$FINAL_FRAGMENT" \
    --output "$FINAL_IMAGE" \
    --report "$REPACK_REPORT" \
    --budget-output "$DASH_BUILD_WORK/size-budget.json"

python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["status"] == "PACKAGING_VALID"' \
    "$REPACK_REPORT"
sha256sum "$FINAL_IMAGE"
```

重打包工具只替换 type-2、name=`recovery` 的 fragment。工具保留其他 payload 和容器元数据。

工具重新计算受影响的布局字段和 AVB footer。工具还检查本地 AVB descriptor 和镜像大小。

没有私钥时，输出镜像使用 algorithm-NONE footer。顶层 stock vbmeta descriptor 不再匹配该镜像。

`UNTESTED` 表示该镜像只通过主机端检查。只有实机测试可以改变该状态。

## 刷入

检查当前槽位，并设置镜像路径：

```sh
fastboot getvar current-slot
FINAL_IMAGE=/path/to/dash-UNTESTED-vendor_boot.img
```

返回 `current-slot: a` 时，运行：

```sh
fastboot flash vendor_boot_a "$FINAL_IMAGE"
```

返回 `current-slot: b` 时，运行：

```sh
fastboot flash vendor_boot_b "$FINAL_IMAGE"
```

适配过程中，A、B 两个 vendor_boot 槽均曾使用开发构建完成实机刷写与启动测试。

刷入镜像前，备份或确认你拥有 `vendor_boot` 镜像。

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

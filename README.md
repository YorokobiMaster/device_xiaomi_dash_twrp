# Unofficial TeamWin Recovery Project for Xiaomi dash

> 本项目大量工程由 AI 完成。如果你介意，请勿使用未经你自己审查的构建产物。

> 甚至该页面也请你尽可能结合源码进行验证。

dash的 recovery 内嵌在 `vendor_boot` 中，因此 Android 构建输出并非最终可直接刷入产物。本文档同时记录源码设计、已验证行为和已知缺陷。

请你知晓，本项目适配机型为 Redmi Turbo 5 Max (`dash`, mt6991 / Mediatek Dimensity 9500s), 中国大陆版本，非面向国际发售的 Poco X8 Pro Max. 不建议在 Poco X8 Pro Max 上测试，后果自负。

## 已知问题

- MTP 传输大于 4 GiB 时，PC 端可能卡死；请改用 `adb push`，并等待传输完整结束。
- `adb sideload` 完成后 recovery 可能卡在 sideload 页面，不建议使用。
- 震动，截图，OTG懒得修了。

## 与上游略有不同的地方

- **内部存储使用 `/data/media/0`。** recovery 运行时不保留 `/sdcard` 作为内部存储别名。
- **已验证候选镜像中的 adb 是 root。** 这一行为依赖额外的 recovery `prop.default` 属性补丁；普通 `m recovery` 本身不保证生成 root adbd。
- **SELinux 是 recovery-only 的 permissive。** 这是实机观察到的 stock recovery 行为，不代表正常 Android 系统启动策略。
- **Format Data 使用小米式的 dm 映射处理。** 在已测试的官方完整 OTA 环境中，可以直接卡刷 OTA 后使用 Format Data，无需再回到小米 recovery 做一次全局清除。
- **`/cache` 实际指向 Xiaomi 的 `rescue` 分区。** UI 名称为 `Cache (Rescue)`；源码目标是让 Factory Reset 排除它，但手动 Wipe Cache 或 Advanced Wipe 仍然可以清除它。请勿把 `/cache` 当作普通缓存分区。 p.s. adb sideload里面的忘改了，懒得改了。反正你也不会用的对吧？哪天出bug了顺手划掉。

## 可供参考的设计

### 解密

FBE 解密依赖原厂 A15 vendor/odm 提供的 KeyMint、Gatekeeper 和 Weaver 服务或库。通过 `TW_KEEP_VENDOR_MOUNTED` / `TW_KEEP_ODM_MOUNTED` 保持所需分区可用，vendor 侧原厂二进制不重新链接。

需要注意：

- keystore2 的 schema 版本应读取 `version` 表：`SELECT version FROM version WHERE id=0`。不要使用 `PRAGMA user_version`；keystore2 会把数据库文件 attach 到内存库，后者的 `user_version` 不代表 keystore2 schema 版本。
- 解密流程读取的原厂 SQLite 数据库先快照到 `/tmp`，再以只读方式打开（`SqliteSnapshot`），以避免直接读取正在变化的文件。

### A15 vendor 桥接与 TWRP 16

TWRP 14.1 的方案是把 vendor 库拖进构建环境重新链接；TWRP 16 则使用 A16 编译的 recovery 二进制，通过 `prebuilt/a15-aidl` 提供 A15 AIDL 头文件和链接兼容集，让它对接 A15 vendor 的接口。

当前 recovery 保持 stock sepolicy，并观察到 permissive 行为。若要改成 enforcing，必须先确认 recovery、`su` 和 vendor 服务实际运行在哪些 domain，以及这些 domain 在 stock policy 下需要哪些权限。

### 触摸

触摸屏使用设备专属的 vendor_dlkm 模块：`xiaomi_touch_dash.ko` 和 `nt38771_touch_dash.ko`。recovery init 负责加载模块。

小米的触摸上报依赖 `touch_report_debug` 的 host-touch 循环。项目把它包装成 `dash-touch-bridge` init service，并设置 `/odm/lib64` 的 `LD_LIBRARY_PATH`，避免把完整 Android Binder HAL 作为 recovery 的启动前提。

### Format Data

userdata 挂载 device-mapper 映射时直接执行 mkfs 会遇到设备忙。Format Data 前先执行 `dmctl delete userdata`，删除失败则 fail-closed；随后等待 `/dev/block/mapper/userdata` 节点真正消失，再格式化原始 userdata 块设备。

### Cache (Rescue) 与 Factory Reset

`/dev/block/by-name/rescue` 被 TWRP 挂载到 `/cache`，因此 `/cache` 不是传统意义上的 Android cache。源码 fstab 使用：

```text
wait,check,formattable,wipeduringfactoryreset=0,display="Cache (Rescue)"
```

`wipeduringfactoryreset=0` 只排除 Factory Reset；手动 Wipe Cache、Advanced Wipe 以及某些要求自动清 cache 的刷机流程仍可能擦除该分区。

## 构建与重打包

`m recovery` 主要更新 recovery 二进制及其直接构建产物；它不会保证 `out/target/product/dash/recovery/root/` 中的 recovery ramdisk staging 已刷新。本设备设置了 `BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true`，所以生成最终 recovery fragment 前必须额外构建 `vendorbootimage`。

下面的命令假定 Android 源码树为 `source-twrp16/`，步骤均在该目录内执行。本仓库根目录的 `local_manifest.xml` 会让 repo 额外拉入本设备树、修改过的三个平台仓库（`bootable/recovery`、`system/core`、`system/vold`）以及 `repack/` 工具。

```sh
# 1. 同步固定的 TWRP 16 源码树（含本设备树、平台修改和 repack 工具）
cd /path/to/source-twrp16
repo init -u https://github.com/TWRP-Test/platform_manifest_twrp_aosp -b twrp-16.0
mkdir -p .repo/local_manifests
curl -L -o .repo/local_manifests/dash.xml \
    https://raw.githubusercontent.com/YorokobiMaster/device_xiaomi_dash_twrp/twrp-16.0/local_manifest.xml
repo sync

# 2. 编译 recovery，并刷新 recovery ramdisk/vendor_boot staging
source build/envsetup.sh
lunch twrp_dash-bp2a-eng
SOONG_GOMEMLIMIT=8GiB SOONG_GOGC=20 m recovery vendorbootimage -j4

# 3. 在重打包前确认最新 fstab 已进入 staging
cmp device/xiaomi/dash/recovery.fstab \
    out/target/product/dash/recovery/root/system/etc/recovery.fstab

# 4. 准备经过审计的精简 runtime tree
#    不要直接把 stock vendor_boot 提取出的 recovery.cpio 当 replacement：
#    原厂 type-2 小片段通常不含 system/bin/recovery。
VALIDATED_RUNTIME_TREE=/path/to/validated-runtime-tree
RUNTIME_TREE=/tmp/dash-runtime-tree
REPLACEMENT_CPIO=/tmp/dash-recovery.cpio
REPLACEMENT_LZ4=/tmp/dash-recovery.cpio.lz4
FINAL_FRAGMENT="$REPLACEMENT_LZ4"
cp -a --reflink=auto "$VALIDATED_RUNTIME_TREE" "$RUNTIME_TREE"
# 只覆盖本轮已经审计过的文件；保留已验证的共享库、触摸桥接、prop 和
# 其它 stock-derived payload。不要用 rsync 把整个 staging tree 覆盖进来：
# 构建树中的共享库可能来自不同的 API 世代，单独替换 translate/compat
# 库会把新的未随包提供的 NDK 依赖带进 recovery，导致 linker 在启动时退出。
cp out/target/product/dash/recovery/root/system/bin/recovery \
    "$RUNTIME_TREE/system/bin/recovery"
cp out/target/product/dash/recovery/root/system/etc/recovery.fstab \
    "$RUNTIME_TREE/system/etc/recovery.fstab"
cp out/target/product/dash/recovery/root/twres/languages/en.xml \
    "$RUNTIME_TREE/twres/languages/en.xml"
# portrait.xml 等其它主题文件只有在逐文件对比源码与 validated tree、并确认
# 未回退 /data/media/0 等设备专属约束后，才能单独加入白名单。
out/host/linux-x86/bin/mkbootfs \
    -d out/target/product/dash \
    "$RUNTIME_TREE" > "$REPLACEMENT_CPIO"
out/host/linux-x86/bin/lz4 \
    -l -12 --favor-decSpeed "$REPLACEMENT_CPIO" "$REPLACEMENT_LZ4"

# 5. 如果需要 root adbd，才执行下面三行；否则保留上面的 FINAL_FRAGMENT
ROOT_ADBD_LZ4=/tmp/dash-root-adbd.cpio.lz4
python3 device/xiaomi/dash/tools/patch_recovery_adbd_props.py \
    --input-fragment "$REPLACEMENT_LZ4" \
    --output-fragment "$ROOT_ADBD_LZ4" \
    --report /tmp/root-adbd-patch-report.json
FINAL_FRAGMENT="$ROOT_ADBD_LZ4"

# 6. 验证最终 replacement fragment 同时含有新 recovery、fstab 和 root adbd 属性
lz4 -dc "$FINAL_FRAGMENT" | cpio -t | grep -Fx 'system/bin/recovery'
lz4 -dc "$FINAL_FRAGMENT" | \
    cpio -i --to-stdout system/etc/recovery.fstab | \
    grep -F 'wipeduringfactoryreset=0' \
    | grep -F 'display="Cache (Rescue)"'

# 7. 以原厂 vendor_boot 和 vbmeta 为模板重打包
#    repack/inputs/ 不在公开仓库中分发；请自行从官方固件提取 stock
#    vendor_boot/vbmeta 并放到对应路径
FINAL_IMAGE=/tmp/dash-UNTESTED-vendor_boot.img
repack/stock_aware_repack_tool \
    --template repack/inputs/dash-a15/stock-vendor_boot.img \
    --vbmeta-owner repack/inputs/dash-a15/template-local-vbmeta.img \
    --replacement "$FINAL_FRAGMENT" \
    --output "$FINAL_IMAGE" \
    --report /tmp/repack-report.json \
    --budget-output /tmp/size-budget.json
```

`verify_tree.py` 只检查源码树和静态约束，不检查最终 CPIO 是否真的包含最新文件；`cmp`、`system/bin/recovery` 存在性和 CPIO 内部核验不能省略。原厂 type-2 recovery 小片段不能单独作为 replacement，否则可能只换进 fstab，却留下 stock recovery 二进制。

重打包工具只替换 type-2/name=`recovery` fragment，保留非目标 payload 和容器元数据，并重新计算受影响的布局字段和 AVB footer。替换 recovery 后，顶层 stock vbmeta 描述符预期会发生变化；没有私钥时生成的是结构有效但未经设备验证的 `UNTESTED` 候选镜像。

本仓库不分发 Xiaomi vendor/system 运行时专有组件；设备树中仍包含 stock-derived DTB、A15 AIDL 兼容性预编译文件和校验材料，来源与分发许可应在公开发布前单独确认。

## 刷入

```sh
fastboot getvar current-slot
fastboot flash vendor_boot_current-slot
```

dash为 VAB 结构，`vendor_boot` 分槽位。刷前确认活动槽，并务必备份对应的原厂 `vendor_boot`。

## 致谢

- 基于 [TeamWin Recovery Project](https://github.com/TeamWin/android_bootable_recovery)，感谢 TeamWin 及所有上游贡献者。
- 基于 [TWRP-Test](https://github.com/TWRP-Test) 维护的 [TWRP 16](https://github.com/TWRP-Test/platform_manifest_twrp_aosp) 开发分支。
- GPT 5.6 Sol: 主力攻坚。
- Kimi K3: 发散，惹我生气。
- GLM 5.2: 某主力模型遇到点KeyMint, Decrypt关键字被safety check塞口球的时候。
- GPT 5.6 Luna: 我缺的token这块谁给我补啊？
- Claude Opus 4.8: 虽然很短暂但是谢谢你监工一段时间。
- [Tibo](https://github.com/tibo-openai) 大善人的Codex resets。
- 我和我的钱包。
- GO FUCK YOURSELF ANTHROPIC.

## 协议
- 本项目中的代码依照各文件适用的许可证发布，原有版权及许可证声明应予保留。TWRP 衍生部分通常适用 GPL-3.0-or-later，AOSP 衍生部分主要适用 Apache-2.0；本项目原创文档、脚本及工具的许可证以对应文件或仓库许可证说明为准。

## 免责声明
- 本项目与 Xiaomi 无关，不分发或修改 Xiaomi vendor/system 运行时专有组件。
- 软件按“现状”提供，不作任何担保。刷机变砖、数据丢失或售后影响均由使用者自行承担。

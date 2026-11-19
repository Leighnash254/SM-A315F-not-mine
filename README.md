<div align="center">

# ⚡ Zareth Kernel for Samsung Galaxy A31 & A41
### High-Performance, Stealth-Rooted Linux 4.14 Kernel for MediaTek MT6768 (Helio P65)
#### Designed for OneUI 8 (Android 16), OneUI 6/7 Ports, GSIs, and Stock Android 12

[![Release](https://img.shields.io/github/v/release/hpbzareth/SM-A315F?color=blue&label=Latest%20Release&style=for-the-badge)](https://github.com/hpbzareth/SM-A315F/releases/tag/v1.0.0-Rev3)
[![Kernel Version](https://img.shields.io/badge/Kernel-4.14.186-orange?style=for-the-badge&logo=linux)](https://github.com/hpbzareth/SM-A315F)
[![KernelSU-Next](https://img.shields.io/badge/KernelSU--Next-v1.0.5-brightgreen?style=for-the-badge)](https://github.com/KernelSU-Next/KernelSU-Next)
[![SuSFS](https://img.shields.io/badge/SuSFS-v2.2.0-red?style=for-the-badge)](https://gitlab.com/simonpunk/susfs4ksu)
[![Architecture](https://img.shields.io/badge/Arch-arm64-blueviolet?style=for-the-badge)](https://github.com/hpbzareth/SM-A315F)

**[English](README.md)** | **[Tiếng Việt (vi_VN)](README_vi.md)**

---

</div>

## 📌 Overview

**Zareth Kernel** is a custom kernel tailored specifically for the **Samsung Galaxy A31 (`SM-A315F`)** and **Samsung Galaxy A41 (`SM-A415F`)**, powered by the **MediaTek Helio P65 (`MT6768`)** SoC.

Built upon the battle-tested **Atrocious V6** codebase (by Abdullah Al Noman) and fine-tuned for modern Android userspace (OneUI 8 / Android 16 UN1CA port by Mouhamad10), Zareth Kernel delivers seamless root capabilities, advanced anti-detection mechanisms, Samsung Knox SDP storage compatibility, and smooth, battery-efficient performance.

---

## 🚀 Key Features

### 🛡️ Next-Gen Root & Anti-Detection
* **KernelSU-Next v1.0.5 (Official Companion `ksud v1.0.5`):** Complete kernel-level root solution with in-tree magic mount.
* **On-Demand Throne Tracking:** Overcomes Samsung SDP encrypted `/data` storage during early boot, ensuring instantaneous Manager detection and flawless manual superuser toggling.
* **SuSFS v2.2.0 (Kernel-Level Stealth):**
  * Advanced mount hiding and `try_umount` protection.
  * Hides KSU paths, root binaries, and module mounts from banking apps and anti-cheat engines.
  * Designed to achieve green Play Integrity (MEETS_DEVICE_INTEGRITY & MEETS_STRONG_INTEGRITY).
* **SELinux Permissive:** Provides rock-solid boot stability across custom ROMs, GSI ports, and ported vendor overlays.

### ⚡ Mitrinket-Inspired Performance Tuning
* **Touch & Display Latency:** SchedTune and EAS energy-aware `schedutil` governor tuned for instant 60Hz touch response and zero stutter.
* **RAM & Memory Optimization:**
  * High-speed ZRAM with LZ4 / ZSTD compression.
  * Proactive Process Reclaim and VM Pressure tuning frees ~150–200 MB of extra RAM for multitasking.
* **Network & Ping:** Google BBR TCP Congestion Control set as default for lower ping and smoother Wi-Fi / LTE throughput.
* **Deep Sleep & Battery Life:** Energy-efficient workqueues (`WQ_POWER_EFFICIENT_DEFAULT`), `PM_AUTOSLEEP`, and `PM_WAKELOCKS` ensure minimal battery drain while the screen is locked.
* **Storage I/O:** BFQ and MQ-Deadline I/O schedulers for rapid app startup and smooth database operations.

### 🌐 eBPF 5.15 Backport Subsystem
* Includes **183 backported eBPF commits** from Linux 5.15 (including `bpf_spin_lock`, `BPF_RAW_TRACEPOINT`, `bpf_sk_fullsock`, `bpf_tcp_sock`, `bpf_line_info`, and cgroup storage).
* Guarantees full compatibility with Android 14/15/16 networking daemons (`netd`, `bpfloader`), completely preventing bootloops on OneUI 8.

### 🔒 Samsung Knox SDP & F2FS Compatibility
* Full in-tree support for `CONFIG_SDP=y`, `CONFIG_FSCRYPT_SDP=y`, and `CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y`.
* Fully decrypts `/data` without data wipes, corruption, or bootloops.

### 📦 Clean AnyKernel3 Recovery Installer
* Stripped of `#FLASHAFTERUPDATEV2` and `/metadata` partition locking references.
* 100% safe, clean installation across TWRP, OrangeFox, and PBRP without partition unmount errors.

---

## 📱 Device Compatibility

| Device Name | Model Number | Target SoC | Defconfig |
| :--- | :--- | :--- | :--- |
| **Samsung Galaxy A31** | `SM-A315F`, `SM-A315G`, `SM-A315N` | MediaTek Helio P65 (`MT6768`) | `a31_defconfig` |
| **Samsung Galaxy A41** | `SM-A415F` | MediaTek Helio P65 (`MT6768`) | `a41_defconfig` |

---

## 📥 Downloads (Revision 3 - Current Stable)

Download flashable ZIPs and companion APKs directly from the **[GitHub Releases Page (v1.0.0-Rev3)](https://github.com/hpbzareth/SM-A315F/releases/tag/v1.0.0-Rev3)**:

| Asset | Description | Size |
| :--- | :--- | :--- |
| `SM-A31-ZarethKernel-Rev3-Permissive-SuSFS.zip` | Flashable AnyKernel3 for Galaxy A31 | ~37.1 MB |
| `SM-A41-ZarethKernel-Rev3-Permissive-SuSFS.zip` | Flashable AnyKernel3 for Galaxy A41 | ~37.3 MB |
| `KernelSU_Next_v1.0.5_12430-release.apk` | **Recommended** Manager APK (v1.0.5) | ~7.9 MB |
| `KernelSU_Next_v1.0.4_12335-release.apk` | Compatible Manager APK (v1.0.4) | ~7.8 MB |
| `APatch_11282_release.apk` | APatch Root Manager | ~6.7 MB |
| `sha256sums.txt` | Official SHA-256 Checksums | 525 B |

> [!NOTE]
> **Revision 1** and **Revision 2** are marked as `[OUTDATED]`. Always flash **Revision 3 (Rev3)** for full compatibility and built-in bootloop recovery.

---

## 📲 Installation Guide

### Prerequisites
1. Unlocked bootloader.
2. Custom Recovery installed (TWRP / OrangeFox).
3. Complete backup of your boot and data partitions.

### Steps
1. Download the flashable ZIP matching your device (`SM-A31-...` or `SM-A41-...`).
2. Boot your phone into Recovery Mode.
3. In TWRP / OrangeFox, select **Install** -> Choose the ZIP file -> **Swipe to Confirm Flash**.
4. Once installation completes successfully, select **Reboot System**.
5. After booting into Android, install the `KernelSU_Next_v1.0.5_12430-release.apk`.
6. Open KernelSU Next Manager to verify `Working` status and SuSFS integration.

---

## 🛠️ Build from Source

Automated builds are handled via GitHub Actions. If you wish to build locally:

```bash
# Clone the repository
git clone https://github.com/hpbzareth/SM-A315F.git -b main
cd SM-A315F

# Setup toolchain (Proton Clang 13 / Clang 14 + GCC 4.9 cross-compilers)
export ARCH=arm64
export SUBARCH=arm64
export CC=clang
export CLANG_TRIPLE=aarch64-linux-gnu-
export CROSS_COMPILE=aarch64-linux-gnu-
export CROSS_COMPILE_ARM32=arm-linux-gnueabi-

# Build for Samsung Galaxy A31
make O=out a31_defconfig
make O=out -j$(nproc)

# Append DTB and package with AnyKernel3
cat out/arch/arm64/boot/Image.gz out/arch/arm64/boot/dts/mediatek/mt6768.dtb > out/arch/arm64/boot/Image.gz-dtb
```

---

## 📜 Changelog

### Revision 3 (Rev3) — Current Stable
- **Resolved Zygisk Next `❌ Could not connect to service!` & Bootloop:**
  - Diagnosed crash loop in `system_server` caused by leftover dirty modules (`zygisk_vector` / Vector by JingMatrix) attempting Dobby inline hooking into read-only guard pages (`0x703bec2000`, `SEGV_ACCERR`), which shut down Zygisk Next daemon (`STOP_BY_CRASH`) and triggered RescueParty recovery bootloops.
  - Built-in AnyKernel3 auto-recovery: Automatically detects and disables `zygisk_vector` (`touch /data/adb/modules/zygisk_vector/disable`) and clears Zygisk Next crash lock (`rm -f /data/adb/zygisksu/.abort_msg /data/adb/zygisksu/hook_status`) during flashing.
- **Relaxed Module RWX Protections:** Disabled `CONFIG_STRICT_MODULE_RWX` to allow runtime memory hooking.
- **Zero KProbes Manual Inline Hooks:** Retained native manual hooks in `fs/exec.c`, `fs/read_write.c`, `fs/open.c`, `fs/stat.c`, and `drivers/input/input.c`.
- **Branding:** Updated to `4.14.186 Zareth Kernel Rev3`.

### Revision 2 (Rev2) — Outdated / Superseded
- **Fixed Manual Superuser Granting:** Injected on-demand `track_throne()` in `core_hook.c` and relaxed filesystem magic check in `throne_tracker.c` for Android 16 SDP encryption.
- **Fixed Module Removal:** Embedded official `ksud v1.0.5` binary matching Manager v1.0.5/v1.0.4 CLI protocol.
- **Fixed AnyKernel3 Partition Locking:** Stripped `#FLASHAFTERUPDATEV2` and `/metadata` references to eliminate TWRP unlocking errors.
- **Branding:** `4.14.186 Zareth Kernel Rev2`.

### Revision 1 (Rev1) — Outdated
- Initial release featuring Mitrinket-inspired performance tuning, KernelSU-Next LTS, and SuSFS v2.2.0.

---

## 🤝 Credits & Acknowledgements

- **Abdullah Al Noman ([@SN-Abdullah-Al-Noman](https://github.com/SN-Abdullah-Al-Noman)):** Original Atrocious Kernel developer.
- **Mouhamad10 ([@Mouhamad10](https://github.com/Mouhamad10)):** UN1CA OneUI 8 port developer & MT6768 bring-up notes.
- **simonpunk ([@simonpunk](https://gitlab.com/simonpunk)):** Creator of SuSFS.
- **KernelSU & KernelSU-Next Teams:** Revolutionary kernel-based root solutions.
- **osm0sis ([@osm0sis](https://github.com/osm0sis)):** AnyKernel3 flashable zip template.
- **Zareth Halcyon:** Kernel tuning, SDP/Knox integration, bug fixes & maintenance.

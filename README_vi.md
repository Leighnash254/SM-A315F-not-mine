<div align="center">

# ⚡ Zareth Kernel cho Samsung Galaxy A31 & A41
### Nhân Linux 4.14 Hiệu Năng Cao, Tích Hợp KernelSU-Next & Ẩn Root SuSFS cho MediaTek MT6768 (Helio P65)
#### Tương thích tối ưu với OneUI 8 (Android 16), các bản Rom Port OneUI 6/7, GSI và Stock Android 12

[![Bản phát hành](https://img.shields.io/github/v/release/hpbzareth/SM-A315F?color=blue&label=B%E1%BA%A3n%20M%E1%BB%9Bi%20Nh%E1%BA%A5t&style=for-the-badge)](https://github.com/hpbzareth/SM-A315F/releases/tag/v1.0.0-Rev2)
[![Phiên bản Kernel](https://img.shields.io/badge/Kernel-4.14.186-orange?style=for-the-badge&logo=linux)](https://github.com/hpbzareth/SM-A315F)
[![KernelSU-Next](https://img.shields.io/badge/KernelSU--Next-v1.0.5-brightgreen?style=for-the-badge)](https://github.com/KernelSU-Next/KernelSU-Next)
[![SuSFS](https://img.shields.io/badge/SuSFS-v2.2.0-red?style=for-the-badge)](https://gitlab.com/simonpunk/susfs4ksu)
[![Kiến trúc](https://img.shields.io/badge/Ki%E1%BA%BFn%20tr%C3%BAc-arm64-blueviolet?style=for-the-badge)](https://github.com/hpbzareth/SM-A315F)

**[English](README.md)** | **[Tiếng Việt (vi_VN)](README_vi.md)**

---

</div>

## 📌 Giới Thiệu

**Zareth Kernel** là bản nhân tuỳ chỉnh hiệu năng cao được phát triển chuyên biệt cho hai dòng máy **Samsung Galaxy A31 (`SM-A315F`)** và **Samsung Galaxy A41 (`SM-A415F`)**, chạy vi xử lý **MediaTek Helio P65 (`MT6768`)**.

Được kế thừa trên nền tảng ổn định của **Atrocious V6** (bởi dev Abdullah Al Noman) và tinh chỉnh tối ưu cho hệ điều hành mới nhất (OneUI 8 / Android 16 UN1CA port bởi dev Mouhamad10), Zareth Kernel đem lại khả năng Root sâu ở tầng nhân (KernelSU-Next), công nghệ ẩn Root chống phát hiện ngân hàng hàng đầu (SuSFS v2.2.0), tương thích chuẩn mã hoá Samsung Knox SDP, cùng hiệu năng mượt mà và tiết kiệm pin vượt trội.

---

## 🚀 Các Tính Năng Nổi Bật

### 🛡️ Hệ Thống Root Thế Hệ Mới & Ẩn Root Toàn Diện
* **KernelSU-Next v1.0.5 (Nhúng sẵn `ksud v1.0.5` chính thức):** Quản lý quyền Root trực tiếp từ nhân Linux qua cơ chế Magic Mount không can thiệp hệ thống.
* **On-Demand Throne Tracking:** Giải quyết triệt để vấn đề phân vùng `/data` bị mã hoá Samsung SDP ở giai đoạn early boot, giúp kernel nhận diện Manager tức thì và cấp quyền Superuser thủ công mượt mà 100%.
* **SuSFS v2.2.0 (Ẩn Root Cấp Độ Nhân):**
  * Ẩn toàn bộ các điểm gắn kết (mount points) và bảo vệ bằng `try_umount`.
  * Giấu đường dẫn KSU, tệp thực thi `su`, và các module KSU khỏi các app ngân hàng, ví điện tử (VNeID, Techcombank, Vietcombank, Momo...) và game chống gian lận.
  * Hỗ trợ vượt chứng chỉ Play Integrity (Device & Strong integrity).
* **SELinux Permissive:** Đảm bảo độ tương thích và ổn định tuyệt đối khi chạy Rom Port, GSI, ngăn chặn hoàn toàn lỗi treo logo do phân quyền SELinux.

### ⚡ Tối Ưu Hiệu Năng Chuẩn Mitrinket
* **Giảm Độ Trễ Cảm Ứng & Màn Hình:** Điều tốc năng lượng `schedutil` kết hợp cơ chế SchedTune EAS mang lại phản hồi cảm ứng 60Hz tức thì, triệt tiêu hiện tượng giật khung hình.
* **Tối Ưu & Thu Hồi Bộ Nhớ RAM:**
  * RAM ảo ZRAM tốc độ cao chuẩn nén LZ4 / ZSTD.
  * Tích hợp Process Reclaim và cân bằng áp lực VM Pressure, giải phóng thêm từ ~150 đến 200 MB RAM thực cho các tác vụ đa nhiệm.
* **Mạng & Độ Trễ Ping:** Kích hoạt thuật toán điều khiển tắc nghẽn Google BBR TCP làm mặc định, giảm ping khi chơi game và lướt web mượt mà trên Wi-Fi & 4G/LTE.
* **Tiết Kiệm Pin & Chế Độ Ngủ Sâu:** Tối ưu hoá hàng đợi công việc tiết kiệm điện (`WQ_POWER_EFFICIENT_DEFAULT`), `PM_AUTOSLEEP` và `PM_WAKELOCKS` giúp máy đạt trạng thái Deep Sleep chuẩn khi tắt màn hình, hạn chế tụt pin qua đêm.
* **Tốc Độ Đọc Ghi Bộ Nhớ (I/O):** Bộ điều phối I/O BFQ và MQ-Deadline giúp tăng tốc độ khởi động ứng dụng và load dữ liệu eMMC.

### 🌐 Hệ Thống Backport eBPF 5.15
* Chứa sẵn **183 bản vá backport eBPF** từ Linux 5.15 (bao gồm `bpf_spin_lock`, `BPF_RAW_TRACEPOINT`, `bpf_sk_fullsock`, `bpf_tcp_sock`, `bpf_line_info`, cgroup storage...).
* Giúp các tiến trình mạng hiện đại của Android 14/15/16 (`netd`, `bpfloader`) hoạt động trơn tru, không bị bootloop trên OneUI 8.

### 🔒 Tương Thích Hoàn Hảo Mã Hoá Samsung Knox SDP & F2FS
* Giữ nguyên vẹn `CONFIG_SDP=y`, `CONFIG_FSCRYPT_SDP=y` và `CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y`.
* Giải mã phân vùng dữ liệu `/data` trơn tru trên OneUI 8 và Stock, không bị đòi format hay mất dữ liệu.

### 📦 Bộ Cài AnyKernel3 Không Lỗi Phân Vùng
* Đã gỡ bỏ sạch sẽ mã định danh `#FLASHAFTERUPDATEV2` và các lệnh unmount `/metadata` trong updater script.
* Flash mượt mà 100% qua TWRP, OrangeFox, PBRP, không lo lỗi khoá phân vùng `mmcblk0p28` hay bận `system_root`.

---

## 📱 Danh Sách Thiết Bị Hỗ Trợ

| Tên Thiết Bị | Mã Model | Chipset | File Cấu Hình (Defconfig) |
| :--- | :--- | :--- | :--- |
| **Samsung Galaxy A31** | `SM-A315F`, `SM-A315G`, `SM-A315N` | MediaTek Helio P65 (`MT6768`) | `a31_defconfig` |
| **Samsung Galaxy A41** | `SM-A415F` | MediaTek Helio P65 (`MT6768`) | `a41_defconfig` |

---

## 📥 Tải Về (Revision 2 - Bản Ổn Định Hiện Tại)

Tải file zip flash và app quản lý tại trang **[GitHub Releases (v1.0.0-Rev2)](https://github.com/hpbzareth/SM-A315F/releases/tag/v1.0.0-Rev2)**:

| File Cài Đặt | Mô Tả | Dung Lượng |
| :--- | :--- | :--- |
| `SM-A31-ZarethKernel-Rev2-Permissive-SuSFS.zip` | File zip flash qua Recovery cho Galaxy A31 | ~37.1 MB |
| `SM-A41-ZarethKernel-Rev2-Permissive-SuSFS.zip` | File zip flash qua Recovery cho Galaxy A41 | ~37.3 MB |
| `KernelSU_Next_v1.0.5_12430-release.apk` | **Khuyên dùng:** App quản lý KernelSU Next (v1.0.5) | ~7.9 MB |
| `KernelSU_Next_v1.0.4_12335-release.apk` | App quản lý KernelSU Next (v1.0.4) | ~7.8 MB |
| `APatch_11282_release.apk` | App quản lý APatch Root | ~6.7 MB |
| `sha256sums.txt` | Mã kiểm tra toàn vẹn SHA-256 | 525 B |

> [!WARNING]
> **Bản Revision 1** đã bị đánh dấu là `[OUTDATED]` do lỗi kẹt UID Manager lúc khởi động và lệch giao thức daemon `ksud`. **Tuyệt đối khuyến nghị anh em sử dụng bản Revision 2 (Rev2)**.

---

## 📲 Hướng Dẫn Cài Đặt

### Chuẩn bị
1. Máy đã mở khoá Bootloader (Unlock Bootloader).
2. Đã cài Custom Recovery (TWRP hoặc OrangeFox).
3. Sao lưu lại phân vùng `boot` và `data` đề phòng rủi ro.

### Các bước cài đặt
1. Tải file ZIP tương ứng với thiết bị của bạn (`SM-A31-...` hoặc `SM-A41-...`).
2. Khởi động điện thoại vào chế độ Recovery (TWRP / OrangeFox).
3. Chọn mục **Install** -> Chọn file ZIP vừa tải -> **Gạt thanh trượt để xác nhận Flash**.
4. Sau khi quá trình flash báo thành công, chọn **Reboot System**.
5. Sau khi máy khởi động vào Android, cài đặt ứng dụng `KernelSU_Next_v1.0.5_12430-release.apk`.
6. Mở app KernelSU Next để kiểm tra trạng thái hoạt động (`Hoạt động`) cùng huy hiệu SuSFS.

---

## 📜 Lịch Sử Phiên Bản (Changelog)

### Revision 2 (Rev2) — Bản Ổn Định Mới Nhất
- **Sửa Lỗi Cấp Superuser Thủ Công:** Tích hợp cơ chế quét on-demand `track_throne()` vào `core_hook.c` và bỏ qua kiểm tra magic con trong `throne_tracker.c` cho Android 16 SDP.
- **Sửa Lỗi Gỡ Module:** Nhúng đúng binary `ksud v1.0.5` đồng bộ hoàn toàn chuẩn giao thức với Manager v1.0.5 và v1.0.4.
- **Sửa Lỗi Khóa Phân Vùng Recovery:** Loại bỏ hoàn toàn `#FLASHAFTERUPDATEV2` và các mount `/metadata` trong script cài đặt AnyKernel3.
- **Định danh:** Nâng cấp tên kernel thành `4.14.186 Zareth Kernel Rev2`.

### Revision 1 (Rev1) — Đã Lỗi Thời
- Phiên bản đầu tiên tích hợp tối ưu Mitrinket, KernelSU-Next LTS và SuSFS v2.2.0.

---

## 🤝 Lời Cảm Ơn & Nguồn Tham Khảo

- **Abdullah Al Noman ([@SN-Abdullah-Al-Noman](https://github.com/SN-Abdullah-Al-Noman)):** Tác giả bản kernel Atrocious gốc cho A31.
- **Mouhamad10 ([@Mouhamad10](https://github.com/Mouhamad10)):** Tác giả bản port OneUI 8 UN1CA & tài liệu bring-up MT6768.
- **simonpunk ([@simonpunk](https://gitlab.com/simonpunk)):** Tác giả SuSFS.
- **Đội ngũ phát triển KernelSU & KernelSU-Next:** Giải pháp Root thế hệ mới cho nhân Linux.
- **osm0sis ([@osm0sis](https://github.com/osm0sis)):** Bộ khung flash zip AnyKernel3.
- **Zareth Halcyon:** Tinh chỉnh kernel, tích hợp SDP Knox, khắc phục lỗi & duy trì dự án.

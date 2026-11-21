# Mini Project - Hệ thống giám sát tiêu hao năng lượng (Smart Energy Monitor)

## Đề bài

Lập trình viên tại công ty giải pháp quản lý năng lượng thông minh cho nhà máy sản xuất xây dựng chương trình CLI **giám sát tiêu hao năng lượng** bằng Python. Toàn bộ logic bắt buộc triển khai bằng **các hàm độc lập**, không viết mã tự do bên ngoài hàm.

**Mục tiêu:** vận dụng List chứa Dictionary để lưu bản ghi; tư duy lập trình hàm (chia nhỏ bài toán, tham số, giá trị trả về); phân tích yêu cầu từ SRS; Clean Code, Logging, Unit Test và Exception Handling.

Dữ liệu demo (khởi tạo trong hàm `main`):

```python
devices = [
    {"id": "M01", "location": "Mechanical Shop A", "old_index": 1200, "new_index": 4500, "status": "Normal"},
    {"id": "M02", "location": "Assembly Line B",   "old_index": 2300, "new_index": 8500, "status": "Overload"},
]
```

### Menu bắt buộc

```
════════════════════════════════════════════════
      SMART ENERGY MONITOR - PHÒNG CƠ ĐIỆN      
════════════════════════════════════════════════
1. Xem danh sách thiết bị giám sát
2. Cập nhật chỉ số điện tiêu thụ (Check-in)
3. Kích hoạt trạng thái cảnh báo quá tải
4. Tính tổng lượng điện & Chi phí năng lượng
5. Thoát chương trình
════════════════════════════════════════════════
```

## 1. Phân tích yêu cầu

### Quy tắc nghiệp vụ

| Quy tắc | Giá trị | Hằng số trong code |
|---|---|---|
| Lượng điện tiêu thụ của thiết bị | `new_index - old_index` (kWh) | hàm `get_consumption` |
| Ngưỡng quá tải | tiêu thụ **> 5,000 kWh** mới được chuyển sang Overload | `OVERLOAD_THRESHOLD_KWH = 5_000` |
| Đơn giá cơ sở | 3,000 VND / kWh | `UNIT_PRICE_VND = 3_000` |
| Chiết khấu | tổng **>= 50,000 kWh** thì giảm 3% trên tổng tiền, ngược lại 0% | `DISCOUNT_THRESHOLD_KWH = 50_000`, `DISCOUNT_PERCENT = 3` |

### Mã lỗi

| Mã | Tình huống | Xử lý |
|---|---|---|
| ERR-E01 | Mã thiết bị không tồn tại (chức năng 2, 3) | Báo lỗi và **hủy thao tác**, quay về menu |
| ERR-E02 | Chỉ số mới < chỉ số cũ | Báo lỗi, **vòng lặp bắt nhập lại** chỉ số mới |
| ERR-E03 | Nhập chữ / số âm cho chỉ số, để trống mã thiết bị | Báo lỗi, nhập lại ngay tại bước đó (mã tự đặt cho lỗi validate dữ liệu, đề không ghi rõ) |
| ERR-E04 | Kích hoạt cảnh báo cho thiết bị đã Overload | Báo lỗi, hủy thao tác |

### Thiết kế hàm (100% logic nằm trong hàm)

| Nhóm | Hàm | Tham số → Trả về | Vai trò |
|---|---|---|---|
| Hiển thị | `show_devices(devices)` | list → None | Bảng căn lề f-string; danh sách rỗng in "Hệ thống hiện chưa có thiết bị giám sát nào!" |
| Cập nhật chỉ số | `update_indices(devices)` | list → bool | Nhập mã, kiểm tra tồn tại (ERR-E01), nhập chỉ số cũ / mới (ERR-E02, ERR-E03), cập nhật trực tiếp |
| Kích hoạt cảnh báo | `activate_overload_alert(devices)` | list → bool | Tìm thiết bị, chặn ERR-E01 / ERR-E04, tiêu thụ > 5,000 kWh thì ghi đè `status = "Overload"` + log WARNING |
| Tính toán tài chính | `calculate_energy_financials(devices)` | list → `tuple(total_kwh, discount_percent, total_cost)` | **Chỉ tính toán và return tuple**, không print |
| Hiển thị báo cáo | `show_financial_report(devices)` | list → None | Nơi gọi hàm tính toán nhận tuple và in ra màn hình |
| Điều phối | `main(devices=None)` | → None | Cấu hình logging, khởi tạo dữ liệu, vòng lặp `while True`, rẽ nhánh 1-5 |
| Phụ trợ | `setup_logging`, `display_menu`, `read_menu_choice`, `find_device`, `get_consumption`, `input_device_id`, `input_non_negative_int` |  | Cấu hình log, in menu, đọc lựa chọn (try-except), tìm kiếm, tính tiêu thụ, nhập có validate |

### Exception Handling

- **Menu:** `read_menu_choice` dùng `try: int(...) except ValueError` → nhập chữ không làm sập chương trình; số ngoài 1-5 báo "Chức năng không tồn tại".
- **Chỉ số điện:** `input_non_negative_int` dùng `try-except ValueError` + kiểm tra `>= 0`, lặp đến khi hợp lệ.
- **Mã thiết bị:** chuẩn hóa (xóa khoảng trắng, viết hoa: `m01` → `M01`), không cho để trống.

### Logging

`setup_logging()` được gọi đầu hàm `main`, format `%(asctime)s - %(levelname)s - %(message)s` (giờ dạng `2026-06-09 15:50:47` như đề):

- **Console:** chỉ in mức **WARNING**: dòng `[Cảnh báo]: Thiết bị ... đã vượt ngưỡng tiêu thụ an toàn, chuyển sang OVERLOAD!` xuất hiện đúng thời điểm kích hoạt quá tải như ví dụ của đề.
- **File `energy_monitor.log`:** lưu từ mức INFO trở lên: khởi động / dừng, xem danh sách, cập nhật chỉ số, báo cáo tài chính (INFO); lỗi ERR-E01 / E02 / E04 (ERROR); cảnh báo quá tải (WARNING). Các lỗi đã có thông báo `[Lỗi]` cho người dùng nên không in trùng lên console.

### Thuật toán hàm core

```
calculate_energy_financials(devices):
    total_kwh ← Σ (new_index - old_index) của mọi thiết bị
    NẾU total_kwh >= 50,000: discount ← 3   NGƯỢC LẠI: discount ← 0
    total_cost ← total_kwh × 3,000 × (100 - discount) / 100
    TRẢ VỀ (total_kwh, discount, total_cost)
```

Ví dụ của đề: 60,000 kWh × 3,000 = 180,000,000 VND; giảm 3% → **174,600,000 VND**.

## 2. Mã nguồn

File: [`energy_monitor.py`](energy_monitor.py)

```python
"""Smart Energy Monitor - Hệ thống giám sát tiêu hao năng lượng nhà máy.

Mỗi thiết bị là một dictionary:
    {"id": str, "location": str, "old_index": int, "new_index": int,
     "status": "Normal" | "Overload"}
Toàn bộ logic được chia thành các hàm độc lập; chương trình chạy từ main().
"""

import logging

LOG_FILE = "energy_monitor.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

STATUS_NORMAL = "Normal"
STATUS_OVERLOAD = "Overload"
OVERLOAD_THRESHOLD_KWH = 5_000  # vượt mức này thì được phép báo quá tải
UNIT_PRICE_VND = 3_000  # đơn giá cơ sở VND / kWh
DISCOUNT_THRESHOLD_KWH = 50_000  # từ mốc này trở lên được chiết khấu
DISCOUNT_PERCENT = 3  # chiết khấu 3% trên tổng tiền

MENU_LINE = "═" * 48
TABLE_LINE = "─" * 72

ERR_NOT_FOUND = (
    "(ERR-E01): Mã thiết bị này không tồn tại trong danh sách hệ thống"
)
ERR_INDEX_ORDER = "(ERR-E02): Chỉ số mới không được nhỏ hơn chỉ số cũ"
ERR_INVALID_INPUT = "(ERR-E03)"
ERR_ALREADY_OVERLOAD = (
    "(ERR-E04): Thao tác bị hủy! Thiết bị này đã được kích hoạt trạng thái "
    "OVERLOAD từ trước!"
)

logger = logging.getLogger("energy_monitor")


# =====================================================================
# CẤU HÌNH & HÀM PHỤ TRỢ
# =====================================================================
def setup_logging(log_file=LOG_FILE):
    """Cấu hình logging cho toàn hệ thống.

    - Console: chỉ mức WARNING (cảnh báo quá tải hiện ngay cho người vận
      hành; lỗi nhập liệu đã có thông báo [Lỗi] riêng nên không in trùng).
    - File energy_monitor.log: từ mức INFO (lưu vết đầy đủ để kiểm tra).
    """
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.addFilter(lambda record: record.levelno == logging.WARNING)
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False


def get_consumption(device):
    """Lượng điện tiêu thụ (kWh) của một thiết bị = new_index - old_index."""
    return device["new_index"] - device["old_index"]


def find_device(devices, device_id):
    """Tìm thiết bị theo mã (đã chuẩn hóa).

    Trả về:
        dict | None: thiết bị tìm thấy hoặc None
    """
    for device in devices:
        if device["id"] == device_id:
            return device
    return None


def input_device_id(prompt):
    """Nhập mã thiết bị: xóa khoảng trắng, viết hoa; để trống thì nhập lại."""
    while True:
        device_id = "".join(input(prompt).split()).upper()
        if device_id:
            return device_id
        print(f"[Lỗi] {ERR_INVALID_INPUT}: Mã thiết bị không được để trống!")


def input_non_negative_int(prompt):
    """Nhập số nguyên >= 0; nhập chữ hoặc số âm thì báo lỗi và nhập lại."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print(f"[Lỗi] {ERR_INVALID_INPUT}: Chỉ số phải là số nguyên!")
            logger.info("Invalid numeric input for index: %r", text)
            continue
        if value < 0:
            print(
                f"[Lỗi] {ERR_INVALID_INPUT}: Chỉ số phải lớn hơn hoặc bằng 0!"
            )
            logger.info("Negative index input: %s", value)
            continue
        return value


# =====================================================================
# CÁC HÀM CHỨC NĂNG
# =====================================================================
def display_menu():
    """In menu chính (không trả về giá trị)."""
    print()
    print(MENU_LINE)
    print("SMART ENERGY MONITOR - PHÒNG CƠ ĐIỆN".center(48))
    print(MENU_LINE)
    print("1. Xem danh sách thiết bị giám sát")
    print("2. Cập nhật chỉ số điện tiêu thụ (Check-in)")
    print("3. Kích hoạt trạng thái cảnh báo quá tải")
    print("4. Tính tổng lượng điện & Chi phí năng lượng")
    print("5. Thoát chương trình")
    print(MENU_LINE)


def show_devices(devices):
    """Chức năng 1: in bảng thiết bị căn lề bằng f-string. Không trả về."""
    if not devices:
        print("Hệ thống hiện chưa có thiết bị giám sát nào!")
        return
    print("── DANH SÁCH THIẾT BỊ GIÁM SÁT ──")
    print(
        f"{'MÃ TB':<6}| {'VỊ TRÍ PHÂN XƯỞNG':<22}| {'CHỈ SỐ CŨ':>9} | "
        f"{'CHỈ SỐ MỚI':>10} | TRẠNG THÁI"
    )
    print(TABLE_LINE)
    for device in devices:
        print(
            f"{device['id']:<6}| {device['location']:<22}| "
            f"{device['old_index']:>9} | {device['new_index']:>10} | "
            f"{device['status']}"
        )
    print(TABLE_LINE)
    logger.info("Viewed device list (%s devices)", len(devices))


def update_indices(devices):
    """Chức năng 2: cập nhật chỉ số cũ / mới của một thiết bị.

    - Không tìm thấy mã: báo ERR-E01 và hủy thao tác.
    - Chỉ số mới < chỉ số cũ: báo ERR-E02 và bắt nhập lại chỉ số mới.

    Trả về:
        bool: True nếu cập nhật thành công
    """
    print("── CẬP NHẬT CHỈ SỐ ĐIỆN ──")
    device_id = input_device_id("Nhập mã thiết bị: ")
    device = find_device(devices, device_id)
    if device is None:
        print(f"[Lỗi] {ERR_NOT_FOUND}")
        logger.error("ERR-E01 - Update failed, device %s not found", device_id)
        return False

    old_index = input_non_negative_int("Nhập chỉ số cũ: ")
    while True:
        new_index = input_non_negative_int("Nhập chỉ số mới: ")
        if new_index >= old_index:
            break
        print(f"[Lỗi] {ERR_INDEX_ORDER} ({old_index}). Vui lòng nhập lại!")
        logger.error(
            "ERR-E02 - New index %s < old index %s for %s",
            new_index,
            old_index,
            device_id,
        )

    device["old_index"] = old_index
    device["new_index"] = new_index
    print(f"[Thành công]: Thiết bị {device_id} đã được cập nhật số liệu mới")
    logger.info(
        "Updated %s indices: old=%s, new=%s", device_id, old_index, new_index
    )
    return True


def activate_overload_alert(devices):
    """Chức năng 3: chuyển thiết bị sang Overload nếu tiêu thụ > 5,000 kWh.

    Trả về:
        bool: True nếu thiết bị được chuyển sang Overload
    """
    print("── KÍCH HOẠT TRẠNG THÁI CẢNH BÁO ──")
    device_id = input_device_id("Nhập mã thiết bị cần duyệt: ")
    device = find_device(devices, device_id)
    if device is None:
        print(f"[Lỗi] {ERR_NOT_FOUND}")
        logger.error("ERR-E01 - Alert failed, device %s not found", device_id)
        return False
    if device["status"] == STATUS_OVERLOAD:
        print(f"[Lỗi] {ERR_ALREADY_OVERLOAD}")
        logger.error("ERR-E04 - Device %s is already Overload", device_id)
        return False

    consumption = get_consumption(device)
    print(
        f"Tìm thấy thiết bị tại: {device['location']} "
        f"(Lượng tiêu thụ: {consumption} kWh)"
    )
    if consumption <= OVERLOAD_THRESHOLD_KWH:
        print(
            f"[Thông báo]: Thiết bị {device_id} vẫn trong ngưỡng an toàn "
            f"(<= {OVERLOAD_THRESHOLD_KWH:,} kWh), giữ trạng thái "
            f"{device['status']}."
        )
        logger.info(
            "Device %s is within safe threshold (%s kWh)",
            device_id,
            consumption,
        )
        return False

    device["status"] = STATUS_OVERLOAD
    logger.warning(
        "[Cảnh báo]: Thiết bị %s đã vượt ngưỡng tiêu thụ an toàn, "
        "chuyển sang OVERLOAD!",
        device_id,
    )
    print(
        f"[Thành công]: Thiết bị {device_id} đã được kích hoạt trạng thái "
        "OVERLOAD!"
    )
    return True


def calculate_energy_financials(devices):
    """Tính toán tài chính năng lượng của toàn nhà máy (KHÔNG in ra màn hình).

    Tham số:
        devices (list[dict]): danh sách thiết bị
    Trả về:
        tuple: (tổng lượng điện kWh, phần trăm chiết khấu,
                tổng tiền điện sau chiết khấu VND)
    """
    total_kwh = sum(get_consumption(device) for device in devices)
    if total_kwh >= DISCOUNT_THRESHOLD_KWH:
        discount_percent = DISCOUNT_PERCENT
    else:
        discount_percent = 0
    gross_cost = total_kwh * UNIT_PRICE_VND
    total_cost = round(gross_cost * (100 - discount_percent) / 100)
    return total_kwh, discount_percent, total_cost


def show_financial_report(devices):
    """Chức năng 4: gọi hàm tính toán, nhận tuple và hiển thị báo cáo."""
    total_kwh, discount_percent, total_cost = calculate_energy_financials(
        devices
    )
    print("── BÁO CÁO TÀI CHÍNH NĂNG LƯỢNG ──")
    print(f"+ Tổng lượng điện tiêu thụ thực tế: {total_kwh:,} kWh")
    print(f"+ Tỷ lệ chiết khấu áp dụng từ nhà nước: {discount_percent}%")
    print(
        "+ Tổng chi phí năng lượng phải trả sau chiết khấu: "
        f"{total_cost:,} VND"
    )
    logger.info(
        "Financial report: %s kWh, discount %s%%, cost %s VND",
        total_kwh,
        discount_percent,
        total_cost,
    )


def read_menu_choice():
    """Đọc lựa chọn menu; nhập chữ thì bắt ValueError, trả về None."""
    text = input("Mời chọn chức năng (1-5): ").strip()
    try:
        return int(text)
    except ValueError:
        print("[Lỗi]: Lựa chọn phải là số nguyên từ 1 đến 5!")
        logger.info("Invalid menu input: %r", text)
        return None


# =====================================================================
# HÀM ĐIỀU PHỐI CHÍNH
# =====================================================================
def main(devices=None):
    """Cấu hình logging, khởi tạo dữ liệu demo và chạy vòng lặp menu."""
    setup_logging()
    if devices is None:
        devices = [
            {
                "id": "M01",
                "location": "Mechanical Shop A",
                "old_index": 1200,
                "new_index": 4500,
                "status": STATUS_NORMAL,
            },
            {
                "id": "M02",
                "location": "Assembly Line B",
                "old_index": 2300,
                "new_index": 8500,
                "status": STATUS_OVERLOAD,
            },
        ]
    logger.info("Smart Energy Monitor started")
    while True:
        display_menu()
        choice = read_menu_choice()
        if choice is None:
            continue
        if choice == 1:
            show_devices(devices)
        elif choice == 2:
            update_indices(devices)
        elif choice == 3:
            activate_overload_alert(devices)
        elif choice == 4:
            show_financial_report(devices)
        elif choice == 5:
            print("Cảm ơn bạn đã sử dụng phần mềm Smart Energy Monitor!")
            print("[Chương trình kết thúc]")
            logger.info("Smart Energy Monitor stopped")
            break
        else:
            print("[Lỗi]: Chức năng không tồn tại, vui lòng chọn từ 1 đến 5!")
            logger.info("Menu choice out of range: %s", choice)


if __name__ == "__main__":
    main()
```

## 3. Kết quả chạy thử

Kịch bản: xem danh sách → báo cáo với dữ liệu gốc (9,500 kWh, 0%) → duyệt M01 khi còn trong ngưỡng → nhập menu sai (`abc`, `9`) → cập nhật mã không tồn tại (ERR-E01) → cập nhật `m01` (chỉ số âm, chữ, chỉ số mới nhỏ hơn cũ → ERR-E02, nhập lại 6500) → kích hoạt M02 (ERR-E04) → kích hoạt M01 (5,500 kWh → OVERLOAD + WARNING) → M99 (ERR-E01) → cập nhật M02 (2300 → 56800) → xem danh sách → báo cáo (60,000 kWh, 3%, 174,600,000 VND) → thoát. Phần nhập của người dùng hiển thị ngay sau dấu nhắc; khung menu lặp lại được ẩn.

```
Mời chọn chức năng (1-5): 1
── DANH SÁCH THIẾT BỊ GIÁM SÁT ──
MÃ TB | VỊ TRÍ PHÂN XƯỞNG     | CHỈ SỐ CŨ | CHỈ SỐ MỚI | TRẠNG THÁI
────────────────────────────────────────────────────────────────────────
M01   | Mechanical Shop A     |      1200 |       4500 | Normal
M02   | Assembly Line B       |      2300 |       8500 | Overload
────────────────────────────────────────────────────────────────────────

Mời chọn chức năng (1-5): 4
── BÁO CÁO TÀI CHÍNH NĂNG LƯỢNG ──
+ Tổng lượng điện tiêu thụ thực tế: 9,500 kWh
+ Tỷ lệ chiết khấu áp dụng từ nhà nước: 0%
+ Tổng chi phí năng lượng phải trả sau chiết khấu: 28,500,000 VND

Mời chọn chức năng (1-5): 3
── KÍCH HOẠT TRẠNG THÁI CẢNH BÁO ──
Nhập mã thiết bị cần duyệt: M01
Tìm thấy thiết bị tại: Mechanical Shop A (Lượng tiêu thụ: 3300 kWh)
[Thông báo]: Thiết bị M01 vẫn trong ngưỡng an toàn (<= 5,000 kWh), giữ trạng thái Normal.

Mời chọn chức năng (1-5): abc
[Lỗi]: Lựa chọn phải là số nguyên từ 1 đến 5!

Mời chọn chức năng (1-5): 9
[Lỗi]: Chức năng không tồn tại, vui lòng chọn từ 1 đến 5!

Mời chọn chức năng (1-5): 2
── CẬP NHẬT CHỈ SỐ ĐIỆN ──
Nhập mã thiết bị: M99
[Lỗi] (ERR-E01): Mã thiết bị này không tồn tại trong danh sách hệ thống

Mời chọn chức năng (1-5): 2
── CẬP NHẬT CHỈ SỐ ĐIỆN ──
Nhập mã thiết bị: m01
Nhập chỉ số cũ: -5
[Lỗi] (ERR-E03): Chỉ số phải lớn hơn hoặc bằng 0!
Nhập chỉ số cũ: 1000
Nhập chỉ số mới: năm nghìn
[Lỗi] (ERR-E03): Chỉ số phải là số nguyên!
Nhập chỉ số mới: 500
[Lỗi] (ERR-E02): Chỉ số mới không được nhỏ hơn chỉ số cũ (1000). Vui lòng nhập lại!
Nhập chỉ số mới: 6500
[Thành công]: Thiết bị M01 đã được cập nhật số liệu mới

Mời chọn chức năng (1-5): 3
── KÍCH HOẠT TRẠNG THÁI CẢNH BÁO ──
Nhập mã thiết bị cần duyệt: M02
[Lỗi] (ERR-E04): Thao tác bị hủy! Thiết bị này đã được kích hoạt trạng thái OVERLOAD từ trước!

Mời chọn chức năng (1-5): 3
── KÍCH HOẠT TRẠNG THÁI CẢNH BÁO ──
Nhập mã thiết bị cần duyệt:  
[Lỗi] (ERR-E03): Mã thiết bị không được để trống!
Nhập mã thiết bị cần duyệt: M01
Tìm thấy thiết bị tại: Mechanical Shop A (Lượng tiêu thụ: 5500 kWh)
2026-11-21 16:47:25 - WARNING - [Cảnh báo]: Thiết bị M01 đã vượt ngưỡng tiêu thụ an toàn, chuyển sang OVERLOAD!
[Thành công]: Thiết bị M01 đã được kích hoạt trạng thái OVERLOAD!

Mời chọn chức năng (1-5): 3
── KÍCH HOẠT TRẠNG THÁI CẢNH BÁO ──
Nhập mã thiết bị cần duyệt: M99
[Lỗi] (ERR-E01): Mã thiết bị này không tồn tại trong danh sách hệ thống

Mời chọn chức năng (1-5): 2
── CẬP NHẬT CHỈ SỐ ĐIỆN ──
Nhập mã thiết bị: M02
Nhập chỉ số cũ: 2300
Nhập chỉ số mới: 56800
[Thành công]: Thiết bị M02 đã được cập nhật số liệu mới

Mời chọn chức năng (1-5): 1
── DANH SÁCH THIẾT BỊ GIÁM SÁT ──
MÃ TB | VỊ TRÍ PHÂN XƯỞNG     | CHỈ SỐ CŨ | CHỈ SỐ MỚI | TRẠNG THÁI
────────────────────────────────────────────────────────────────────────
M01   | Mechanical Shop A     |      1000 |       6500 | Overload
M02   | Assembly Line B       |      2300 |      56800 | Overload
────────────────────────────────────────────────────────────────────────

Mời chọn chức năng (1-5): 4
── BÁO CÁO TÀI CHÍNH NĂNG LƯỢNG ──
+ Tổng lượng điện tiêu thụ thực tế: 60,000 kWh
+ Tỷ lệ chiết khấu áp dụng từ nhà nước: 3%
+ Tổng chi phí năng lượng phải trả sau chiết khấu: 174,600,000 VND

Mời chọn chức năng (1-5): 5
Cảm ơn bạn đã sử dụng phần mềm Smart Energy Monitor!
[Chương trình kết thúc]
```

Trường hợp danh sách trống (gọi hàm trực tiếp):

```
>>> show_devices([]):
Hệ thống hiện chưa có thiết bị giám sát nào!

>>> calculate_energy_financials([]) -> (0, 0, 0)
```

### File log `energy_monitor.log`

```
2026-11-21 16:47:25 - INFO - Smart Energy Monitor started
2026-11-21 16:47:25 - INFO - Viewed device list (2 devices)
2026-11-21 16:47:25 - INFO - Financial report: 9500 kWh, discount 0%, cost 28500000 VND
2026-11-21 16:47:25 - INFO - Device M01 is within safe threshold (3300 kWh)
2026-11-21 16:47:25 - INFO - Invalid menu input: 'abc'
2026-11-21 16:47:25 - INFO - Menu choice out of range: 9
2026-11-21 16:47:25 - ERROR - ERR-E01 - Update failed, device M99 not found
2026-11-21 16:47:25 - INFO - Negative index input: -5
2026-11-21 16:47:25 - INFO - Invalid numeric input for index: 'năm nghìn'
2026-11-21 16:47:25 - ERROR - ERR-E02 - New index 500 < old index 1000 for M01
2026-11-21 16:47:25 - INFO - Updated M01 indices: old=1000, new=6500
2026-11-21 16:47:25 - ERROR - ERR-E04 - Device M02 is already Overload
2026-11-21 16:47:25 - WARNING - [Cảnh báo]: Thiết bị M01 đã vượt ngưỡng tiêu thụ an toàn, chuyển sang OVERLOAD!
2026-11-21 16:47:25 - ERROR - ERR-E01 - Alert failed, device M99 not found
2026-11-21 16:47:25 - INFO - Updated M02 indices: old=2300, new=56800
2026-11-21 16:47:25 - INFO - Viewed device list (2 devices)
2026-11-21 16:47:25 - INFO - Financial report: 60000 kWh, discount 3%, cost 174600000 VND
2026-11-21 16:47:25 - INFO - Smart Energy Monitor stopped
```

### Bảng kiểm thử chức năng

| Chức năng | Dữ liệu | Kết quả mong đợi | Đạt |
|---|---|---|---|
| 1 - Có dữ liệu | 2 thiết bị mẫu | Bảng căn lề M01 / M02 | ✅ |
| 1 - Danh sách trống | `[]` | Hệ thống hiện chưa có thiết bị giám sát nào! | ✅ |
| 2 - Thành công | m01, 1000, 6500 | [Thành công]: Thiết bị M01 đã được cập nhật số liệu mới | ✅ |
| 2 - Không tìm thấy | M99 | ERR-E01, hủy thao tác | ✅ |
| 2 - Chỉ số mới < cũ | cũ 1000, mới 500 | ERR-E02, nhập lại chỉ số mới | ✅ |
| 2 - Chỉ số âm / chữ | -5, `năm nghìn` | ERR-E03, nhập lại tại bước đó | ✅ |
| 3 - Trong ngưỡng | M01 (3,300 kWh) | Giữ Normal | ✅ |
| 3 - Kích hoạt | M01 (5,500 kWh) | WARNING + [Thành công]... OVERLOAD! | ✅ |
| 3 - Đã quá tải | M02 | ERR-E04 | ✅ |
| 4 - Dưới mốc | 9,500 kWh | 0%, 28,500,000 VND | ✅ |
| 4 - Đạt mốc | 60,000 kWh | 3%, 174,600,000 VND | ✅ |
| Menu sai | `abc`, `9` | Báo lỗi, không crash | ✅ |
| 5 - Thoát | 5 | Lời chào + [Chương trình kết thúc] | ✅ |

## 4. Unit Test

File: [`test_energy.py`](test_energy.py): 3 ca kiểm thử biên tài chính (dưới mốc, đúng mốc 50,000 kWh, ví dụ 60,000 kWh của đề) và 3 ca bổ sung.

```python
"""Unit test cho hàm core calculate_energy_financials.

Chạy: python -m unittest test_energy -v   (hoặc: pytest test_energy.py)
"""

import unittest

from energy_monitor import calculate_energy_financials


def make_device(device_id, old_index, new_index):
    """Tạo nhanh một thiết bị giả lập cho test."""
    return {
        "id": device_id,
        "location": "Test",
        "old_index": old_index,
        "new_index": new_index,
        "status": "Normal",
    }


class TestCalculateEnergyFinancials(unittest.TestCase):
    """3 ca kiểm thử biên tài chính + các ca bổ sung."""

    def test_case_1_below_threshold_no_discount(self):
        """Ca 1: dữ liệu mẫu 3,300 + 6,200 = 9,500 kWh < 50,000 -> 0%."""
        devices = [
            make_device("M01", 1200, 4500),
            make_device("M02", 2300, 8500),
        ]
        self.assertEqual(
            calculate_energy_financials(devices), (9500, 0, 28_500_000)
        )

    def test_case_2_exactly_threshold_gets_discount(self):
        """Ca 2 (biên): đúng 50,000 kWh -> được chiết khấu 3%."""
        devices = [
            make_device("M01", 0, 20_000),
            make_device("M02", 10_000, 40_000),
        ]
        self.assertEqual(
            calculate_energy_financials(devices), (50_000, 3, 145_500_000)
        )

    def test_case_3_above_threshold_like_srs_example(self):
        """Ca 3: 60,000 kWh -> 180,000,000 x 97% = 174,600,000 VND."""
        devices = [
            make_device("M01", 1000, 6500),
            make_device("M02", 2300, 56_800),
        ]
        self.assertEqual(
            calculate_energy_financials(devices), (60_000, 3, 174_600_000)
        )

    def test_just_below_threshold(self):
        """Bổ sung: 49,999 kWh vẫn chưa được chiết khấu."""
        devices = [make_device("M01", 1, 50_000)]
        self.assertEqual(
            calculate_energy_financials(devices), (49_999, 0, 149_997_000)
        )

    def test_empty_device_list(self):
        """Bổ sung: không có thiết bị -> (0, 0, 0)."""
        self.assertEqual(calculate_energy_financials([]), (0, 0, 0))

    def test_returns_tuple_of_three_values(self):
        """Bổ sung: kết quả phải là tuple gồm đúng 3 giá trị."""
        result = calculate_energy_financials([make_device("M01", 0, 10)])
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
```

```
test_case_1_below_threshold_no_discount (test_energy.TestCalculateEnergyFinancials.test_case_1_below_threshold_no_discount)
Ca 1: dữ liệu mẫu 3,300 + 6,200 = 9,500 kWh < 50,000 -> 0%. ... ok
test_case_2_exactly_threshold_gets_discount (test_energy.TestCalculateEnergyFinancials.test_case_2_exactly_threshold_gets_discount)
Ca 2 (biên): đúng 50,000 kWh -> được chiết khấu 3%. ... ok
test_case_3_above_threshold_like_srs_example (test_energy.TestCalculateEnergyFinancials.test_case_3_above_threshold_like_srs_example)
Ca 3: 60,000 kWh -> 180,000,000 x 97% = 174,600,000 VND. ... ok
test_empty_device_list (test_energy.TestCalculateEnergyFinancials.test_empty_device_list)
Bổ sung: không có thiết bị -> (0, 0, 0). ... ok
test_just_below_threshold (test_energy.TestCalculateEnergyFinancials.test_just_below_threshold)
Bổ sung: 49,999 kWh vẫn chưa được chiết khấu. ... ok
test_returns_tuple_of_three_values (test_energy.TestCalculateEnergyFinancials.test_returns_tuple_of_three_values)
Bổ sung: kết quả phải là tuple gồm đúng 3 giá trị. ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

## 5. Đối chiếu thang điểm

| Tiêu chí | Điểm | Đáp ứng |
|---|---|---|
| Cấu trúc hàm & đặt tên | 3.0 | Mọi logic nằm trong hàm, tên `snake_case` (`show_devices`, `update_indices`, `activate_overload_alert`, `calculate_energy_financials`); hàm tài chính `return` tuple 3 giá trị, không print |
| Logic nghiệp vụ & Logging | 3.0 | Bảng căn lề, cập nhật đúng thiết bị, tìm kiếm + ghi đè trạng thái; tiêu thụ và mốc chiết khấu 3% chính xác; WARNING đúng lúc kích hoạt quá tải |
| Menu & vòng lặp điều phối | 1.0 | `while True` trong `main`, thoát ở lựa chọn 5 |
| Validate & ngoại lệ | 2.0 | Chỉ số >= 0, chỉ số mới >= chỉ số cũ; `try-except ValueError` ở menu và ô nhập chỉ số |
| Unit Test & Clean Code | 1.0 | `test_energy.py` 6 test pass; hằng số thay magic number, docstring, PEP 8 (kiểm tra bằng `ruff`, dòng <= 79 ký tự) |

## Ghi chú

- Đề không kèm nội dung SRS nên 3 ca kiểm thử tài chính được chọn theo biên của quy tắc chiết khấu: dưới 50,000 kWh, đúng 50,000 kWh và ví dụ 60,000 kWh.
- Ở chức năng 2, người dùng nhập cả chỉ số cũ và chỉ số mới như ví dụ của đề; hai giá trị này ghi đè `old_index` / `new_index` của thiết bị.
- Mã ERR-E03 được dùng cho lỗi định dạng dữ liệu nhập (đề chỉ nêu E01, E02, E04).
- Đề ghi "vị trí xưởng không được để trống"; vì không có chức năng thêm thiết bị, ràng buộc không để trống được áp dụng cho ô nhập mã thiết bị.

## Cách chạy

Yêu cầu Python 3.8+, không cần thư viện ngoài.

```bash
python energy_monitor.py
python -m unittest test_energy -v     # hoặc: pytest test_energy.py
```

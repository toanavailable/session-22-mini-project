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

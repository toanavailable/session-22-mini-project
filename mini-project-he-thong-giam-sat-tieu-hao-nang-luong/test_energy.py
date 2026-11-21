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

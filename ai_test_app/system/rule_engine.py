from typing import List
from models.schemas import TestCase


def generate_basic_testcases(project_name: str, scenario: str, requirements: str | None = None) -> List[TestCase]:
    tc_list: List[TestCase] = []

    tc_list.append(
        TestCase(
            id="TC001",
            title=f"Validate scenario: {scenario}",
            steps=[
                "Chuẩn bị môi trường",
                f"Thực hiện kịch bản: {scenario}",
                "Quan sát hệ thống phản hồi"
            ],
            expected="Hệ thống xử lý kịch bản thành công mà không lỗi"
        )
    )

    tc_list.append(
        TestCase(
            id="TC002",
            title="Kiểm tra dữ liệu bắt buộc",
            steps=[
                "Bỏ trống các field bắt buộc (nếu có)",
                "Submit form / gọi API"
            ],
            expected="Hệ thống báo lỗi hợp lệ, hiển thị thông báo validation"
        )
    )

    if requirements:
        tc_list.append(
            TestCase(
                id="TC003",
                title="Kiểm tra theo requirements người dùng gửi lên",
                steps=[
                    f"Đối chiếu yêu cầu: {requirements}",
                    "Thực thi từng yêu cầu",
                ],
                expected="Tất cả yêu cầu được thỏa"
            )
        )

    return tc_list

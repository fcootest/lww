"""Seed EMP data from AP."""

from src.modules.emp.model import EMP
from src.modules.emp.repository import emp_repository


EMP_SEED = [
    EMP(emp_id="EMP-001", emp_code="TiepTA", emp_name="Tran Anh Tiep",
        email="tiepta@apero.vn", department="CDT-LEGAL", position="Legal Manager"),
    EMP(emp_id="EMP-002", emp_code="TrungNV", emp_name="Nguyen Van Trung",
        email="trungnv@apero.vn", department="CDT-LEGAL", position="Legal Specialist"),
    EMP(emp_id="EMP-003", emp_code="HuongLT", emp_name="Le Thi Huong",
        email="huonglt@apero.vn", department="CDT-LEGAL", position="Legal Intern"),
    EMP(emp_id="EMP-004", emp_code="MinhPT", emp_name="Pham Thanh Minh",
        email="minhpt@apero.vn", department="CDT-PRODUCT", position="Product Manager"),
    EMP(emp_id="EMP-005", emp_code="LanNTH", emp_name="Nguyen Thi Hong Lan",
        email="lannth@apero.vn", department="CDT-ASO", position="ASO Specialist"),
    EMP(emp_id="EMP-006", emp_code="DucNH", emp_name="Nguyen Hoang Duc",
        email="ducnh@apero.vn", department="CDT-FINANCE", position="Accountant"),
]


def seed_all():
    """Seed all EMP data."""
    emp_repository.seed(EMP_SEED)

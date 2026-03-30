"""Seed TST data from AP Appendix B.1."""

from src.modules.tst.model import TST
from src.modules.tst.repository import tst_repository


LF210_SEED = [
    TST(tst_id="TST-001", tst_code="LF210", tst_name="Copyright Check", tst_level=1, sla_days=5),
    TST(tst_id="TST-002", tst_code="LF211", tst_name="Input tai lieu UI/UX", tst_level=2, my_parent_task="TST-001", sla_days=1),
    TST(tst_id="TST-003", tst_code="LF211.1", tst_name="Chuan bi ban so sanh UI/UX", tst_level=3, my_parent_task="TST-002", sla_days=1),
    TST(tst_id="TST-004", tst_code="LF212", tst_name="Ra soat UI/UX", tst_level=2, my_parent_task="TST-001", sla_days=2),
    TST(tst_id="TST-005", tst_code="LF212.1", tst_name="Doi chieu man hinh", tst_level=3, my_parent_task="TST-004", sla_days=1),
    TST(tst_id="TST-006", tst_code="LF212.2", tst_name="Kiem tra Asset", tst_level=3, my_parent_task="TST-004", sla_days=1),
    TST(tst_id="TST-007", tst_code="LF212.3", tst_name="Kiem tra anh AI", tst_level=3, my_parent_task="TST-004", sla_days=1),
    TST(tst_id="TST-008", tst_code="LF212.4", tst_name="Doi chieu chinh sach Store", tst_level=3, my_parent_task="TST-004", sla_days=1),
    TST(tst_id="TST-009", tst_code="LF212.5", tst_name="Tong hop & phan hoi", tst_level=3, my_parent_task="TST-004", sla_days=1),
]

LF220_SEED = [
    TST(tst_id="TST-010", tst_code="LF220", tst_name="Trademark Check", tst_level=1, sla_days=3),
    TST(tst_id="TST-011", tst_code="LF221", tst_name="Input Trademark details", tst_level=2, my_parent_task="TST-010", sla_days=1),
    TST(tst_id="TST-012", tst_code="LF221.1", tst_name="Gui ten app, icon, keywords", tst_level=3, my_parent_task="TST-011", sla_days=1),
    TST(tst_id="TST-013", tst_code="LF222", tst_name="Ra soat Trademark", tst_level=2, my_parent_task="TST-010", sla_days=1),
    TST(tst_id="TST-014", tst_code="LF222.1", tst_name="Tra cuu WIPO", tst_level=3, my_parent_task="TST-013", sla_days=1),
    TST(tst_id="TST-015", tst_code="LF222.2", tst_name="Tra cuu USPTO", tst_level=3, my_parent_task="TST-013", sla_days=1),
    TST(tst_id="TST-016", tst_code="LF222.3", tst_name="Tra cuu Cuc SHTT VN", tst_level=3, my_parent_task="TST-013", sla_days=1),
    TST(tst_id="TST-017", tst_code="LF222.4", tst_name="Tra cuu Google Search", tst_level=3, my_parent_task="TST-013", sla_days=1),
    TST(tst_id="TST-018", tst_code="LF222.5", tst_name="Tra cuu WIPO Image", tst_level=3, my_parent_task="TST-013", sla_days=1),
    TST(tst_id="TST-019", tst_code="LF222.6", tst_name="Tra cuu Google Reverse Image", tst_level=3, my_parent_task="TST-013", sla_days=1),
    TST(tst_id="TST-020", tst_code="LF222.7", tst_name="Tong hop & phan hoi Product", tst_level=3, my_parent_task="TST-013", sla_days=1),
]

LF230_SEED = [
    TST(tst_id="TST-021", tst_code="LF230", tst_name="Policy Review", tst_level=1, sla_days=7),
    TST(tst_id="TST-022", tst_code="LF231", tst_name="Input Policy docs", tst_level=2, my_parent_task="TST-021", sla_days=1),
    TST(tst_id="TST-023", tst_code="LF231.1", tst_name="Upload policy drafts", tst_level=3, my_parent_task="TST-022", sla_days=1),
    TST(tst_id="TST-024", tst_code="LF232", tst_name="Ra soat Policy", tst_level=2, my_parent_task="TST-021", sla_days=2),
    TST(tst_id="TST-025", tst_code="LF232.1", tst_name="Kiem tra noi dung", tst_level=3, my_parent_task="TST-024", sla_days=1),
    TST(tst_id="TST-026", tst_code="LF232.2", tst_name="Kiem tra luat ap dung", tst_level=3, my_parent_task="TST-024", sla_days=1),
    TST(tst_id="TST-027", tst_code="LF232.3", tst_name="Kiem tra tuan thu", tst_level=3, my_parent_task="TST-024", sla_days=1),
    TST(tst_id="TST-028", tst_code="LF232.4", tst_name="Kiem tra quyen rieng tu", tst_level=3, my_parent_task="TST-024", sla_days=1),
    TST(tst_id="TST-029", tst_code="LF232.5", tst_name="Tong hop ra soat policy", tst_level=3, my_parent_task="TST-024", sla_days=1),
    TST(tst_id="TST-030", tst_code="LF233", tst_name="Phe duyet Policy", tst_level=2, my_parent_task="TST-021", sla_days=1),
    TST(tst_id="TST-031", tst_code="LF233.1", tst_name="Legal Manager duyet", tst_level=3, my_parent_task="TST-030", sla_days=1),
    TST(tst_id="TST-032", tst_code="LF234", tst_name="Xuat ban Policy", tst_level=2, my_parent_task="TST-021", sla_days=1),
    TST(tst_id="TST-033", tst_code="LF234.1", tst_name="Publish policy", tst_level=3, my_parent_task="TST-032", sla_days=1),
]

LF240_SEED = [
    TST(tst_id="TST-034", tst_code="LF240", tst_name="Contract Review", tst_level=1, sla_days=10),
    TST(tst_id="TST-035", tst_code="LF241", tst_name="Input Contract", tst_level=2, my_parent_task="TST-034", sla_days=1),
    TST(tst_id="TST-036", tst_code="LF241.1", tst_name="Upload hop dong", tst_level=3, my_parent_task="TST-035", sla_days=1),
    TST(tst_id="TST-037", tst_code="LF242", tst_name="Ra soat Contract", tst_level=2, my_parent_task="TST-034", sla_days=3),
    TST(tst_id="TST-038", tst_code="LF242.1", tst_name="Kiem tra dieu khoan", tst_level=3, my_parent_task="TST-037", sla_days=1),
    TST(tst_id="TST-039", tst_code="LF242.2", tst_name="Kiem tra luat ap dung", tst_level=3, my_parent_task="TST-037", sla_days=1),
    TST(tst_id="TST-040", tst_code="LF242.3", tst_name="Kiem tra rui ro", tst_level=3, my_parent_task="TST-037", sla_days=1),
    TST(tst_id="TST-041", tst_code="LF242.4", tst_name="Kiem tra boi thuong", tst_level=3, my_parent_task="TST-037", sla_days=1),
    TST(tst_id="TST-042", tst_code="LF242.5", tst_name="Tong hop ra soat contract", tst_level=3, my_parent_task="TST-037", sla_days=1),
    TST(tst_id="TST-043", tst_code="LF243", tst_name="Phe duyet Contract", tst_level=2, my_parent_task="TST-034", sla_days=1),
    TST(tst_id="TST-044", tst_code="LF243.1", tst_name="Legal Manager duyet contract", tst_level=3, my_parent_task="TST-043", sla_days=1),
    TST(tst_id="TST-045", tst_code="LF244", tst_name="Ky hop dong", tst_level=2, my_parent_task="TST-034", sla_days=2),
    TST(tst_id="TST-046", tst_code="LF244.1", tst_name="Ky va luu tru", tst_level=3, my_parent_task="TST-045", sla_days=1),
    TST(tst_id="TST-047", tst_code="LF245", tst_name="Theo doi Contract", tst_level=2, my_parent_task="TST-034", sla_days=2),
    TST(tst_id="TST-048", tst_code="LF245.1", tst_name="Theo doi thuc hien", tst_level=3, my_parent_task="TST-047", sla_days=1),
    TST(tst_id="TST-049", tst_code="LF246", tst_name="Gia han / Cham dut", tst_level=2, my_parent_task="TST-034", sla_days=1),
    TST(tst_id="TST-050", tst_code="LF246.1", tst_name="Xu ly gia han hoac cham dut", tst_level=3, my_parent_task="TST-049", sla_days=1),
    TST(tst_id="TST-051", tst_code="LF247", tst_name="Luu tru Contract", tst_level=2, my_parent_task="TST-034", sla_days=1),
    TST(tst_id="TST-052", tst_code="LF247.1", tst_name="Luu tru va dong bo", tst_level=3, my_parent_task="TST-051", sla_days=1),
]

ALL_SEED = LF210_SEED + LF220_SEED + LF230_SEED + LF240_SEED


def seed_all():
    """Seed all TST data."""
    tst_repository.seed(ALL_SEED)

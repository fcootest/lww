"""Step 3: TST entity + repository tests."""

import pytest
from pydantic import ValidationError
from src.modules.tst.model import TST, TSTTreeNode
from src.modules.tst.repository import TSTRepository
from src.seeds.seed_tst import LF210_SEED


@pytest.fixture
def repo():
    """Fresh repository with LF210 seed data."""
    from src.config.database import reset_db
    reset_db()
    r = TSTRepository()
    r.seed(LF210_SEED)
    return r


class TestTSTModel:
    """Test TST Pydantic model validation."""

    def test_valid_tst(self):
        t = TST(tst_id="T1", tst_code="LF210", tst_name="Test", tst_level=1)
        assert t.tst_id == "T1"
        assert t.tst_level == 1

    def test_level_must_be_1_2_3(self):
        with pytest.raises(ValidationError):
            TST(tst_id="T1", tst_code="X", tst_name="X", tst_level=0)
        with pytest.raises(ValidationError):
            TST(tst_id="T1", tst_code="X", tst_name="X", tst_level=4)

    def test_default_is_active(self):
        t = TST(tst_id="T1", tst_code="X", tst_name="X", tst_level=1)
        assert t.is_active is True

    def test_optional_fields(self):
        t = TST(tst_id="T1", tst_code="X", tst_name="X", tst_level=2, my_parent_task="P1", sla_days=3)
        assert t.my_parent_task == "P1"
        assert t.sla_days == 3


class TestTSTRepository:
    """Test TST repository operations."""

    def test_get_all_returns_seeded_data(self, repo):
        result = repo.get_all()
        assert len(result) == 9  # LF210 has 9 TST

    def test_get_by_id_found(self, repo):
        result = repo.get_by_id("TST-001")
        assert result is not None
        assert result.tst_code == "LF210"
        assert result.tst_level == 1

    def test_get_by_id_not_found(self, repo):
        result = repo.get_by_id("NONEXISTENT")
        assert result is None

    def test_get_by_id_correct_fields(self, repo):
        result = repo.get_by_id("TST-005")
        assert result.tst_code == "LF212.1"
        assert result.tst_name == "Doi chieu man hinh"
        assert result.tst_level == 3
        assert result.my_parent_task == "TST-004"
        assert result.sla_days == 1

    def test_get_children(self, repo):
        children = repo.get_children("TST-001")
        assert len(children) == 2  # LF211, LF212
        codes = {c.tst_code for c in children}
        assert codes == {"LF211", "LF212"}

    def test_get_children_l2(self, repo):
        children = repo.get_children("TST-004")
        assert len(children) == 5  # LF212.1-5
        assert all(c.tst_level == 3 for c in children)


class TestTSTTree:
    """Test hierarchical tree building."""

    def test_get_tree_root(self, repo):
        tree = repo.get_tree()
        assert len(tree) == 1  # Only LF210 L1
        assert tree[0].tst_code == "LF210"

    def test_get_tree_has_l2_children(self, repo):
        tree = repo.get_tree("TST-001")
        assert len(tree) == 1
        root = tree[0]
        assert len(root.children) == 2  # LF211, LF212

    def test_get_tree_has_l3_children(self, repo):
        tree = repo.get_tree("TST-001")
        root = tree[0]
        lf212 = [c for c in root.children if c.tst_code == "LF212"][0]
        assert len(lf212.children) == 5  # LF212.1-5

    def test_get_tree_full_hierarchy(self, repo):
        tree = repo.get_tree("TST-001")
        root = tree[0]
        # L1: LF210
        assert root.tst_level == 1
        # L2: LF211 has 1 child, LF212 has 5 children
        lf211 = [c for c in root.children if c.tst_code == "LF211"][0]
        lf212 = [c for c in root.children if c.tst_code == "LF212"][0]
        assert len(lf211.children) == 1  # LF211.1
        assert len(lf212.children) == 5  # LF212.1-5
        # L3: leaf nodes
        assert all(len(c.children) == 0 for c in lf212.children)

    def test_get_tree_nonexistent_returns_empty(self, repo):
        tree = repo.get_tree("NONEXISTENT")
        assert tree == []


class TestTSTCRUD:
    """Test create/update/delete operations."""

    def test_create(self, repo):
        new = TST(tst_id="TST-100", tst_code="TEST", tst_name="Test Type", tst_level=1)
        result = repo.create(new)
        assert result.tst_id == "TST-100"
        assert repo.get_by_id("TST-100") is not None

    def test_update(self, repo):
        result = repo.update("TST-001", {"tst_name": "Updated Name"})
        assert result is not None
        assert result.tst_name == "Updated Name"

    def test_update_nonexistent(self, repo):
        result = repo.update("FAKE", {"tst_name": "X"})
        assert result is None

    def test_soft_delete(self, repo):
        assert repo.soft_delete("TST-009") is True
        assert repo.get_by_id("TST-009") is None  # inactive
        assert len(repo.get_all()) == 8  # was 9

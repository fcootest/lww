"""TST repository — SQLite data access layer."""

from typing import Optional
from datetime import datetime
from src.modules.tst.model import TST, TSTTreeNode
from src.config.database import get_db


def _row_to_tst(row) -> TST:
    return TST(
        tst_id=row["tst_id"], tst_code=row["tst_code"], tst_name=row["tst_name"],
        tst_level=row["tst_level"], my_parent_task=row["my_parent_task"],
        description=row["description"], sla_days=row["sla_days"],
        is_active=bool(row["is_active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _tst_to_params(tst: TST) -> dict:
    return {
        "tst_id": tst.tst_id, "tst_code": tst.tst_code, "tst_name": tst.tst_name,
        "tst_level": tst.tst_level, "my_parent_task": tst.my_parent_task,
        "description": tst.description, "sla_days": tst.sla_days,
        "is_active": int(tst.is_active),
        "created_at": tst.created_at.isoformat(), "updated_at": tst.updated_at.isoformat(),
    }


_INS = """INSERT OR IGNORE INTO tst (tst_id, tst_code, tst_name, tst_level, my_parent_task,
    description, sla_days, is_active, created_at, updated_at)
    VALUES (:tst_id, :tst_code, :tst_name, :tst_level, :my_parent_task,
            :description, :sla_days, :is_active, :created_at, :updated_at)"""


class TSTRepository:
    """SQLite TST repository."""

    def seed(self, items: list[TST]):
        db = get_db()
        for item in items:
            db.execute(_INS, _tst_to_params(item))
        db.commit()

    def get_all(self) -> list[TST]:
        return [_row_to_tst(r) for r in get_db().execute("SELECT * FROM tst WHERE is_active=1").fetchall()]

    def get_by_id(self, tst_id: str) -> Optional[TST]:
        row = get_db().execute("SELECT * FROM tst WHERE tst_id=? AND is_active=1", (tst_id,)).fetchone()
        return _row_to_tst(row) if row else None

    def get_children(self, parent_id: str) -> list[TST]:
        return [_row_to_tst(r) for r in get_db().execute(
            "SELECT * FROM tst WHERE my_parent_task=? AND is_active=1", (parent_id,)).fetchall()]

    def get_tree(self, root_id: Optional[str] = None) -> list[TSTTreeNode]:
        if root_id:
            root = self.get_by_id(root_id)
            return [self._build_node(root)] if root else []
        return [self._build_node(r) for r in self.get_all() if r.tst_level == 1]

    def _build_node(self, tst: TST) -> TSTTreeNode:
        children = self.get_children(tst.tst_id)
        return TSTTreeNode(
            tst_id=tst.tst_id, tst_code=tst.tst_code, tst_name=tst.tst_name,
            tst_level=tst.tst_level, my_parent_task=tst.my_parent_task,
            description=tst.description, sla_days=tst.sla_days, is_active=tst.is_active,
            children=[self._build_node(c) for c in children],
        )

    def create(self, tst: TST) -> TST:
        db = get_db()
        db.execute(_INS.replace("OR IGNORE ", ""), _tst_to_params(tst))
        db.commit()
        return tst

    def update(self, tst_id: str, updates: dict) -> Optional[TST]:
        db = get_db()
        row = db.execute("SELECT * FROM tst WHERE tst_id=?", (tst_id,)).fetchone()
        if not row:
            return None
        data = _row_to_tst(row).model_dump()
        data.update(updates)
        data["updated_at"] = datetime.utcnow()
        updated = TST(**data)
        p = _tst_to_params(updated)
        db.execute("""UPDATE tst SET tst_code=:tst_code, tst_name=:tst_name, tst_level=:tst_level,
            my_parent_task=:my_parent_task, description=:description, sla_days=:sla_days,
            is_active=:is_active, updated_at=:updated_at WHERE tst_id=:tst_id""", p)
        db.commit()
        return updated

    def soft_delete(self, tst_id: str) -> bool:
        row = get_db().execute("SELECT 1 FROM tst WHERE tst_id=?", (tst_id,)).fetchone()
        if not row:
            return False
        self.update(tst_id, {"is_active": False})
        return True

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tst")
        db.commit()


tst_repository = TSTRepository()

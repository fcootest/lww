"""Filter Config repository — SQLite data access layer."""

from src.modules.filters.model import TSTFilter, TSTTDT
from src.config.database import get_db


class TSTFilterRepository:
    """SQLite TST_Filter repository."""

    def get_by_tst(self, tst_id: str) -> list[TSTFilter]:
        rows = get_db().execute("SELECT * FROM tst_filter WHERE tst_id=?", (tst_id,)).fetchall()
        return [TSTFilter(tst_id=r["tst_id"], filter_type=r["filter_type"],
                filter_code=r["filter_code"]) for r in rows]

    def exists(self, tst_id: str, filter_type: str, filter_code: str) -> bool:
        return get_db().execute(
            "SELECT 1 FROM tst_filter WHERE tst_id=? AND filter_type=? AND filter_code=?",
            (tst_id, filter_type, filter_code)).fetchone() is not None

    def create(self, item: TSTFilter) -> TSTFilter:
        db = get_db()
        db.execute("INSERT OR IGNORE INTO tst_filter (tst_id, filter_type, filter_code) VALUES (?, ?, ?)",
            (item.tst_id, item.filter_type, item.filter_code))
        db.commit()
        return item

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tst_filter")
        db.commit()


class TSTTDTRepository:
    """SQLite TST_TDT repository."""

    def get_by_tst(self, tst_id: str) -> list[TSTTDT]:
        rows = get_db().execute("SELECT * FROM tst_tdt WHERE tst_id=?", (tst_id,)).fetchall()
        return [TSTTDT(tst_id=r["tst_id"], tdt_id=r["tdt_id"],
                is_required=bool(r["is_required"])) for r in rows]

    def exists(self, tst_id: str, tdt_id: str) -> bool:
        return get_db().execute(
            "SELECT 1 FROM tst_tdt WHERE tst_id=? AND tdt_id=?",
            (tst_id, tdt_id)).fetchone() is not None

    def create(self, item: TSTTDT) -> TSTTDT:
        db = get_db()
        db.execute("INSERT OR IGNORE INTO tst_tdt (tst_id, tdt_id, is_required) VALUES (?, ?, ?)",
            (item.tst_id, item.tdt_id, int(item.is_required)))
        db.commit()
        return item

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tst_tdt")
        db.commit()


tst_filter_repository = TSTFilterRepository()
tst_tdt_repository = TSTTDTRepository()

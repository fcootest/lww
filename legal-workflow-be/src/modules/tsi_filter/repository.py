"""TSI_Filter repository — SQLite data access layer."""

from src.modules.tsi_filter.model import TSIFilter
from src.config.database import get_db


class TSIFilterRepository:
    """SQLite TSI_Filter repository."""

    def get_by_tsi(self, tsi_id: str) -> list[TSIFilter]:
        rows = get_db().execute("SELECT * FROM tsi_filter WHERE tsi_id=?", (tsi_id,)).fetchall()
        return [TSIFilter(id=r["id"], tsi_id=r["tsi_id"],
                filter_type=r["filter_type"], filter_code=r["filter_code"]) for r in rows]

    def create(self, tsi_filter: TSIFilter) -> TSIFilter:
        db = get_db()
        db.execute("INSERT INTO tsi_filter (tsi_id, filter_type, filter_code) VALUES (?, ?, ?)",
            (tsi_filter.tsi_id, tsi_filter.filter_type, tsi_filter.filter_code))
        db.commit()
        row = db.execute("SELECT last_insert_rowid()").fetchone()
        tsi_filter.id = row[0]
        return tsi_filter

    def next_id(self) -> int:
        row = get_db().execute("SELECT COALESCE(MAX(id), 0) + 1 FROM tsi_filter").fetchone()
        return row[0]

    def clear(self):
        db = get_db()
        db.execute("DELETE FROM tsi_filter")
        db.commit()


tsi_filter_repository = TSIFilterRepository()

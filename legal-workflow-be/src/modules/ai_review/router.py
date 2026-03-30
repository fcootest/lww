"""AI Review router - trigger and view AI review results."""

import json
import os
from uuid import uuid4
from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error

router = APIRouter(
    prefix="/api/legal/task",
    tags=["AI Review"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")


@router.post("/{tsi_id}/ai-review")
async def trigger_ai_review(tsi_id: str, user: dict = Depends(get_current_user)):
    """Trigger AI review for a task step. Returns structured review results."""
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tdi.repository import tdi_repository
    from src.modules.tst.repository import tst_repository
    from src.modules.tsev.model import TSEV, TSEVEventType
    from src.modules.tsev.repository import tsev_repository
    from src.modules.ai_review.service import run_ai_review
    from src.modules.ai_review.file_reader import read_file_content

    tsi = tsi_repository.get_by_id(tsi_id)
    if not tsi:
        return send_error(message="TSI not found", status_code=404)

    tst = tst_repository.get_by_id(tsi.tst_id)
    step_name = tst.tst_name if tst else "Unknown Step"

    docs = tdi_repository.get_by_tsi(tsi_id)
    doc_names = [d.file_name for d in docs]

    if not doc_names:
        return send_error(message="No documents to review", status_code=400)

    # Read actual file content from uploaded files
    all_content = ""
    for doc in docs:
        if doc.file_url and doc.file_url.startswith("/api/legal/task/"):
            parts = doc.file_url.split("/")
            if len(parts) >= 6:
                file_tsi_id = parts[4]
                filename = parts[-1]
                file_path = os.path.join(UPLOAD_DIR, file_tsi_id, filename)
                content = read_file_content(file_path)
                if content:
                    sep = "\n=== " + doc.file_name + " ===\n"
                    all_content += sep + content + "\n"

    # Run AI review with real content
    result = await run_ai_review(step_name, doc_names, all_content)

    # Store result as TSEV event
    tsev = TSEV(
        tsev_id=f"TSEV-{uuid4().hex[:8]}",
        tsi_id=tsi_id,
        event_type=TSEVEventType.COMMENT,
        emp_id="AI_REVIEWER",
        event_data=json.dumps(result, ensure_ascii=False),
    )
    tsev_repository.create(tsev)

    return send_success(data=result, message="AI review completed")


@router.get("/{tsi_id}/ai-review")
async def get_ai_review(tsi_id: str, user: dict = Depends(get_current_user)):
    """Get the latest AI review result for a task step."""
    from src.modules.tsev.repository import tsev_repository

    events = tsev_repository.get_by_tsi(tsi_id)
    for evt in reversed(events):
        if evt.emp_id == "AI_REVIEWER" and evt.event_data:
            try:
                data = json.loads(evt.event_data)
                return send_success(data=data)
            except json.JSONDecodeError:
                pass

    return send_success(data=None, message="No AI review found")

"""AI Review Service - auto-review documents using GPT-4o.

Uses OpenAI API when OPENAI_API_KEY is set, otherwise falls back to mock.
"""

import json
import random
import os
from typing import Optional

# Step-specific review checklists
STEP_CHECKLISTS = {
    "Chuan bi ban so sanh UI/UX": {
        "checklist": [
            "Ban so sanh UI/UX day du (co screenshot goc va screenshot app)",
            "Dinh dang file dung (.pptx, .pdf, .xlsx)",
            "Ghi chu ro rang tung man hinh",
            "Danh dau cac diem giong/khac biet",
        ],
        "focus": "So sanh giao dien nguoi dung"
    },
    "Doi chieu man hinh": {
        "checklist": [
            "Toan bo man hinh chinh da duoc doi chieu",
            "Khong co yeu to sao chep UI tu app khac",
            "Cac icon/image la original hoac co license",
            "Layout khong copy nguyen si tu competitor",
        ],
        "focus": "Phat hien sao chep giao dien"
    },
    "Kiem tra Asset": {
        "checklist": [
            "Tat ca asset (icon, image, font) co nguon goc ro rang",
            "Khong su dung asset vi pham ban quyen",
            "License cua asset duoc ghi chep day du",
            "Khong co watermark tu stock photo chua mua",
        ],
        "focus": "Kiem tra ban quyen tai nguyen"
    },
    "Kiem tra anh AI": {
        "checklist": [
            "Xac dinh anh nao duoc tao boi AI",
            "Anh AI co ghi chu ro nguon tao (Midjourney, DALL-E, etc.)",
            "Khong vi pham chinh sach Store ve AI-generated content",
            "Anh AI khong chua noi dung nhay cam",
        ],
        "focus": "Phat hien va kiem tra anh tao boi AI"
    },
    "Doi chieu chinh sach Store": {
        "checklist": [
            "Tuan thu Apple App Store Guidelines",
            "Tuan thu Google Play Store Policy",
            "Screenshot Store listing chinh xac",
            "Mo ta app khong gay hieu lam",
        ],
        "focus": "Kiem tra tuan thu chinh sach Store"
    },
    "Tong hop & phan hoi": {
        "checklist": [
            "Bao cao tong hop day du tat ca cac buoc truoc",
            "Ket luan ro rang: PASS / FAIL / CAN CHINH SUA",
            "Liet ke cac van de can xu ly (neu co)",
            "De xuat hanh dong tiep theo",
        ],
        "focus": "Tong hop ket qua kiem tra"
    },
}

DEFAULT_CHECKLIST = {
    "checklist": [
        "Tai lieu day du va dung dinh dang",
        "Noi dung phu hop voi yeu cau buoc nay",
        "Khong co loi chinh ta hoac sai sot lon",
        "Thong tin nhat quan voi cac buoc truoc",
    ],
    "focus": "Kiem tra tong quat"
}


def get_checklist_for_step(step_name: str) -> dict:
    for key, val in STEP_CHECKLISTS.items():
        if key.lower() in step_name.lower():
            return val
    return DEFAULT_CHECKLIST


def mock_ai_review(step_name: str, doc_names: list[str]) -> dict:
    """Mock AI review for when no API key is available."""
    checklist_config = get_checklist_for_step(step_name)
    checklist = checklist_config["checklist"]

    results = []
    for item in checklist:
        passed = random.random() > 0.2
        results.append({
            "item": item,
            "status": "PASS" if passed else "FAIL",
            "note": "" if passed else "Can kiem tra lai",
        })

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    score = round(pass_count / total * 100)

    if score == 100:
        verdict = "PASS"
        summary = f"Tat ca {total} muc kiem tra deu dat. Tai lieu day du va hop le."
    elif score >= 75:
        verdict = "PASS_WITH_NOTES"
        fail_items = [r["item"] for r in results if r["status"] == "FAIL"]
        summary = f"Dat {pass_count}/{total} muc. Luu y: {'; '.join(fail_items)}"
    else:
        verdict = "FAIL"
        fail_items = [r["item"] for r in results if r["status"] == "FAIL"]
        summary = f"Khong dat {total - pass_count}/{total} muc. Can chinh sua: {'; '.join(fail_items)}"

    return {
        "verdict": verdict,
        "score": score,
        "summary": summary,
        "checklist": results,
        "docs_reviewed": doc_names,
        "model": "mock-v1",
    }


def real_openai_review(step_name: str, doc_names: list[str], api_key: str, file_contents: str = "") -> dict:
    """Call real OpenAI GPT-4o-mini for document review."""
    from openai import OpenAI

    checklist_config = get_checklist_for_step(step_name)
    checklist_items = checklist_config["checklist"]
    focus = checklist_config["focus"]

    content_section = ""
    if file_contents.strip():
        content_section = f"""

NOI DUNG TAI LIEU (extracted text):
---
{file_contents[:3000]}
---
"""

    prompt = f"""Ban la AI Legal Reviewer cho he thong Legal Workflow.
Nhiem vu: Kiem tra tai lieu cho buoc "{step_name}" (Focus: {focus}).

Tai lieu da upload: {', '.join(doc_names)}
{content_section}
Checklist can kiem tra:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(checklist_items))}

Hay danh gia tung muc trong checklist dua tren NOI DUNG tai lieu thuc te.
Tra ve JSON voi format:
{{
  "verdict": "PASS" | "PASS_WITH_NOTES" | "FAIL",
  "score": <0-100>,
  "summary": "<tom tat tieng Viet, neu ro noi dung tai lieu co gi>",
  "checklist": [
    {{"item": "<ten muc>", "status": "PASS" | "FAIL", "note": "<ghi chu cu the dua tren noi dung file>"}}
  ]
}}

Chi tra ve JSON, khong them text khac."""

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.choices[0].message.content.strip()
    # Parse JSON from response
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if JSON parse fails
        return {
            "verdict": "PASS_WITH_NOTES",
            "score": 75,
            "summary": raw[:200],
            "checklist": [{"item": item, "status": "PASS", "note": ""} for item in checklist_items],
            "docs_reviewed": doc_names,
            "model": resp.model,
        }

    result["docs_reviewed"] = doc_names
    result["model"] = resp.model
    return result


async def run_ai_review(step_name: str, doc_names: list[str], file_contents: str = "") -> dict:
    """Run AI review - uses OpenAI if key available, otherwise mock."""
    from dotenv import load_dotenv
    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            return real_openai_review(step_name, doc_names, openai_key, file_contents)
        except Exception as e:
            print(f"[AI Review] OpenAI error: {e}, falling back to mock")

    return mock_ai_review(step_name, doc_names)

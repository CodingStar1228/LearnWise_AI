#!/usr/bin/env python3
"""
Minimal AP/IB textbook ingestion: extract text from PDFs → scaffold course JSON.
Full LLM question extraction can be added later; this creates chapters + sample KP.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTBOOKS = ROOT / "textbooks"
COURSES = ROOT / "data" / "courses"
MAX_PAGES_PER_BOOK = 30


def extract_text_pdfplumber(pdf_path: Path, max_pages: int) -> list[str]:
    try:
        import pdfplumber
    except ImportError:
        return []

    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages[:max_pages]):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text.strip())
    return pages


def slug_from_path(pdf_path: Path) -> str:
    name = pdf_path.stem.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
    return name[:48]


def ingest_book(pdf_path: Path, course_type: str) -> dict:
    pages = extract_text_pdfplumber(pdf_path, MAX_PAGES_PER_BOOK)
    subject_slug = slug_from_path(pdf_path)
    out_dir = COURSES / course_type / subject_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    chapter_id = f"{course_type.lower()}_{subject_slug}_c01"
    kp_id = f"{course_type.lower()}_{subject_slug}_kc01"

    preview = "\n\n".join(pages[:3])[:2000] if pages else f"Placeholder for {pdf_path.name}"

    chapters = [{
        "id": "01",
        "title": pdf_path.stem,
        "parent_id": "",
        "order": 1,
        "description": preview[:500],
        "knowledge_points": [kp_id],
        "sub_chapters": [],
    }]

    knowledgepoints = [{
        "id": kp_id,
        "title": f"Introduction — {pdf_path.stem}",
        "chapter_id": chapter_id,
        "description": preview,
        "summry": preview[:800],
    }]

    questions = [{
        "id": f"{course_type.lower()}_{subject_slug}_q01",
        "title": "Concept check",
        "content": (
            f"Based on the opening of **{pdf_path.stem}**, explain one core idea "
            "in your own words (Feynman style).\nA. ...\nB. ...\nC. ...\nD. ..."
        ),
        "difficulty": 2,
        "type": "concept",
        "knowledge_points": [kp_id],
        "related_questions": [],
        "reference_answer": {
            "content": "Open-ended",
            "key_points": ["Clear definition", "Example or application"],
            "explanation": "Student should articulate the main concept from the textbook opening.",
        },
        "chapter": "01",
    }]

    (out_dir / "knowledgepoints").mkdir(parents=True, exist_ok=True)
    (out_dir / "questions").mkdir(parents=True, exist_ok=True)

    with open(out_dir / "chapters.json", "w", encoding="utf-8") as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    with open(out_dir / "knowledgepoints" / "ch01.json", "w", encoding="utf-8") as f:
        json.dump(knowledgepoints, f, ensure_ascii=False, indent=2)
    with open(out_dir / "questions" / "ch01.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return {
        "pdf": str(pdf_path),
        "out_dir": str(out_dir),
        "pages_extracted": len(pages),
    }


def main():
    results = []
    for course_type in ("AP", "IB"):
        course_dir = TEXTBOOKS / course_type
        if not course_dir.exists():
            continue
        for pdf in sorted(course_dir.glob("*.pdf")):
            results.append(ingest_book(pdf, course_type))

    manifest = COURSES / "manifest.json"
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Ingested {len(results)} books. Manifest: {manifest}")


if __name__ == "__main__":
    main()

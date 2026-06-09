#!/usr/bin/env python3
"""Build minimal SFT jsonl from ds_data questions for EasyEdu Feynman tutoring."""
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = ROOT / "data" / "ds_data" / "questions"
OUT_DIR = ROOT / "data" / "rlhf_data" / "sft"
SYSTEM_ROUTER = (
    "You are the Router Agent in EasyEdu IB/AP Feynman tutoring. "
    "Output ONLY JSON with is_right, is_complete, reason, next_agent."
)
SYSTEM_TEACHER = (
    "You are the Teacher Agent in EasyEdu. Guide the student bilingually (EN+CN), "
    "Feynman style — hints before full answers."
)
SYSTEM_STUDENT = (
    "You are the Student Agent in EasyEdu. Ask one deep Socratic question as a peer learner."
)


def load_all_questions():
    items = []
    for path in sorted(QUESTIONS_DIR.glob("chapter_*.json")):
        with open(path, encoding="utf-8") as f:
            items.extend(json.load(f))
    return items


def sample_router(q, next_agent: str, is_right, is_complete, reason: str):
    user = (
        f"Problem: {q['title']}\n{q['content']}\n\n"
        f"Student says: {q['reference_answer']['content']}"
    )
    return {
        "input": [
            {"role": "system", "content": SYSTEM_ROUTER},
            {"role": "user", "content": user},
        ],
        "output": {
            "role": "assistant",
            "content": json.dumps(
                {
                    "is_right": is_right,
                    "is_complete": is_complete,
                    "reason": reason,
                    "next_agent": next_agent,
                },
                ensure_ascii=False,
            ),
        },
    }


def sample_teacher(q, is_right: bool, is_complete: bool):
    user = f"Problem: {q['content']}\nStudent explanation needs feedback."
    content = (
        f"**Key idea**: {q['reference_answer']['explanation']}\n"
        "Can you walk me through why your approach works step by step? "
        f"（你能逐步说明你的思路吗？）"
    )
    if not is_right:
        content = (
            "Your direction has a gap — what assumption are you making about the structure? "
            f"（你的思路里哪一步可能有问题？）\n"
            f"Hint: {q['reference_answer']['explanation']}"
        )
    return {
        "input": [
            {"role": "system", "content": SYSTEM_TEACHER},
            {"role": "user", "content": user},
        ],
        "output": {"role": "assistant", "content": content},
    }


def sample_student(q):
    user = f"Problem: {q['content']}\nStudent gave a mostly correct but shallow answer."
    content = (
        "That's a good start — but **why** does that property hold in this AP/IB context? "
        "Could you relate it to another concept you've studied? "
        "（为什么在这个情境下成立？能和别的知识点联系起来吗？）"
    )
    return {
        "input": [
            {"role": "system", "content": SYSTEM_STUDENT},
            {"role": "user", "content": user},
        ],
        "output": {"role": "assistant", "content": content},
    }


def main():
    questions = load_all_questions()
    if not questions:
        print("No questions found in ds_data; writing tiny placeholder set.")
        questions = [{
            "title": "Sample",
            "content": "What is 2+2?",
            "reference_answer": {"content": "4", "explanation": "Basic addition."},
        }]

    samples = []
    for q in questions:
        samples.append(sample_router(q, "student", True, False, "Correct MCQ, needs Feynman explanation"))
        samples.append(sample_router(q, "teacher", False, False, "Incorrect explanation"))
        samples.append(sample_teacher(q, False, False))
        samples.append(sample_teacher(q, True, True))
        samples.append(sample_student(q))

    random.shuffle(samples)
    split = max(1, int(len(samples) * 0.9))
    train, val = samples[:split], samples[split:]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "train.jsonl", "w", encoding="utf-8") as f:
        for row in train:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(OUT_DIR / "val.jsonl", "w", encoding="utf-8") as f:
        for row in val:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(train)} train + {len(val)} val samples to {OUT_DIR}")


if __name__ == "__main__":
    main()

# EasyEdu Business Case — IAIO AI for Business

> Product: **EasyEdu** · Team: **LearnWise_AI**

## Target customers
- IB/AP tutoring centers and international schools
- Study-abroad agencies offering structured subject coaching
- B2B edtech platforms needing white-label AI tutoring

## Problem
- Generic chatbots answer questions but do not improve deep understanding
- Commercial LLM APIs: cost scales with usage, data leaves the institution, little customization
- Teachers lack scalable tools for "explain the problem" classroom practice

## Solution — EasyEdu
- **Feynman loop**: student explains → Router evaluates → Student probes or Teacher corrects/summarizes
- **Own model stack**: QLoRA fine-tune on 4090 + vLLM self-hosting (`docs/MODEL_SERVING.md`, `docs/TRAINING.md`)
- **IB/AP content path**: textbook ingestion → structured course bank (`scripts/ingest_textbooks.py`)
- **Bilingual**: English-first AP/IB terms + Chinese support for mixed classrooms

## Why it wins for business
| Dimension | Commercial API tutor | EasyEdu |
|-----------|---------------------|---------|
| Cost | Per-token, grows with seats | Fixed GPU + optional API fallback |
| Data | Third-party cloud | On-prem / private cloud |
| Pedagogy | Q&A | Explain-to-learn + multi-agent |
| Curriculum | Generic | AP/IB textbooks → custom bank |

## Demo flow (competition)
1. Select course / chapter / problem
2. Student explains solution in chat
3. Show Router JSON decision (optional debug)
4. Student or Teacher agent responds bilingually
5. Highlight: runs on **your** model endpoint (`LEARNWISE_LLM_BACKEND=local_vllm`)

## Go-to-market (light)
- Pilot with one AP subject (e.g. Statistics) + one IB subject (Math AA HL)
- Package: software + model weights + ingestion for institution's licensed textbooks
- Metrics: session completion, explanation depth (router `is_complete`), teacher time saved

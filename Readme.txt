# ScribeXAgent

**Multi-agent AI scribe for  clinical visits** — real-time transcription, speaker diarization, SOAP note generation, and EPIC/FHIR integration. Built entirely offline — no PHI leaves the machine.

---

## The Problem

A  doctor sees 20 patients a day × 30 minutes each.  
After every visit: manual transcription → SOAP note → EHR upload.  
**400+ minutes of documentation per day** — on top of patient care.

Existing tools fail because they either require cloud (PHI can't leave the clinic), don't handle multiple speakers, or produce notes that need more editing than writing from scratch.

---

## Requirements Discovery First

Before writing code, a structured clinical requirements analysis defined what to build:

| Question | Answer |
|---|---|
| Who reviews the output? | Doctor approves, patient edits history only |
| How many speakers per visit? | Doctor + patient (child) + parent(s) |
| Real-time or post-processing? | Both |
| Data leave the machine? | Never |
| Output format? | FHIR R4 → EPIC EHR |
| Transcription accuracy target? | 95% |
| Languages? | English, Spanish, French |

This is why diarization is not optional — a doctor visit has 3+ speakers and the SOAP note must correctly attribute who said what.

---

## v1 — Single Agent (`scribex`)

The first version proved the concept with a simple linear pipeline:

```
🎙️ Audio → Whisper ASR → Single LLM call → SOAP note → Doctor review → PDF + SQLite
```

**It worked. And it showed exactly what breaks at scale:**

```
❌ No speaker diarization   → doctor and patient voices mixed in SOAP sections
❌ One LLM does everything  → mediocre transcription + extraction + formatting
❌ No stage checkpoints     → noisy audio fails the entire pipeline silently
```

These three failures directly shaped the multi-agent architecture.  
→ [scribex (v1)](https://github.com/Umanagendra-M/scribex)

---

## v2 — Multi-Agent Architecture (This Repository)

Each failure from v1 became a dedicated agent:

```
                    🎙️  Audio Input
                         │
              ┌──────────▼──────────┐
              │  TranscriptionAgent  │  Whisper ASR + medical vocabulary
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  DiarizationAgent    │  pyannote — who said what
              │  (doctor / patient   │
              │   / parent / child)  │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  ExtractionAgent     │  symptoms, diagnoses, meds
              │                      │  ICD-10 code suggestions
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  SOAPAgent           │  structures S/O/A/P sections
              │                      │  specialty-aware templates
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  ReviewAgent         │  doctor approves
              │                      │  patient edits history only
              │                      │  medications + assessment locked
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  ExportAgent         │  FHIR R4 bundle → EPIC
              │                      │  PDF copy + audit log
              └─────────────────────┘
```

Orchestrated with **LangGraph** — explicit state transitions between agents, retry per stage, no silent failures.

---

## v1 → v2 Comparison

```
scribex (v1)              ScribeXAgent (v2)
────────────────          ──────────────────────────
Single LLM call      →    Specialized agent per task
No diarization       →    DiarizationAgent (pyannote)
Sequential, brittle  →    LangGraph state machine
WAV file only        →    Real-time mic + file input
PDF only             →    FHIR R4 → EPIC integration
English only         →    English, Spanish, French
SQLite               →    PostgreSQL + full audit trail
```

---

## SOAP Output Format

```
S — Subjective    patient-reported symptoms     ✏️ patient can edit
O — Objective     doctor's clinical findings    🔒 locked
A — Assessment    diagnosis                     🔒 locked
P — Plan          treatment plan                🔒 locked
```

---

## Stack

```
Agent Orchestration   LangGraph
Speech Recognition    Whisper (local, offline)
Speaker Diarization   pyannote.audio
Clinical NLP          spaCy + medical entity models
LLM Inference         Ollama (local)
FHIR Integration      fhir.resources + EPIC FHIR API
Storage               PostgreSQL + SQLite
UI                    Streamlit
Containerization      Docker
Language              Python 3.11
```

---

## Scale Profile

```
Patients/day    20
Audio/visit     ~30 min WAV
Notes/day       20 SOAP notes (~10MB each)
Hardware        Windows, 16GB RAM
GPU             Optional
Offline         Yes — no internet required
```

---

## Quickstart

```bash
git clone https://github.com/Umanagendra-M/ScribeXAgent.git
cd ScribeXAgent
cp .env.example .env
docker compose up -d
# open http://localhost:8501
```

---

## Roadmap

```
v1.0  ✅  Single agent SOAP pipeline (scribex)
v2.0  🔄  Multi-agent LangGraph pipeline (this repo)
v2.1  ⬜  EPIC FHIR integration
v2.2  ⬜  ICD-10 code suggestions
v2.3  ⬜  Learning from doctor corrections (LoRA fine-tuning)
v3.0  ⬜  Multi-clinic deployment
```

---

## Author

**Umanagendra M** — ML/AI Engineer, 8 years in production NLP and GenAI.  
Previously built clinical NLP pipelines at Carelon/Elevance Health.

[GitHub](https://github.com/Umanagendra-M) · [scribex v1](https://github.com/Umanagendra-M/scribex)

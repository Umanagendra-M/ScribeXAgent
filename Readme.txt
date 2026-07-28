# ScribeX

**AI scribe for pediatric clinical visits** — converts doctor-patient audio into structured SOAP notes, locally, offline, with no PHI leaving the machine.

---

## The Problem

A pediatrician sees 20 patients a day × 30 min each.  
After every visit: manual transcription → SOAP note → EHR upload.  
That's **400+ minutes of documentation per day** — time that should go to patients.

Existing tools either require cloud (PHI can't leave the clinic) or produce notes that need more editing than writing from scratch.

---

## How It Works

```
  🎙️ Audio (mic / phone / WAV file)
         │
         ▼
  ┌─────────────────┐
  │  Whisper ASR    │  local transcription, no cloud
  └────────┬────────┘
           │  raw transcript
           ▼
  ┌─────────────────┐
  │  LLM (Ollama)   │  SOAP note generation
  └────────┬────────┘
           │  structured note
           ▼
  ┌─────────────────┐
  │  Doctor Review  │  approve / edit
  └────────┬────────┘
           │  approved
           ▼
  ┌─────────────────┐
  │  PDF + SQLite   │  export + store locally
  └─────────────────┘
```

---

## SOAP Output Format

```
S — Subjective   patient-reported symptoms (editable by patient)
O — Objective    doctor's clinical observations (locked)
A — Assessment   diagnosis (locked)
P — Plan         treatment plan (locked)
```

Role-based editing: patients can update their history. Medications and assessment are locked after doctor approval.

---

## Built For

```
Clinic type:    Pediatric inpatient
Patients/day:   20
Visit length:   ~30 minutes
Languages:      English  (Spanish, French planned)
Hardware:       Windows, 16GB RAM, no GPU required
Data policy:    100% offline — nothing leaves the machine
```

---

## Stack

```
Transcription   Whisper (local)
SOAP generation Ollama LLM
Storage         SQLite
UI              Streamlit
Language        Python 3.11
```

---

## Quickstart

```bash
git clone https://github.com/Umanagendra-M/scribex.git
cd scribex
pip install -r requirements.txt
cp .env.example .env
streamlit run src/app.py
```

Drop a WAV file in `data/` or connect a mic. The system transcribes, generates the SOAP note, and presents it for doctor review.

---

## What This Version Taught Me

Building v1 with a single LLM pipeline revealed three hard limits:

```
❌  No speaker diarization
    → Can't tell doctor from patient from parent
    → Subjective / Objective sections get mixed up

❌  Single LLM call for everything
    → Transcription + extraction + formatting = mediocre at all three
    → Specialized models per task outperform one general call

❌  No retry per stage
    → If transcription is noisy, the whole pipeline fails
    → No checkpoint between stages
```

These three observations drove the multi-agent redesign.

---

## What Comes Next

**[ScribeXAgent →](https://github.com/Umanagendra-M/ScribeXAgent)** — v2 built with LangGraph, one agent per concern.

```
scribex (this repo)          ScribeXAgent (v2)
──────────────────           ──────────────────────
Single LLM call         →    Specialized agents per task
No diarization          →    DiarizationAgent (pyannote)
Sequential pipeline     →    LangGraph state machine
WAV file only           →    Real-time + file input
PDF only                →    FHIR R4 + EPIC integration
English only            →    English, Spanish, French
```

v1 proved the concept. v2 solves what v1 exposed.

---

## Author

**Umanagendra M** — ML/AI Engineer, 8 years in production NLP and GenAI.  
Previously built clinical NLP pipelines at Carelon/Elevance Health.

[GitHub](https://github.com/Umanagendra-M) · [ScribeXAgent](https://github.com/Umanagendra-M/ScribeXAgent)

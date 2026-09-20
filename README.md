# AgentCare 🩺

**AgentCare** is a multi-agent AI clinical decision support system for **Type-2 Diabetes management**.

> ⚠️ **MANDATORY SAFETY DISCLAIMER**: AgentCare does **NOT** diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only by organizing health records, summarizing medical history, interpreting prescriptions, translating clinical instructions into patient-friendly language, and generating reminders.

---

## 🏗️ Multi-Agent System Architecture

AgentCare leverages **5 specialized AI agents** built on top of a common safety-constrained base framework:

```
                              ┌───────────────────────────────────┐
                              │           AgentCare API           │
                              │        FastAPI + SQLAlchemy       │
                              └─────────────────┬─────────────────┘
                                                │
       ┌──────────────────┬─────────────────────┼─────────────────────┬──────────────────┐
       │                  │                     │                     │                  │
┌──────▼──────────┐┌──────▼───────────┐ ┌───────▼───────────┐ ┌───────▼───────────┐ ┌──────▼───────────┐
│ Record Organizer││History Summarizer│ │    Prescription   │ │   Communication   │ │     Reminder     │
│      Agent      ││      Agent       │ │ Interpreter Agent │ │ Translator Agent  │ │  Generator Agent │
└─────────────────┘└──────────────────┘ └───────────────────┘ └───────────────────┘ └──────────────────┘
  Extracts labs      Synthesizes HbA1c    Explains Metformin    Translates clinical  Schedules glucose &
  & glucose logs     glycemic trends      dosage & side effects targets into plain   medication check-
  into JSON DB       longitudinally       non-prescriptively    everyday language    in reminders
```

1. **Health Record Organizer Agent** ([`record_organizer.py`](file:///Users/rahulvoruganti/Desktop/ai_mini/backend/agents/record_organizer.py)): Extracts structured records (`hba1c`, `blood_glucose`, `medication`, `lifestyle`) from raw reports into JSON database objects.
2. **History Summarizer Agent** ([`history_summarizer.py`](file:///Users/rahulvoruganti/Desktop/ai_mini/backend/agents/history_summarizer.py)): Synthesizes longitudinal patient records into concise summaries covering HbA1c trends, blood glucose patterns, and adherence.
3. **Prescription Interpreter Agent** ([`prescription_interpreter.py`](file:///Users/rahulvoruganti/Desktop/ai_mini/backend/agents/prescription_interpreter.py)): Explains prescribed Type-2 Diabetes medications in simple terms (what it is for, how to take it, common side effects) without altering dosages.
4. **Communication Translator Agent** ([`communication_translator.py`](file:///Users/rahulvoruganti/Desktop/ai_mini/backend/agents/communication_translator.py)): Translates complex clinical targets and care plans into simple, encouraging, everyday patient language.
5. **Reminder Generator Agent** ([`reminder_generator.py`](file:///Users/rahulvoruganti/Desktop/ai_mini/backend/agents/reminder_generator.py)): Creates structured reminders for glucose checks, medication times, and lifestyle activities.

---

## 🔒 Safety & Audit Compliance

- **Non-Diagnostic Constraint**: System prompts and test assertions enforce strict boundaries preventing diagnostic or prescriptive outputs.
- **Pytest Safety Suite**: Includes unit tests ([`test_agents.py`](file:///Users/rahulvoruganti/Desktop/ai_mini/backend/tests/test_agents.py)) verifying safety compliance.
- **Audit Middleware**: Every request and LLM invocation is logged via [`AuditLoggingMiddleware`](file:///Users/rahulvoruganti/Desktop/ai_mini/backend/app/middleware/audit_logging.py) and tagged with `X-Safety-Disclaimer` headers.
- **Role-Based Access Control (RBAC)**: Clinicians can access all patient profiles; patients can only access their own profile.

---

## 🛠️ Project Structure

```
ai_mini/
├── backend/
│   ├── agents/                     # 5 Multi-Agent AI Modules
│   │   ├── base_agent.py           # BaseAgent class with safety prompt & JSON parser
│   │   ├── record_organizer.py     # Record Organizer Agent
│   │   ├── history_summarizer.py   # History Summarizer Agent
│   │   ├── prescription_interpreter.py # Prescription Interpreter Agent
│   │   ├── communication_translator.py  # Communication Translator Agent
│   │   └── reminder_generator.py   # Reminder Generator Agent
│   ├── app/
│   │   ├── api/                    # FastAPI APIRouters (/auth, /patients, /reminders)
│   │   ├── core/                   # Security (JWT, bcrypt) & Settings
│   │   ├── db/                     # SQLAlchemy SQLite Session & Engine
│   │   ├── middleware/             # Audit Logging Middleware
│   │   ├── models/                 # User, PatientProfile, DiabetesRecord, Medication, Reminder
│   │   └── schemas/                # Pydantic Request/Response validation schemas
│   ├── tests/                      # Pytest safety test suite
│   ├── seed_data.py                # Database seeder (synthetic Type-2 Diabetes dataset)
│   └── main.py                     # FastAPI application entry point
├── frontend/                       # React + Vite + TypeScript + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/             # DisclaimerBanner component
│   │   ├── pages/                  # Login, ClinicianDashboard, PatientPortal
│   │   ├── services/               # Axios API client with JWT interceptor
│   │   └── App.tsx                 # React Router configuration
│   └── vite.config.ts              # Vite server & API proxy config
├── .env.example                    # Environment variable template
├── seed_data.py                    # Root seed runner
└── README.md                       # Project documentation
```

---

## 🚀 Setup & Execution Guide

### 1. Environment Configuration

Copy `.env.example` to `.env` and configure credentials:

```bash
cp .env.example .env
```

*(Note: If `OPENAI_API_KEY` is omitted or left as placeholder, the system automatically runs using deterministic offline rule fallback mode).*

---

### 2. Backend Setup & Seeding

```bash
# Navigate to backend
cd backend

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
pip install pytest

# Seed database with synthetic Type-2 Diabetes patient records
python seed_data.py

# Run Pytest safety test suite
PYTHONPATH=. pytest tests/test_agents.py

# Start FastAPI server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API docs are accessible at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

### 3. Frontend Setup

In a separate terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

The application will run at [http://localhost:5173](http://localhost:5173).

---

## 🎬 Interactive Demo Flow

### 👨‍⚕️ Clinician Walkthrough (`dr_jenkins` / `clinician123`)
1. Open [http://localhost:5173](http://localhost:5173) and click **Clinician Demo**.
2. **Organized Records Tab**: View structured HbA1c (7.5%), fasting & postprandial glucose logs, and medical history.
3. **AI History Summary Tab**: Click *Generate New Summary* to invoke **History Summarizer Agent**.
4. **Prescription Interpreter Tab**: Click *Run Interpreter Agent* to view plain-language Metformin dosage guides.
5. **Patient Reminders Tab**: Click *Generate Agent Reminders* to trigger **Reminder Generator Agent**.

### 👤 Patient Walkthrough (`john_doe` / `patient123`)
1. Log in as **Patient Demo**.
2. **Your Type-2 Diabetes Guidance**: View translated care targets generated by **Communication Translator Agent**.
3. **My Reminders Checklist**: View active reminders and check off completed medication/glucose checks.
4. **Upload New Health Record**: Paste a raw report (e.g., `"HbA1c: 7.4% on 2025-02-01. Blood glucose: 130 mg/dL"`) and click *Submit*. The **Health Record Organizer Agent** parses and inserts structured records in real time.

"""
Patients API Router for AgentCare Type-2 Diabetes Decision Support System.

DISCLAIMER: AgentCare does not diagnose Type-2 Diabetes or prescribe treatment.
It assists clinicians and patients only.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from io import BytesIO
from pathlib import Path
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User, PatientProfile
from app.models.diabetes_record import DiabetesRecord
from app.models.medication import Medication
from app.models.reminder import Reminder
from app.api.deps import get_current_user, verify_patient_access
from app.schemas.diabetes_record import RecordUploadRequest, DiabetesRecordListResponse, DiabetesRecordSchema
from app.schemas.medication import PrescriptionInterpretationResponse, MedicationSchema
from app.schemas.reminder import ReminderListResponse, ReminderSchema

# Import Multi-Agent suite
from agents.record_organizer import RecordOrganizerAgent
from agents.history_summarizer import HistorySummarizerAgent
from agents.prescription_interpreter import PrescriptionInterpreterAgent
from agents.communication_translator import CommunicationTranslatorAgent
from agents.reminder_generator import ReminderGeneratorAgent

router = APIRouter(prefix="/patients", tags=["Patients & Multi-Agent Operations"])

SAFETY_DISCLAIMER = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."

# Initialize agents
record_organizer_agent = RecordOrganizerAgent()
history_summarizer_agent = HistorySummarizerAgent()
prescription_interpreter_agent = PrescriptionInterpreterAgent()
communication_translator_agent = CommunicationTranslatorAgent()
reminder_generator_agent = ReminderGeneratorAgent()


@router.get("/{id}/records", response_model=DiabetesRecordListResponse)
def get_patient_records(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns list of DiabetesRecords for a patient. Requires RBAC verification.
    """
    verify_patient_access(id, current_user, db)
    
    records = db.query(DiabetesRecord).filter(DiabetesRecord.patient_id == id).order_by(DiabetesRecord.date.desc()).all()
    return DiabetesRecordListResponse(
        records=records,
        disclaimer=SAFETY_DISCLAIMER,
    )


@router.post("/{id}/records/upload", response_model=DiabetesRecordListResponse)
async def upload_patient_record(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Uploads raw clinical report text, invokes Record Organizer Agent to extract structured
    Type-2 Diabetes data, saves parsed records into the database, and returns structured records.
    """
    verify_patient_access(id, current_user, db)
    
    patient = db.query(PatientProfile).filter(PatientProfile.id == id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    extracted_text = None
    file = None
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        raw_form_text = form.get("raw_text")
        extracted_text = raw_form_text if isinstance(raw_form_text, str) else None
        uploaded_file = form.get("file")
        file = uploaded_file if hasattr(uploaded_file, "read") and hasattr(uploaded_file, "filename") else None
    else:
        body = RecordUploadRequest.model_validate(await request.json())
        extracted_text = body.raw_text

    if file:
        file_bytes = await file.read()
        try:
            if file.content_type == "application/pdf" or Path(file.filename or "").suffix.lower() == ".pdf":
                pages = convert_from_bytes(file_bytes)
                extracted_text = "\n".join(pytesseract.image_to_string(page) for page in pages)
            elif file.content_type and file.content_type.startswith("image/"):
                extracted_text = pytesseract.image_to_string(Image.open(BytesIO(file_bytes)))
            else:
                raise HTTPException(status_code=400, detail="Only image and PDF files are supported.")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Unable to extract text from the uploaded record: {exc}")

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Provide record text or upload an image/PDF record.")

    # Invoke Health Record Organizer Agent
    extracted_records = record_organizer_agent.organize_records(extracted_text)
    
    saved_models = []
    for item in extracted_records:
        rec_date = datetime.utcnow()
        if item.get("date"):
            try:
                rec_date = datetime.strptime(item["date"], "%Y-%m-%d")
            except Exception:
                rec_date = datetime.utcnow()

        record_model = DiabetesRecord(
            patient_id=id,
            record_type=item.get("record_type", "raw"),
            value=item.get("value"),
            unit=item.get("unit"),
            date=rec_date,
            notes=item.get("notes"),
            raw_text=extracted_text,
        )
        db.add(record_model)
        saved_models.append(record_model)

    db.commit()
    for m in saved_models:
        db.refresh(m)

    return DiabetesRecordListResponse(
        records=saved_models,
        disclaimer=SAFETY_DISCLAIMER,
    )


@router.get("/{id}/summary")
def get_patient_summary(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetches all records for a patient, invokes History Summarizer Agent,
    and returns concise Type-2 Diabetes history summary.
    """
    verify_patient_access(id, current_user, db)
    
    records = db.query(DiabetesRecord).filter(DiabetesRecord.patient_id == id).all()
    summary = history_summarizer_agent.summarize_history(records)
    
    return {
        "patient_id": id,
        "summary": summary,
        "disclaimer": SAFETY_DISCLAIMER,
    }


@router.get("/{id}/prescriptions/interpret", response_model=PrescriptionInterpretationResponse)
def interpret_patient_prescriptions(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetches current medications for patient and invokes Prescription Interpreter Agent
    to provide plain-language explanations.
    """
    verify_patient_access(id, current_user, db)
    
    medications = db.query(Medication).filter(Medication.patient_id == id).all()
    explanation = prescription_interpreter_agent.interpret_prescriptions(medications)
    
    return PrescriptionInterpretationResponse(
        medications=medications,
        explanation=explanation,
        disclaimer=SAFETY_DISCLAIMER,
    )


@router.get("/{id}/instructions/translate")
def translate_patient_instructions(
    id: int,
    instructions: Optional[str] = None,
    language: str = "en-IN",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invokes Communication Translator Agent to translate clinical directives into simple, patient-friendly guidance.
    """
    verify_patient_access(id, current_user, db)
    
    profile = db.query(PatientProfile).filter(PatientProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    if not instructions:
        instructions = (
            f"Clinical Targets for Type-2 Diabetes Management: Target HbA1c is {profile.target_hba1c}%. "
            "Self-monitor fasting blood glucose daily prior to breakfast. Continue Metformin 500mg BID with meals. "
            "Engage in 30 minutes of moderate physical exercise 4x/week."
        )

    supported_languages = {"en-IN", "hi-IN", "te-IN"}
    if language not in supported_languages:
        raise HTTPException(status_code=400, detail="Language must be en-IN, hi-IN, or te-IN.")

    translation = communication_translator_agent.translate_instructions(instructions, language)
    
    return {
        "patient_id": id,
        "original_instructions": instructions,
        "translated_instructions": translation,
        "language": language,
        "disclaimer": SAFETY_DISCLAIMER,
    }


@router.get("/{id}/reminders", response_model=ReminderListResponse)
def get_patient_reminders(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns list of active reminders for a patient.
    """
    verify_patient_access(id, current_user, db)
    
    reminders = db.query(Reminder).filter(Reminder.patient_id == id).order_by(Reminder.scheduled_time.asc()).all()
    return ReminderListResponse(
        reminders=reminders,
        disclaimer=SAFETY_DISCLAIMER,
    )


@router.post("/{id}/reminders/generate", response_model=ReminderListResponse)
def generate_patient_reminders(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invokes Reminder Generator Agent using patient's current medications & care plan,
    saves generated reminders to the database, and returns them.
    """
    verify_patient_access(id, current_user, db)
    
    medications = db.query(Medication).filter(Medication.patient_id == id).all()
    profile = db.query(PatientProfile).filter(PatientProfile.id == id).first()

    context = f"Patient Target HbA1c: {profile.target_hba1c if profile else 7.0}%\nMedications:\n"
    for m in medications:
        context += f"- {m.name} {m.dosage}, {m.frequency}\n"

    generated_items = reminder_generator_agent.generate_reminders(context)
    
    created_reminders = []
    for item in generated_items:
        sched_time = datetime.utcnow()
        if item.get("scheduled_time"):
            try:
                sched_time = datetime.fromisoformat(item["scheduled_time"].replace("Z", "+00:00"))
            except Exception:
                sched_time = datetime.utcnow()

        reminder_model = Reminder(
            patient_id=id,
            reminder_type=item.get("reminder_type", "medication"),
            message=item.get("message", "Type-2 Diabetes monitoring reminder"),
            scheduled_time=sched_time,
            is_completed=False,
        )
        db.add(reminder_model)
        created_reminders.append(reminder_model)

    db.commit()
    for r in created_reminders:
        db.refresh(r)

    return ReminderListResponse(
        reminders=created_reminders,
        disclaimer=SAFETY_DISCLAIMER,
    )

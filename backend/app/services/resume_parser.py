# app/services/resume_parser.py

import os
import json
import logging
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from transformers import pipeline
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import pdfplumber
import docx
import re
from app.models.resume import Resume as ResumeModel
from app.schemas.resume import ResumeStatus, FileType

logger = logging.getLogger(__name__)

# ─── Initialization ───────────────────────────────────────────────────────────
load_dotenv()  # reads .env in project root

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Single-instance HF NER pipeline
hf_ner = pipeline("ner", grouped_entities=True)


# ─── Public API ────────────────────────────────────────────────────────────────
def parse_and_store_resume(file_path: str, user_id: int, db: Session) -> ResumeModel:
    """
    Orchestrates:
      1) Text extraction
      2) LLM parse (Gemini → fallback)
      3) Mandatory field validation
      4) ORM mapping & persistence
    """
    text = _extract_text(file_path)
    parsed = _parse_with_gemini(text)
    if not parsed:
        logger.warning("Gemini parse empty or failed, using HF fallback")
        parsed = _fallback_parse(text)

    _validate_mandatory(parsed, fields=("experience", "education", "skills"))

    resume = _map_to_model(parsed, user_id, file_path)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


# ─── Internal Helpers ──────────────────────────────────────────────────────────
def _extract_text(file_path: str) -> str:
    ext = file_path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif ext == "docx":
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported extension for parsing: .{ext}")


def _parse_with_gemini(text: str) -> Dict[str, Any]:
    prompt = (
            "You are a professional resume parser. Extract structured resume data from the provided raw text.\n"
            "Return ONLY valid JSON with exactly the following fields:\n"
            "- name (string)\n"
            "- email (string)\n"
            "- phone (string)\n"
            "- summary (string)\n"
            "- inferred_role (string) – if not explicitly stated, infer from summary of Resume \n"
            "- skills (array of strings)\n"
            "- education (array of objects with: degree, university, start_date, end_date, cgpa, certification, institution, date)\n"
            "- experience (array of objects with: job_title, company, start_date, end_date, description)\n"
            "- job_titles (array of strings)\n"
            "- years_of_experience (float) – calculate based on job start/end dates\n"
            "- confidence_score (float between 0.0 and 1.0 – your parsing confidence)\n"
            "- processing_time (float in seconds – your total processing time)\n\n"

            "INSTRUCTIONS:\n"
            "• If a field is missing, use null or an empty array ([]).\n"
            "• Do not include any explanations, markdown, or extra formatting.\n"
            "• Return ONLY valid parsable JSON – not a code block or narrative.\n"
            "• Use your best judgment to summarize and infer fields if not explicitly written (e.g. summary).\n\n"

            # Optional: Embed a mini example to reinforce structure
            "Example:\n"
            "{\n"
            "  \"name\": \"Jane Doe\",\n"
            "  \"email\": \"jane.doe@example.com\",\n"
            "  \"phone\": \"+123456789\",\n"
            "  \"summary\": \"Experienced Data Scientist with a strong background in machine learning and analytics.\",\n"
            "\"inferred_role\": \"ML Engineer\",\n"
            "  \"skills\": [\"Python\", \"Machine Learning\", \"SQL\"],\n"
            "  \"education\": [\n"
            "    {\n"
            "      \"degree\": \"BSc Computer Science\",\n"
            "      \"university\": \"University of Example\",\n"
            "      \"start_date\": \"2015\",\n"
            "      \"end_date\": \"2019\",\n"
            "      \"cgpa\": \"3.8\",\n"
            "      \"certification\": null,\n"
            "      \"institution\": null,\n"
            "      \"date\": null\n"
            "    }\n"
            "  ],\n"
            "  \"experience\": [\n"
            "    {\n"
            "      \"job_title\": \"Data Analyst\",\n"
            "      \"company\": \"TechCorp\",\n"
            "      \"start_date\": \"2020\",\n"
            "      \"end_date\": \"2023\",\n"
            "      \"description\": \"Worked on predictive modeling and business intelligence dashboards.\"\n"
            "    }\n"
            "  ],\n"
            "  \"job_titles\": [\"Data Analyst\"],\n"
            "  \"years_of_experience\": 3.0,\n"
            "  \"confidence_score\": 0.92,\n"
            "  \"processing_time\": 1.5\n"
            "}\n\n"
            f"TEXT:\n{text}"
)

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )

    
        raw_text = response.text if response.text is not None else ""
        raw = raw_text.strip()

        cleaned = clean_gemini_json(raw_text)
        
        #  JSON extraction
        return json.loads(cleaned)
    except json.JSONDecodeError as je:
        logger.error("JSON decode error: %s", je)
    except Exception as e:
        logger.error("Gemini API error: %s", e, exc_info=True)

    return {}


def _fallback_parse(text: str) -> Dict[str, Any]:
    """
    Simple fallback: extract entities via HF NER and
    bucket them into skills, job_titles, etc.
    """
    entities = hf_ner(text)
    parsed = {
        "name": None,
        "email": None,
        "phone": None,
        "skills": [],
        "education": [],
        "experience": None,
        "job_titles": [],
        "years_of_experience": None
    }

    if entities:
        for ent in entities:
            if isinstance(ent, dict):
                label = ent.get("entity_group")
                word = ent.get("word")
            else:
                # fallback: try attribute access or skip
                label = getattr(ent, "entity_group", None)
                word = getattr(ent, "word", None)
            if label == "SKILL":
                parsed["skills"].append(word)
            elif label == "ORG":
                parsed["education"].append(word)
            elif label == "PER":
                parsed["name"] = parsed["name"] or word
            # you can expand phone/email/date extraction here

    return parsed


def _validate_mandatory(parsed: Dict[str, Any], fields: tuple):
    for f in fields:
        val = parsed.get(f)
        if not val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mandatory field '{f}' is missing or empty."
            )


def _map_to_model(parsed: Dict[str, Any], user_id: int, file_path: str) -> ResumeModel:
    return  ResumeModel(
    user_id=user_id,
    title=parsed.get("name") or os.path.basename(file_path),
    description=parsed.get("summary"),            # if you generate one
    file_path=file_path,
    inferred_role=parsed.get("inferred_role"),
    file_name=os.path.basename(file_path),
    file_size=os.path.getsize(file_path),
    file_type=FileType[file_path.rsplit(".",1)[-1].upper()],
    status=ResumeStatus.ANALYZED,
    analysis=parsed,                               # your parsed dict
    confidence_score=parsed.get("confidence_score"),
    processing_time=parsed.get("processing_time"),
)
    

def clean_gemini_json(raw: str) -> str:
    return re.sub(r"```(?:json)?|```", "", raw).strip()
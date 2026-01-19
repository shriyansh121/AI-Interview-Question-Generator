"""
Resume parser for extracting candidate information.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
# from pdf2image import convert_from_path
# import pytesseract
import PyPDF2
import docx
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config.settings import settings
from src.utils.logger import setup_logger


logger = setup_logger(
    name="resume_parser",
    log_dir="logs/resume_parser",
)


class ResumeParser:
    def __init__(self):
        # Regex patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        self.linkedin_pattern = r'linkedin\.com/in/[\w-]+'

        # -------- LLM INITIALIZATION (CONFIG-DRIVEN) --------
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.get("llm.model"),
            temperature=settings.get("llm.temperature", 0.7),
            max_tokens=settings.get("llm.max_tokens", 2048),
        )

    # =========================
    # PUBLIC API
    # =========================

    def parse(self, file_path: str) -> Dict[str, any]:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        logger.info(f"Parsing resume: {file_path}")

        if file_path.suffix.lower() == ".pdf":
            text = self._extract_from_pdf(file_path)
        elif file_path.suffix.lower() == ".docx":
            text = self._extract_from_docx(file_path)
        elif file_path.suffix.lower() == ".txt":
            text = self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        summary_text = text[:1500]  # enough for role inference

        job_role = self._extract_job_role(summary_text)
        skills = self._extract_skills(text, job_role)

        info = {
            "raw_text": text,
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "linkedin_url": self._extract_linkedin(text),
            "github_url": self._extract_github(text),
            "portfolio_url": self._extract_portfolio(text),
            "job_role": job_role,
            "skills": skills,
            "experience": self._estimate_experience(text),
            "education": self._extract_education(text),
        }

        logger.info(f"Resume parsed successfully for role: {job_role}")
        return info

    # =========================
    # FILE EXTRACTION
    # =========================

    def _extract_from_pdf(self, file_path: Path) -> str:
        text = ""

        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted

        # ---------- OCR FALLBACK ----------
        if not text.strip():
            logger.warning("No extractable text found using PyPDF2")
            text = self._extract_from_pdf_ocr(file_path)

        return text

    def _extract_from_docx(self, file_path: Path) -> str:
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    def _extract_from_txt(self, file_path: Path) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # =========================
    # BASIC EXTRACTION
    # =========================

    def _extract_email(self, text: str) -> Optional[str]:
        matches = re.findall(self.email_pattern, text)
        return matches[0] if matches else None

    def _extract_phone(self, text: str) -> Optional[str]:
        match = re.search(self.phone_pattern, text)
        return match.group() if match else None

    def _extract_linkedin(self, text: str) -> Optional[str]:
        match = re.search(self.linkedin_pattern, text, re.IGNORECASE)
        if match:
            return f"https://{match.group()}"
        return None

    def _extract_name(self, text: str) -> Optional[str]:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return lines[0] if lines else None

    # =========================
    # EXPERIENCE CALCULATION
    # =========================

    def _estimate_experience(self, text: str) -> str:
        calculated = self._experience_from_dates(text)
        mentioned = self._experience_from_mentions(text)

        valid = [m for m in [calculated, mentioned] if m > 0]
        if not valid:
            return "0 years 0 months"

        total_months = min(valid)
        years, months = divmod(total_months, 12)
        return f"{years} years {months} months"

    def _experience_from_dates(self, text: str) -> int:
        month_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4,
            "may": 5, "jun": 6, "jul": 7, "aug": 8,
            "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }

        pattern = re.compile(
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[-–]\s*'
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})',
            re.IGNORECASE
        )

        total = 0
        for m1, y1, m2, y2 in pattern.findall(text):
            start = datetime(int(y1), month_map[m1.lower()], 1)
            end = datetime(int(y2), month_map[m2.lower()], 1)
            diff = (end.year - start.year) * 12 + (end.month - start.month)
            total += max(diff, 0)

        return total

    def _experience_from_mentions(self, text: str) -> int:
        match = re.search(
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            text,
            re.IGNORECASE,
        )
        return int(match.group(1)) * 12 if match else 0

    # =========================
    # EDUCATION
    # =========================

    def _extract_education(self, text: str) -> List[str]:
        keywords = [
            "bachelor", "master", "phd", "mba", "b.tech", "m.tech",
            "b.sc", "m.sc", "university", "college", "degree"
        ]

        education = []
        for line in text.split("\n"):
            if any(k in line.lower() for k in keywords):
                education.append(line.strip())

        return education

    # =========================
    # LLM-BASED INTELLIGENCE
    # =========================

    def _extract_job_role(self, summary_text: str) -> str:
        prompt = ChatPromptTemplate.from_template(
            """
            You are an expert recruiter.

            From the following resume summary, identify the PRIMARY job role.
            Return ONLY the job role as a short title.

            Text:
            {summary}
            """
        )

        response = self.llm.invoke(
            prompt.format_messages(summary=summary_text)
        )

        return response.content.strip()

    def _extract_skills(self, text: str, job_role: str) -> List[str]:
        prompt = ChatPromptTemplate.from_template(
            """
            You are an expert interviewer.

            Candidate job role:
            {job_role}

            Extract ONLY skill keywords (technical and non-technical).
            Do NOT include certifications, achievements, or tools descriptions.
            Remove duplicates.
            Return output as a simple comma-separated list.

            Resume text:
            {text}
            """
        )

        response = self.llm.invoke(
            prompt.format_messages(job_role=job_role, text=text)
        )

        # Normalize into Python list
        skills = [
            s.strip()
            for s in response.content.split(",")
            if s.strip()
        ]
        return list(set(skills))

    # =========================
    # OPTIONAL LINKS
    # =========================

    def _extract_github(self, text: str) -> Optional[str]:
        pattern = r'(https?://)?(www\.)?github\.com/[A-Za-z0-9_-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group()
            return url if url.startswith("http") else f"https://{url}"
        return None

    def _extract_portfolio(self, text: str) -> Optional[str]:
        urls = re.findall(r'(https?://[^\s]+)', text)
        blacklist = ["linkedin.com", "github.com"]

        for url in urls:
            if not any(b in url.lower() for b in blacklist):
                return url

        return None
    # def _extract_from_pdf_ocr(self, file_path: Path) -> str:
    #     """
    #     OCR fallback for image-based or design-heavy PDFs.
    #     """
    #     logger.warning("Falling back to OCR for PDF text extraction")

    #     text = ""
    #     images = convert_from_path(file_path)

    #     for img in images:
    #         text += pytesseract.image_to_string(img)

    #     return text

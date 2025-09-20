# backend/app/config.py
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp")
MAX_CLAUSE_LENGTH = int(os.getenv("MAX_CLAUSE_LENGTH", "1200"))
CLASSES = [
    "Payment Terms",
    "Termination",
    "Liability",
    "Confidentiality",
    "IP / Ownership",
    "Governing Law",
    "Auto-Renewal",
    "Warranty",
    "Assignment",
    "Miscellaneous",
]

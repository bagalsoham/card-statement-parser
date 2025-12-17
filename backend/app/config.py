# app/config.py
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Groq Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    DEFAULT_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

    # Parser Configuration
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    USE_LLM_FALLBACK: bool = os.getenv("USE_LLM_FALLBACK", "true").lower() in ("true", "1", "yes")
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

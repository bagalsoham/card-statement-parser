import json
from typing import Dict, Optional
import structlog
from app.config import Config

logger = structlog.get_logger()


class LLMExtractor:
    """
    LLM-based extraction using Groq (LLaMA 3).
    Free, fast, and stable for POC usage.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GROQ_API_KEY
        self.client = None

        if not self.api_key:
            logger.warning("no_groq_api_key", message="LLM fallback disabled")
            return

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)

            logger.info(
                "groq_initialized",
                model=Config.DEFAULT_MODEL
            )

        except Exception as e:
            logger.error("groq_init_failed", error=str(e))
            self.client = None

    def extract_fields(self, text: str, issuer: Optional[str] = None) -> Dict:
        if not self.client:
            raise ValueError("Groq client not initialized")

        text_sample = text[:6000]

        prompt = f"""
Extract the following information from this credit card statement.
Return ONLY valid JSON. No explanation.

{{
  "issuer": "Bank/Card issuer name",
  "card_last_4": "Last 4 digits of card number",
  "statement_period": "Billing cycle",
  "due_date": "Payment due date",
  "total_amount_due": "Total amount due (numeric only)"
}}

Rules:
- If missing, return null
- Amount must be numeric only
- Preserve original date format
{f"- Issuer is likely {issuer}" if issuer else ""}

Statement Text:
{text_sample}
""".strip()

        try:
            response = self.client.chat.completions.create(
                model=Config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a precise financial document parser."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
            )

            content = response.choices[0].message.content.strip()
            content = content.replace("```json", "").replace("```", "").strip()

            data = json.loads(content)

            logger.info("llm_extraction_success", fields=list(data.keys()))
            return data

        except json.JSONDecodeError as e:
            logger.error("llm_json_parse_error", error=str(e), response=content[:300])
            raise

        except Exception as e:
            logger.error("llm_extraction_failed", error=str(e))
            raise

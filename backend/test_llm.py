# backend/test_llm.py
# Place this file in: backend/test_llm.py (NOT in tests/)

from app.llm_extractor import LLMExtractor
from app.config import Config

print("=" * 60)
print("Testing LLM Extractor (Groq)")
print("=" * 60)

# =========================
# API Key Check
# =========================
if Config.GROQ_API_KEY:
    print(f"✓ GROQ API Key found: {Config.GROQ_API_KEY[:10]}...")
else:
    print("✗ No GROQ API key found.")
    print("\nTo get a key:")
    print("1. Visit: https://console.groq.com/keys")
    print("2. Create an API key")
    print("3. Add to .env: GROQ_API_KEY=your-key-here")
    exit(1)

print(f"✓ Model: {Config.DEFAULT_MODEL}")
print(f"✓ LLM Fallback Enabled: {Config.USE_LLM_FALLBACK}")
print()

# =========================
# Sample Credit Card Statement
# =========================
test_text = """
HDFC Bank Limited
Credit Card Statement

Statement Period: 01-Nov-2024 to 30-Nov-2024

Card Details:
Card Number: XXXX XXXX XXXX 4567
Card Holder Name: JOHN DOE

Payment Information:
Payment Due Date: 15-Dec-2024
Minimum Amount Due: Rs. 1,234.00
Total Amount Due ₹45,678.50

Previous Balance: ₹12,345.67
Payments Received: ₹12,345.67
New Charges: ₹45,678.50
"""

print("Testing with HDFC statement text...")
print("-" * 60)

try:
    # Initialize extractor
    extractor = LLMExtractor()

    # Run extraction
    result = extractor.extract_fields(test_text, issuer="HDFC")

    print("\n✓ Extraction Successful!")
    print("=" * 60)
    print("RESULTS:")
    print("=" * 60)

    for field, value in result.items():
        print(f"{field:20} : {value}")

    print("=" * 60)
    print("\n✅ LLM Extractor is working correctly!")

except ValueError as e:
    print(f"\n✗ Configuration Error: {e}")
    print("\nMake sure:")
    print("1. GROQ_API_KEY is set in .env")
    print("2. groq is installed: pip install groq")

except Exception as e:
    print(f"\n✗ Extraction Failed: {e}")
    print(f"Error type: {type(e).__name__}")

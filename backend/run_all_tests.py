"""Simple visual test runner for the backend parsers.

Place this file at `backend/run_all_tests.py` and run it from the `backend`
directory. It uses the mock statements in `tests/mock_statements.py` and the
parsers under `app.parsers` to run a quick detection + extraction summary.
"""

import sys

try:
    from app.issuer_detector import IssuerDetector
    from app.parsers.hdfc_parser import HDFCParser
    from app.parsers.icici_parser import ICICIParser
    from app.parsers.sbi_parser import SBIParser
    from app.parsers.axis_parser import AxisParser
    from app.parsers.amex_parser import AmexParser
    from tests.mock_statements import MockStatementGenerator
except Exception as e:
    print("Error importing project modules:", e)
    print("Make sure you run this script from the `backend` directory and that the\n" \
          "virtualenv / dependencies are available.")
    sys.exit(1)


def run_visual_tests():
    print("\n" + "=" * 70)
    print("CREDIT CARD PARSER - COMPREHENSIVE TEST SUITE")
    print("=" * 70 + "\n")

    issuers = [
        ("HDFC Bank", HDFCParser(), MockStatementGenerator.generate_hdfc_statement()),
        ("ICICI Bank", ICICIParser(), MockStatementGenerator.generate_icici_statement()),
        ("SBI Card", SBIParser(), MockStatementGenerator.generate_sbi_statement()),
        ("Axis Bank", AxisParser(), MockStatementGenerator.generate_axis_statement()),
        ("American Express", AmexParser(), MockStatementGenerator.generate_amex_statement()),
    ]

    results = []

    for issuer_name, parser, text in issuers:
        print(f"Testing {issuer_name}...")

        try:
            issuer_code, issuer_conf = IssuerDetector.detect(text)
        except Exception as e:
            issuer_code, issuer_conf = None, 0.0
            print(f"  Detection failed: {e}")

        try:
            result = parser.parse(text)
        except Exception as e:
            print(f"  Parser {parser.__class__.__name__} raised: {e}")
            # create a minimal failing StatementData-like object
            class _Fail:
                overall_confidence = 0.0
                issuer = card_last_4 = statement_period = due_date = type('X', (), {'value': None})()
            result = _Fail()

        fields_extracted = sum(
            1 for field in [result.issuer, result.card_last_4,
                            result.statement_period, result.due_date,
                            result.total_amount_due]
            if getattr(field, "value", None) is not None
        )

        results.append({
            "issuer": issuer_name,
            "detected": issuer_code,
            "detection_confidence": issuer_conf,
            "overall_confidence": getattr(result, "overall_confidence", 0.0),
            "fields_extracted": fields_extracted,
        })

        print(f"  ✓ Detection: {issuer_conf:.2f}")
        print(f"  ✓ Extraction: {results[-1]['overall_confidence']:.2f}")
        print(f"  ✓ Fields: {results[-1]['fields_extracted']}/5\n")

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{ 'Issuer':<20} {'Detection':<12} {'Extraction':<12} {'Fields':<8}")
    print("-" * 70)

    for r in results:
        print(f"{r['issuer']:<20} {r['detection_confidence']:<12.2f} "
              f"{r['overall_confidence']:<12.2f} {r['fields_extracted']}/5")

    avg_detection = sum(r['detection_confidence'] for r in results) / len(results)
    avg_extraction = sum(r['overall_confidence'] for r in results) / len(results)

    print("-" * 70)
    print(f"{ 'AVERAGE':<20} {avg_detection:<12.2f} {avg_extraction:<12.2f}")
    print("=" * 70 + "\n")

    # Pass/Fail
    if avg_detection >= 0.8 and avg_extraction >= 0.8:
        print("✅ ALL TESTS PASSED - Ready for production!")
    elif avg_detection >= 0.7 and avg_extraction >= 0.7:
        print("⚠️  TESTS PASSED - Consider improving some patterns")
    else:
        print("❌ TESTS FAILED - Review and improve parsers")


if __name__ == "__main__":
    run_visual_tests()
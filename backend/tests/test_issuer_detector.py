import pytest

from app.issuer_detector import IssuerDetector
from tests.mock_statements import MockStatementGenerator


@pytest.mark.parametrize(
    "generator_func, expected_code",
    [
        (MockStatementGenerator.generate_hdfc_statement, "HDFC"),
        (MockStatementGenerator.generate_icici_statement, "ICICI"),
        (MockStatementGenerator.generate_sbi_statement, "SBI"),
        (MockStatementGenerator.generate_axis_statement, "AXIS"),
        (MockStatementGenerator.generate_amex_statement, "AMEX"),
    ],
)
def test_detect_returns_issuer_and_confidence(generator_func, expected_code):
    text = generator_func()
    issuer, confidence = IssuerDetector.detect(text)

    assert issuer is not None, "Issuer should be detected"
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
    assert issuer == expected_code

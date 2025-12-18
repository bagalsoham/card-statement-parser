# Contributing to Credit Card Statement Parser

First off, thank you for considering contributing! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Adding New Bank Parser](#adding-new-bank-parser)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code.

- **Be respectful** and inclusive
- **Be patient** with beginners
- **Give constructive feedback**
- **Focus on what is best** for the community

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** and description
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, etc.)
- **Sample PDF** (if possible, anonymized)

**Bug Report Template:**
```markdown
## Bug Description
[Clear description of the bug]

## Steps to Reproduce
1. Start backend server
2. Upload HDFC statement PDF
3. Observe error in response

## Expected Behavior
Should extract all fields with >0.9 confidence

## Actual Behavior
Returns null for card_last_4 field

## Environment
- OS: Windows 11
- Python: 3.10.5
- Browser: Chrome 120
- Backend version: 2.0.0

## Logs
```
[Paste relevant logs here]
```

## Sample PDF
[Attach or describe PDF if possible]
```

### 💡 Suggesting Features

Feature requests are welcome! Please include:

- **Use case**: Why is this needed?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches
- **Impact**: Who benefits from this?

### 🏦 Adding New Bank Support

The most valuable contribution! See [Adding a New Bank Parser](#adding-new-bank-parser) below.

### 📖 Improving Documentation

Documentation improvements are always welcome:
- Fix typos
- Clarify confusing sections
- Add examples
- Translate to other languages

---

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 16+
- Git
- Google Gemini API key (for testing LLM features)

### Setup Steps

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/credit-card-parser.git
cd credit-card-parser

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/credit-card-parser.git

# 4. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. Frontend setup
cd ../frontend
npm install

# 6. Configure environment
cp backend/.env.example backend/.env
# Edit .env with your API keys

# 7. Run tests to verify setup
cd backend
pytest tests/ -v
```

### Development Dependencies

Create `backend/requirements-dev.txt`:

```
# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1

# Code Quality
black==23.12.0
flake8==7.0.0
mypy==1.7.1
isort==5.13.2

# Development Tools
pre-commit==3.6.0
ipython==8.18.1
```

---

## Adding New Bank Parser

### Step-by-Step Guide

#### Step 1: Research Bank Format

Collect 3-5 sample statements and identify:
- Card number masking format
- Date formats used
- Amount labels
- Statement period format

#### Step 2: Create Parser File

Create `backend/app/parsers/newbank_parser.py`:

```python
import re
from app.parsers.base_parser import BaseParser

class NewBankParser(BaseParser):
    """New Bank-specific parser"""
    
    def extract_with_regex(self, text: str) -> dict:
        """Extract using New Bank-specific patterns"""
        result = {}
        
        # Issuer
        result["issuer"] = {
            "value": "New Bank",
            "method": "regex"
        }
        
        # Card last 4
        card_patterns = [
            r"Card Number[:\s]*(?:XXXX\s*){3}(\d{4})",
            r"ending\s+(?:in\s+)?(\d{4})"
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["card_last_4"] = {
                    "value": match.group(1),
                    "method": "regex"
                }
                break
        
        # Statement period
        period_patterns = [
            r"Statement Period[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*to\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        ]
        
        for pattern in period_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["statement_period"] = {
                    "value": f"{match.group(1)} to {match.group(2)}",
                    "method": "regex"
                }
                break
        
        # Due date
        due_patterns = [
            r"Payment Due Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})"
        ]
        
        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["due_date"] = {
                    "value": match.group(1).strip(),
                    "method": "regex"
                }
                break
        
        # Total amount due
        amount_patterns = [
            r"Total Amount Due[:\s]*(?:Rs\.?|₹)?\s*([\d,]+\.?\d*)"
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["total_amount_due"] = {
                    "value": match.group(1).replace(",", ""),
                    "method": "regex"
                }
                break
        
        return result
```

#### Step 3: Register Parser

Update `backend/main.py`:

```python
from app.parsers.newbank_parser import NewBankParser

PARSER_REGISTRY = {
    "HDFC": HDFCParser(),
    "ICICI": ICICIParser(),
    "SBI": SBIParser(),
    "AXIS": AxisParser(),
    "AMEX": AmexParser(),
    "NEWBANK": NewBankParser(),  # Add here
}
```

#### Step 4: Add Detection Patterns

Update `backend/app/issuer_detector.py`:

```python
ISSUER_PATTERNS = {
    "HDFC": [r"hdfc\s+bank", r"hdfc\s+credit\s+card"],
    "ICICI": [r"icici\s+bank", r"icici\s+credit"],
    "SBI": [r"sbi\s+card", r"state\s+bank.*card"],
    "AXIS": [r"axis\s+bank", r"axis\s+credit"],
    "AMEX": [r"american\s+express", r"amex"],
    "NEWBANK": [r"new\s+bank", r"newbank\s+credit"],  # Add here
}
```

#### Step 5: Create Test File

Create `backend/tests/test_newbank_parser.py`:

```python
import pytest
from app.parsers.newbank_parser import NewBankParser

class TestNewBankParser:
    """Test New Bank parser"""
    
    def test_newbank_basic_extraction(self):
        """Test basic field extraction"""
        text = """
        New Bank Credit Card Statement
        Card Number: XXXX XXXX XXXX 1234
        Statement Period: 01/11/2024 to 30/11/2024
        Payment Due Date: 15/12/2024
        Total Amount Due: Rs. 10,000.00
        """
        
        parser = NewBankParser()
        result = parser.parse(text)
        
        assert result.issuer.value == "New Bank"
        assert result.card_last_4.value == "1234"
        assert result.overall_confidence >= 0.7
    
    def test_newbank_issuer_detection(self):
        """Test issuer detection"""
        from app.issuer_detector import IssuerDetector
        
        text = "New Bank Credit Card Statement"
        issuer, confidence = IssuerDetector.detect(text)
        
        assert issuer == "NEWBANK"
        assert confidence > 0.5
```

#### Step 6: Update Documentation

Update `README.md` supported issuers table:

```markdown
| Bank | Status | Accuracy | Special Notes |
|------|--------|----------|---------------|
| **New Bank** | ✅ Fully Supported | 95% | [Add notes] |
```

Update `docs/BANK_PATTERNS.md` with New Bank patterns.

#### Step 7: Test Your Parser

```bash
# Run specific test
pytest tests/test_newbank_parser.py -v

# Run all tests
pytest tests/ -v

# Test with real PDF (if available)
python test_example.py path/to/newbank_statement.pdf
```

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Quotes**: Double quotes for strings
- **Imports**: Sorted with `isort`
- **Type hints**: Required for function signatures

### Formatting

```bash
# Format code with Black
black backend/

# Sort imports
isort backend/

# Check style
flake8 backend/

# Type check
mypy backend/app
```

### Example Code Style

```python
from typing import Dict, Optional

import structlog

from app.parsers.base_parser import BaseParser

logger = structlog.get_logger()


class ExampleParser(BaseParser):
    """
    Example parser showing style conventions.
    
    Attributes:
        name: Parser name
        version: Parser version
    """
    
    def __init__(self, name: str = "example") -> None:
        """Initialize parser.
        
        Args:
            name: Parser identifier
        """
        super().__init__()
        self.name = name
        logger.info("parser_initialized", name=name)
    
    def extract_field(self, text: str, pattern: str) -> Optional[str]:
        """Extract single field using pattern.
        
        Args:
            text: Input text to search
            pattern: Regex pattern
            
        Returns:
            Extracted value or None if not found
        """
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `HDFCParser`)
- **Functions/Methods**: `snake_case` (e.g., `extract_fields`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_MODEL`)
- **Private methods**: `_leading_underscore` (e.g., `_calculate_confidence`)
- **Files**: `snake_case` (e.g., `pdf_loader.py`)

---

## Testing Guidelines

### Test Structure

```python
# tests/test_feature.py
import pytest
from app.module import Feature

class TestFeature:
    """Test suite for Feature"""
    
    def test_basic_functionality(self):
        """Test basic use case"""
        # Arrange
        feature = Feature()
        input_data = "test"
        
        # Act
        result = feature.process(input_data)
        
        # Assert
        assert result == "expected"
    
    def test_edge_case(self):
        """Test edge case handling"""
        feature = Feature()
        
        with pytest.raises(ValueError):
            feature.process(None)
    
    @pytest.mark.parametrize("input,expected", [
        ("case1", "result1"),
        ("case2", "result2"),
    ])
    def test_multiple_cases(self, input, expected):
        """Test multiple scenarios"""
        feature = Feature()
        assert feature.process(input) == expected
```

### Test Coverage

Aim for >80% coverage:

```bash
# Run with coverage
pytest --cov=app --cov-report=html tests/

# View report
open htmlcov/index.html
```

### Mock External Services

```python
from unittest.mock import Mock, patch

def test_llm_extraction():
    """Test with mocked LLM"""
    with patch('app.llm_extractor.genai') as mock_genai:
        mock_genai.GenerativeModel.return_value.generate_content.return_value.text = '{"issuer": "Test"}'
        
        extractor = LLMExtractor()
        result = extractor.extract_fields("test text")
        
        assert result["issuer"] == "Test"
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main

### PR Checklist

```markdown
## Description
[Clear description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(parser): add support for New Bank

- Created NewBankParser class
- Added detection patterns
- Updated tests and documentation

Closes #123
```

```
fix(llm): handle empty API responses

- Add null check before accessing response.text
- Return empty dict on failure
- Add logging for debugging
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Code review** by maintainers
3. **Revisions** if requested
4. **Approval** and merge

### After Merge

- Your contribution will be credited in CHANGELOG.md
- Thank you message in merged PR
- Tagged in release notes (if applicable)

---

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/your-username/credit-card-parser/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/your-username/credit-card-parser/issues)
- **Security issues**: Email security@example.com

---

Thank you for contributing! 🚀
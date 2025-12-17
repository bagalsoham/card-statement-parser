class MockStatementGenerator:
    """Generate realistic statement text for testing"""
    
    @staticmethod
    def generate_hdfc_statement(
        card_last_4: str = "4567",
        amount: str = "45678.50",
        due_date: str = "15-Dec-2024"
    ) -> str:
        """Generate HDFC Bank statement text"""
        return f"""
        HDFC BANK LIMITED
        Credit Card Statement
        
        Statement Period: 01-Nov-2024 to 30-Nov-2024
        
        Card Details:
        Card Number: XXXX XXXX XXXX {card_last_4}
        Card Holder Name: JOHN DOE
        
        Payment Information:
        Payment Due Date: {due_date}
        Minimum Amount Due: Rs. 1,234.00
        Total Amount Due ₹{amount}
        
        Previous Balance: ₹12,345.67
        Payments Received: ₹12,345.67
        New Charges: ₹{amount}
        
        Transaction Details:
        Date        Description                Amount
        01-Nov-24   Amazon Purchase           ₹2,345.00
        05-Nov-24   Swiggy Food Order         ₹456.00
        10-Nov-24   Uber Ride                 ₹234.00
        
        Please pay by {due_date} to avoid late fees.
        
        For queries: 1800-XXX-XXXX
        HDFC Bank - Your Banking Partner
        """
    
    @staticmethod
    def generate_icici_statement(
        card_last_4: str = "7890",
        amount: str = "23456.78",
        due_date: str = "20/12/2024"
    ) -> str:
        """Generate ICICI Bank statement text"""
        return f"""
        ICICI BANK
        CREDIT CARD STATEMENT
        
        Statement from: 01/11/2024 To: 30/11/2024
        
        Card Information
        Card No: ****{card_last_4}
        Name: JANE SMITH
        
        Payment Details
        Payment Due By: {due_date}
        Minimum Payment Due: Rs. 2,345.00
        Total Due INR {amount}
        
        Account Summary:
        Opening Balance         Rs. 15,000.00
        Credits                 Rs. 15,000.00
        Debits                  Rs. {amount}
        Closing Balance         Rs. {amount}
        
        Transactions:
        01/11/2024  Flipkart         Rs. 5,678.00
        08/11/2024  BigBasket        Rs. 1,234.00
        15/11/2024  Zomato           Rs. 567.00
        
        Last Date for Payment: {due_date}
        Customer Care: 1860-XXX-XXXX
        ICICI Bank Limited
        """
    
    @staticmethod
    def generate_sbi_statement(
        card_last_4: str = "1234",
        amount: str = "34567.89",
        due_date: str = "18/12/2024"
    ) -> str:
        """Generate SBI Card statement text"""
        return f"""
        SBI CARD
        Credit Card Statement
        
        Statement Period: 01/11/2024 to 30/11/2024
        
        Card Details
        Card No: xxxx xxxx xxxx {card_last_4}
        Primary Card Member: AMIT KUMAR
        
        Payment Information
        Payment Due Date: {due_date}
        Minimum Amount Due: Rs. 3,456.00
        Total Amount Due Rs. {amount}
        
        Balance Summary:
        Previous Balance            Rs. 10,000.00
        Payments/Credits            Rs. 10,000.00
        Purchases & Charges         Rs. {amount}
        Current Balance             Rs. {amount}
        
        Transaction History:
        Date       Merchant              Amount
        02/11/24   Myntra Fashion        Rs. 4,567.00
        09/11/24   BookMyShow            Rs. 890.00
        16/11/24   Reliance Digital      Rs. 12,345.00
        
        Pay by {due_date} to maintain good credit score.
        
        Helpline: 1860-XXX-XXXX
        SBI Card - India's Most Trusted Card
        """
    
    @staticmethod
    def generate_axis_statement(
        card_last_4: str = "5678",
        amount: str = "56789.01",
        due_date: str = "22 Dec 2024"
    ) -> str:
        """Generate Axis Bank statement text"""
        return f"""
        AXIS BANK
        Credit Card Statement
        
        Statement Date: 01 Nov 2024 to 30 Nov 2024
        
        Card Information:
        Card Number: XXXX{card_last_4}
        Cardholder: PRIYA SHARMA
        
        Payment Details:
        Payment Due Date: {due_date}
        Minimum Payment: ₹5,678.00
        Total Amount Due ₹{amount}
        
        Account Activity:
        Opening Balance             ₹8,900.00
        Payments Received           ₹8,900.00
        New Transactions            ₹{amount}
        Closing Balance             ₹{amount}
        
        Recent Transactions:
        Date          Description            Amount
        03 Nov 24     MakeMyTrip Flight      ₹15,678.00
        11 Nov 24     Croma Electronics      ₹8,900.00
        20 Nov 24     Decathlon Sports       ₹4,567.00
        
        Last Date to Pay: {due_date}
        Contact: 1860-XXX-XXXX
        Axis Bank - Badhti Ka Naam Zindagi
        """
    
    @staticmethod
    def generate_amex_statement(
        card_last_5: str = "34567",
        amount: str = "1234.56",
        due_date: str = "Dec 25, 2024"
    ) -> str:
        """Generate American Express statement text"""
        return f"""
        AMERICAN EXPRESS
        Credit Card Statement
        
        Billing Period: Nov 01, 2024 - Nov 30, 2024
        
        Card Member Information:
        Card Member No: *****{card_last_5}
        Name: ROBERT JOHNSON
        
        Payment Information:
        Please Pay By: {due_date}
        Minimum Payment Due: ${amount}
        New Balance ${amount}
        
        Account Summary:
        Previous Balance            $800.00
        Payments & Credits          $800.00
        Charges                     ${amount}
        New Balance                 ${amount}
        
        Charges This Period:
        Nov 03    Apple Store Online      $456.78
        Nov 12    Starbucks              $23.45
        Nov 18    Amazon Prime           $14.99
        
        Payment Amount Due: ${amount}
        Due Date: {due_date}
        
        Member Services: 1-800-XXX-XXXX
        American Express - Don't Leave Home Without It
        """


# ----------------------------------------------------------------------------
# File: tests/test_all_parsers.py
# ----------------------------------------------------------------------------

from app.pdf_loader import PDFLoader
from app.issuer_detector import IssuerDetector
from app.parsers.hdfc_parser import HDFCParser
from app.parsers.icici_parser import ICICIParser
from app.parsers.sbi_parser import SBIParser
from app.parsers.axis_parser import AxisParser
from app.parsers.amex_parser import AmexParser

class TestHDFCParser:
    """Test HDFC Bank parser"""
    
    def test_hdfc_basic_extraction(self):
        """Test basic field extraction"""
        text = MockStatementGenerator.generate_hdfc_statement(
            card_last_4="4567",
            amount="45678.50",
            due_date="15-Dec-2024"
        )
        
        parser = HDFCParser()
        result = parser.parse(text)
        
        # Assertions
        assert result.issuer.value == "HDFC Bank"
        assert result.card_last_4.value == "4567"
        assert "45678.50" in result.total_amount_due.value
        assert result.overall_confidence >= 0.7
    
    def test_hdfc_issuer_detection(self):
        """Test issuer detection"""
        text = MockStatementGenerator.generate_hdfc_statement()
        issuer, confidence = IssuerDetector.detect(text)
        
        assert issuer == "HDFC"
        assert confidence > 0.5
    
    def test_hdfc_edge_cases(self):
        """Test edge cases"""
        # Large amount
        text = MockStatementGenerator.generate_hdfc_statement(
            amount="1,23,456.78"
        )
        parser = HDFCParser()
        result = parser.parse(text)
        
        # Should handle commas
        assert "," not in result.total_amount_due.value or \
               result.total_amount_due.value.replace(",", "").isdigit()


class TestICICIParser:
    """Test ICICI Bank parser"""
    
    def test_icici_basic_extraction(self):
        """Test basic field extraction"""
        text = MockStatementGenerator.generate_icici_statement(
            card_last_4="7890",
            amount="23456.78",
            due_date="20/12/2024"
        )
        
        parser = ICICIParser()
        result = parser.parse(text)
        
        assert result.issuer.value == "ICICI Bank"
        assert result.card_last_4.value == "7890"
        assert result.overall_confidence >= 0.7
    
    def test_icici_date_formats(self):
        """Test multiple date formats"""
        text = MockStatementGenerator.generate_icici_statement(
            due_date="20/12/2024"
        )
        
        parser = ICICIParser()
        result = parser.parse(text)
        
        assert result.due_date.value is not None
        assert result.due_date.confidence >= 0.7


class TestSBIParser:
    """Test SBI Card parser"""
    
    def test_sbi_basic_extraction(self):
        """Test basic field extraction"""
        text = MockStatementGenerator.generate_sbi_statement(
            card_last_4="1234",
            amount="34567.89",
            due_date="18/12/2024"
        )
        
        parser = SBIParser()
        result = parser.parse(text)
        
        assert result.issuer.value == "SBI Card"
        assert result.card_last_4.value == "1234"
        assert result.overall_confidence >= 0.7
    
    def test_sbi_amount_format(self):
        """Test amount parsing with Rs. prefix"""
        text = MockStatementGenerator.generate_sbi_statement(
            amount="50,000.00"
        )
        
        parser = SBIParser()
        result = parser.parse(text)
        
        assert result.total_amount_due.value is not None


class TestAxisParser:
    """Test Axis Bank parser"""
    
    def test_axis_basic_extraction(self):
        """Test basic field extraction"""
        text = MockStatementGenerator.generate_axis_statement(
            card_last_4="5678",
            amount="56789.01",
            due_date="22 Dec 2024"
        )
        
        parser = AxisParser()
        result = parser.parse(text)
        
        assert result.issuer.value == "Axis Bank"
        assert result.card_last_4.value == "5678"
        assert result.overall_confidence >= 0.7
    
    def test_axis_date_with_spaces(self):
        """Test date format with spaces"""
        text = MockStatementGenerator.generate_axis_statement(
            due_date="25 Dec 2024"
        )
        
        parser = AxisParser()
        result = parser.parse(text)
        
        assert result.due_date.value is not None


class TestAmexParser:
    """Test American Express parser"""
    
    def test_amex_basic_extraction(self):
        """Test basic field extraction"""
        text = MockStatementGenerator.generate_amex_statement(
            card_last_5="34567",
            amount="1234.56",
            due_date="Dec 25, 2024"
        )
        
        parser = AmexParser()
        result = parser.parse(text)
        
        assert result.issuer.value == "American Express"
        # Amex may have 5 digits, but we take last 4
        assert len(result.card_last_4.value) == 4
        assert result.overall_confidence >= 0.7
    
    def test_amex_new_balance_label(self):
        """Test 'New Balance' amount label"""
        text = MockStatementGenerator.generate_amex_statement(
            amount="999.99"
        )
        
        parser = AmexParser()
        result = parser.parse(text)
        
        assert result.total_amount_due.value is not None
        assert result.total_amount_due.extraction_method in ["regex", "llm"]


# ----------------------------------------------------------------------------
# File: tests/test_integration.py
# ----------------------------------------------------------------------------

class TestEndToEnd:
    """Integration tests for full pipeline"""
    
    def test_all_issuers_detection(self):
        """Test that all issuers are correctly detected"""
        test_cases = [
            (MockStatementGenerator.generate_hdfc_statement(), "HDFC"),
            (MockStatementGenerator.generate_icici_statement(), "ICICI"),
            (MockStatementGenerator.generate_sbi_statement(), "SBI"),
            (MockStatementGenerator.generate_axis_statement(), "AXIS"),
            (MockStatementGenerator.generate_amex_statement(), "AMEX"),
        ]
        
        for text, expected_issuer in test_cases:
            issuer, confidence = IssuerDetector.detect(text)
            assert issuer == expected_issuer, \
                f"Expected {expected_issuer}, got {issuer}"
            assert confidence > 0.5
    
    def test_all_parsers_confidence(self):
        """Test that all parsers return reasonable confidence"""
        parsers = {
            "HDFC": (HDFCParser(), MockStatementGenerator.generate_hdfc_statement()),
            "ICICI": (ICICIParser(), MockStatementGenerator.generate_icici_statement()),
            "SBI": (SBIParser(), MockStatementGenerator.generate_sbi_statement()),
            "AXIS": (AxisParser(), MockStatementGenerator.generate_axis_statement()),
            "AMEX": (AmexParser(), MockStatementGenerator.generate_amex_statement()),
        }
        
        for issuer, (parser, text) in parsers.items():
            result = parser.parse(text)
            
            print(f"\n{issuer} Results:")
            print(f"  Overall Confidence: {result.overall_confidence:.2f}")
            print(f"  Issuer: {result.issuer.value} ({result.issuer.confidence:.2f})")
            print(f"  Card: {result.card_last_4.value} ({result.card_last_4.confidence:.2f})")
            print(f"  Amount: {result.total_amount_due.value} ({result.total_amount_due.confidence:.2f})")
            
            # All parsers should have >0.7 confidence on synthetic data
            assert result.overall_confidence >= 0.7, \
                f"{issuer} parser confidence too low: {result.overall_confidence}"

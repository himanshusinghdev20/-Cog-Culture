"""
Utilities for Fact-Check Agent
Helper functions and logging
"""

import logging
from datetime import datetime
import json
from pathlib import Path


# Setup logging
def setup_logging(log_file: str = "factchecker.log"):
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def save_results(results: dict, output_file: str = None) -> str:
    """Save verification results to file"""
    if output_file is None:
        output_file = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to {output_file}")
    return output_file


def load_results(input_file: str) -> dict:
    """Load verification results from file"""
    with open(input_file, 'r') as f:
        results = json.load(f)
    
    logger.info(f"Results loaded from {input_file}")
    return results


def format_report(results: list) -> str:
    """Format results as readable report"""
    report = []
    report.append("=" * 70)
    report.append("FACT-CHECK VERIFICATION REPORT")
    report.append("=" * 70)
    report.append("")
    
    # Summary
    verified = sum(1 for r in results if r['status'] == 'VERIFIED')
    unverified = sum(1 for r in results if r['status'] == 'UNVERIFIED')
    no_evidence = sum(1 for r in results if r['status'] == 'NO_EVIDENCE')
    
    report.append(f"Summary: {verified} verified, {unverified} unverified, {no_evidence} no evidence")
    report.append("")
    
    # Detailed results
    for i, result in enumerate(results, 1):
        report.append(f"{i}. {result['claim'][:80]}")
        report.append(f"   Status: {result['status']}")
        report.append(f"   Confidence: {result.get('confidence', 0):.1%}")
        
        if result.get('evidence'):
            report.append(f"   Evidence: {result['evidence_count']} sources")
        
        report.append("")
    
    report.append("=" * 70)
    
    return "\n".join(report)


def validate_pdf_file(file_path: str) -> bool:
    """Check if file is valid PDF"""
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    if path.suffix.lower() != '.pdf':
        logger.error(f"Not a PDF file: {file_path}")
        return False
    
    if path.stat().st_size > 200 * 1024 * 1024:  # 200MB limit
        logger.error(f"File too large: {file_path}")
        return False
    
    return True


def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters but keep alphanumeric, punctuation, and spaces
    text = ''.join(c for c in text if ord(c) > 31 or c == '\n')
    return text


def extract_numbers(text: str) -> list:
    """Extract all numbers from text"""
    import re
    pattern = r'\d+(?:\.\d+)?'
    return re.findall(pattern, text)


def extract_dates(text: str) -> list:
    """Extract dates from text"""
    import re
    patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
        r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
        r'(?:19|20)\d{2}',  # YYYY
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(?:19|20)\d{2}',
    ]
    
    dates = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return dates


def rate_limit_sleep(api_type: str = 'web'):
    """Sleep to respect rate limits"""
    import time
    
    if api_type == 'web':
        time.sleep(1)  # 1 second between web requests
    elif api_type == 'api':
        time.sleep(2)  # 2 seconds between API calls


class ResultsAnalyzer:
    """Analyze and summarize verification results"""
    
    @staticmethod
    def get_summary(results: list) -> dict:
        """Get summary statistics"""
        total = len(results)
        verified = sum(1 for r in results if r['status'] == 'VERIFIED')
        unverified = sum(1 for r in results if r['status'] == 'UNVERIFIED')
        no_evidence = sum(1 for r in results if r['status'] == 'NO_EVIDENCE')
        
        avg_confidence = sum(r.get('confidence', 0) for r in results) / total if total > 0 else 0
        
        return {
            'total_claims': total,
            'verified': verified,
            'unverified': unverified,
            'no_evidence': no_evidence,
            'avg_confidence': avg_confidence,
            'verification_rate': verified / total if total > 0 else 0
        }
    
    @staticmethod
    def get_high_confidence_claims(results: list, threshold: float = 0.75) -> list:
        """Get claims with high confidence"""
        return [r for r in results if r.get('confidence', 0) >= threshold]
    
    @staticmethod
    def get_suspicious_claims(results: list) -> list:
        """Get claims marked as false or no evidence"""
        return [r for r in results if r['status'] in ['NO_EVIDENCE', 'UNVERIFIED']]

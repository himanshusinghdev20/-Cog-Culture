"""
PDF Extraction Module
Enhanced text extraction with cleaning, validation, and metadata handling
"""

import pdfplumber
from typing import List, Dict, Tuple, Optional
import re
import unicodedata


class PDFExtractor:
    """Extract and clean text from PDF files with quality control"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.pages = []
        self.extraction_quality = {}
        
    def extract_text(self) -> str:
        """Extract all text from PDF with cleaning and validation"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                full_text = ""
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        raw_text = page.extract_text() or ""
                        
                        # Clean extracted text
                        cleaned_text = self._clean_text(raw_text)
                        
                        # Validate extraction quality
                        quality = self._assess_quality(raw_text, cleaned_text)
                        self.extraction_quality[page_num + 1] = quality
                        
                        if cleaned_text:
                            full_text += f"\n--- Page {page_num + 1} ---\n{cleaned_text}"
                            self.pages.append({
                                'page_num': page_num + 1,
                                'text': cleaned_text,
                                'raw_length': len(raw_text),
                                'clean_length': len(cleaned_text),
                                'quality': quality,
                                'has_tables': bool(page.extract_tables())
                            })
                    except Exception as e:
                        print(f"Warning: Failed to extract page {page_num + 1}: {str(e)}")
                        continue
                
                self.text = full_text
                return full_text
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # 1. Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        
        # 2. Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # 3. Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n', text)
        
        # 4. Fix hyphens and dashes
        text = text.replace('–', '-').replace('—', '-')
        
        # 5. Fix quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # 6. Remove control characters
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        
        # 7. Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*([^\s.,!?;:])', r'\1 \2', text)
        
        return text.strip()
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Common OCR error corrections"""
        corrections = {
            r'\b0l\b': 'ol',  # 0 to O
            r'\b1l\b': 'il',  # 1 to I
            r'\brn\b': 'in',  # rn to in
            r'\bm\b': 'in',   # m to in
            r'\brn\b': 'm',   # rn to m
            r'\bcl\b': 'd',   # cl to d
            r'\bi1\b': 'il',  # i1 to il
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _assess_quality(self, raw_text: str, cleaned_text: str) -> Dict:
        """Assess extraction quality"""
        if not raw_text:
            return {'score': 0.0, 'status': 'empty', 'issues': ['No text extracted']}
        
        issues = []
        score = 100.0
        
        # Check for unusual character ratios
        special_chars = sum(1 for c in raw_text if not c.isalnum() and not c.isspace())
        special_ratio = special_chars / len(raw_text) if raw_text else 0
        
        if special_ratio > 0.5:
            issues.append('High special character ratio (possible OCR issue)')
            score -= 20
        
        # Check for broken words
        words = cleaned_text.split()
        broken_words = sum(1 for w in words if len(w) < 3 and not w.isdigit())
        if len(words) > 0 and broken_words / len(words) > 0.3:
            issues.append('Many single/double character words')
            score -= 15
        
        # Check if content looks like proper text
        sentences = [s.strip() for s in cleaned_text.split('.') if s.strip()]
        avg_sentence_length = len(' '.join(sentences).split()) / len(sentences) if sentences else 0
        
        if avg_sentence_length < 3:
            issues.append('Very short sentences (possible formatting issue)')
            score -= 20
        elif avg_sentence_length > 50:
            issues.append('Very long sentences (possible missing punctuation)')
            score -= 10
        
        # Ensure minimum content
        if len(cleaned_text) < 100:
            issues.append('Very little text extracted')
            score -= 30
        
        score = max(0, min(100, score))
        
        status = 'excellent' if score >= 90 else 'good' if score >= 70 else 'fair' if score >= 50 else 'poor'
        
        return {
            'score': score / 100.0,
            'status': status,
            'issues': issues,
            'raw_text_length': len(raw_text),
            'clean_text_length': len(cleaned_text),
            'word_count': len(cleaned_text.split()),
            'sentence_count': len([s for s in cleaned_text.split('.') if s.strip()])
        }
    
    def extract_tables(self) -> List[Dict]:
        """Extract tables from PDF with validation"""
        tables = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_tables = page.extract_tables()
                        if page_tables:
                            for table_idx, table in enumerate(page_tables):
                                tables.append({
                                    'page': page_num + 1,
                                    'table_number': table_idx + 1,
                                    'table': table,
                                    'rows': len(table) if table else 0,
                                    'columns': len(table[0]) if table and table[0] else 0
                                })
                    except Exception as e:
                        print(f"Warning: Could not extract tables from page {page_num + 1}: {str(e)}")
                        continue
        except Exception as e:
            print(f"Error extracting tables: {str(e)}")
        return tables
    
    def get_page_text(self, page_num: int) -> str:
        """Get cleaned text from specific page"""
        if page_num > 0 and page_num <= len(self.pages):
            return self.pages[page_num - 1]['text']
        return ""
    
    def get_page_quality(self, page_num: int) -> Optional[Dict]:
        """Get extraction quality metrics for a page"""
        return self.extraction_quality.get(page_num)
    
    def get_metadata(self) -> Dict:
        """Extract PDF metadata"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                metadata = {
                    'num_pages': len(pdf.pages),
                    'metadata': pdf.metadata,
                    'extracted_pages': len(self.pages),
                    'total_text_length': len(self.text),
                    'average_quality': sum(p['quality']['score'] for p in self.pages) / len(self.pages) if self.pages else 0,
                    'pages_quality': self.extraction_quality
                }
                return metadata
        except Exception as e:
            return {'error': str(e)}
    
    def extract_sentences(self, min_length: int = 15, max_length: int = 500) -> List[str]:
        """Extract sentences from cleaned text"""
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', self.text)
        filtered = [s.strip() for s in sentences if min_length <= len(s.strip()) <= max_length]
        return filtered
    
    def extract_paragraphs(self) -> List[str]:
        """Extract paragraphs from text"""
        paragraphs = [p.strip() for p in self.text.split('\n') if p.strip()]
        return paragraphs


def extract_sentences(text: str, min_length: int = 15, max_length: int = 500) -> List[str]:
    """Split text into sentences for claim extraction"""
    if not text:
        return []
    
    # Split by sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Filter by length
    filtered = [s for s in sentences if min_length <= len(s) <= max_length]
    
    return filtered


def extract_key_phrases(text: str) -> List[str]:
    """Extract potential fact-checkable phrases"""
    if not text:
        return []
    
    # Look for patterns with numbers, percentages, years, etc.
    patterns = [
        r'[A-Za-z\s]+\s+(?:\d+(?:%|%\s+|mill|billion|thousand|bn|mn)?)',  # Numbers with units
        r'(?:19|20)\d{2}(?:\s+[-–]\s+(?:19|20)\d{2})?',  # Years/date ranges
        r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:is|was|founded|created|established)',  # Entities with verbs
    ]
    
    phrases = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phrases.extend(matches)
    
    return list(set(phrases))

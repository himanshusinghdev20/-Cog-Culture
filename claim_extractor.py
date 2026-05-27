"""
Claim Extraction Module
Identifies and extracts factual claims from text using LLM (Groq/OpenAI)
"""

import re
from typing import List, Dict
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Try to import Groq first, fallback to OpenAI
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ClaimExtractor:
    """Extract factual claims from text using Groq or OpenAI"""
    
    def __init__(self, use_groq: bool = True, use_openai: bool = False):
        self.use_groq = use_groq and GROQ_AVAILABLE and os.getenv('GROQ_API_KEY')
        self.use_openai = use_openai and OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY')
        
        if self.use_groq:
            self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            print("✅ Using Groq API for claim extraction")
        elif self.use_openai:
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            print("✅ Using OpenAI API for claim extraction")
        else:
            print("⚠️  Using regex-based extraction (less accurate)")
    
    def extract_claims(self, text: str, max_claims: int = 20) -> List[Dict]:
        """Extract claims from text"""
        if self.use_groq:
            return self.extract_claims_groq(text, max_claims)
        elif self.use_openai:
            return self.extract_claims_openai(text, max_claims)
        else:
            return self.extract_claims_regex(text)
    
    def extract_claims_groq(self, text: str, max_claims: int = 20) -> List[Dict]:
        """Extract claims using Groq API (fastest & most accurate)"""
        try:
            # Split into chunks
            max_chunk = 6000
            chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
            
            all_claims = []
            
            for chunk in chunks:
                prompt = f"""Analyze this text and extract ONLY verifiable factual claims.
Focus on:
- Statistics with numbers (e.g., "50% of people", "2.5 million")
- Specific dates and years (e.g., "founded in 1995")
- Named entities with attributes (e.g., "Apple CEO is Tim Cook")
- Technical specifications and measurements
- Financial figures

For each claim provide JSON with:
1. "claim": The claim text (max 100 chars)
2. "category": [statistic, date, named_entity, technical, financial]
3. "entities": Key search terms (2-3 main terms)

Text:
{chunk}

Return ONLY valid JSON array. No markdown. Example:
[
  {{"claim": "Python created in 1991", "category": "date", "entities": ["Python", "1991"]}}
]

Extract max {max_claims} clear, verifiable facts only."""

                message = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="mixtral-8x7b-32768",
                    temperature=0.1,
                    max_tokens=1500,
                    top_p=0.9,
                )
                
                response_text = message.choices[0].message.content
                
                # Extract JSON
                json_match = re.search(r'\[[\s\S]*\]', response_text)
                if json_match:
                    try:
                        claims = json.loads(json_match.group())
                        all_claims.extend(claims)
                    except json.JSONDecodeError:
                        pass
            
            # Deduplicate
            seen = set()
            unique = []
            for claim in all_claims:
                claim_text = claim.get('claim', '').lower()
                if claim_text not in seen:
                    seen.add(claim_text)
                    unique.append(claim)
            
            return unique[:max_claims]
        
        except Exception as e:
            print(f"Error with Groq extraction: {str(e)}")
            return self.extract_claims_regex(text)
    
    def extract_claims_openai(self, text: str, max_claims: int = 20) -> List[Dict]:
        """Extract claims using OpenAI API"""
        try:
            # Split text into chunks if too long
            max_chunk_size = 8000
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            
            all_claims = []
            
            for chunk in chunks:
                prompt = f"""Analyze the following text and extract all factual claims that can be verified.
Focus on:
- Statistics (percentage, numbers, quantities)
- Dates and historical events
- Financial figures
- Technical specifications
- Named entities and their attributes
- Any quantifiable statements

For each claim, provide:
1. The exact claim text
2. Category (statistic/date/financial/technical/other)
3. Key entities or subjects mentioned

Text to analyze:
{chunk}

Return as JSON array with objects containing: claim, category, entities"""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=2000
                )
                
                try:
                    content = response.choices[0].message.content
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        claims = json.loads(json_match.group())
                        all_claims.extend(claims)
                except (json.JSONDecodeError, AttributeError):
                    pass
            
            return all_claims if all_claims else self.extract_claims_regex(text)
        
        except Exception as e:
            print(f"Error with OpenAI extraction: {str(e)}")
            return self.extract_claims_regex(text)
    
    def extract_claims_regex(self, text: str) -> List[Dict]:
        """Regex-based claim extraction as fallback"""
        claims = []
        
        patterns = {
            'statistic': r'(\d+\.?\d*)\s*%|(\d+)\s*(?:million|billion|thousand)',
            'date': r'\b(?:19|20)\d{2}\b|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}',
            'financial': r'\$[\d,]+(?:\.\d{2})?|USD|€',
            'technical': r'(?:v\d+\.\d+|version\s+\d+|release|algorithm)',
        }
        
        for pattern_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                claims.append({
                    'claim': context,
                    'category': pattern_type,
                    'entities': [match.group()],
                    'confidence': 0.7
                })
        
        return claims
    
    def filter_duplicate_claims(self, claims: List[Dict]) -> List[Dict]:
        """Remove duplicate or very similar claims"""
        seen = set()
        unique = []
        
        for claim in claims:
            claim_text = claim.get('claim', '').lower()
            if claim_text not in seen:
                seen.add(claim_text)
                unique.append(claim)
        
        return unique

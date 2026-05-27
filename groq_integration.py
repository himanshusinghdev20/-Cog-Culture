"""
Groq API Integration Module
Fast and accurate LLM-based claim extraction and verification
"""

import os
from typing import List, Dict, Optional
import json
import re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqClaimExtractor:
    """Extract claims using Groq API for fast and accurate results"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        if GROQ_AVAILABLE:
            self.client = Groq(api_key=self.api_key)
    
    def extract_claims(self, text: str, max_claims: int = 20) -> List[Dict]:
        """Extract factual claims using Groq LLM"""
        
        if not self.client:
            raise RuntimeError("Groq client not initialized")
        
        # Split text into chunks if too long
        max_chunk = 6000
        chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
        
        all_claims = []
        
        for chunk_idx, chunk in enumerate(chunks):
            prompt = f"""Analyze this text and extract ONLY verifiable factual claims. 
Focus on:
- Statistics with numbers (e.g., "50% of people", "2.5 million dollars")
- Specific dates and years (e.g., "founded in 1995", "released on March 15, 2020")
- Named entities with attributes (e.g., "Apple CEO is Tim Cook")
- Technical specifications and measurements
- Financial figures and percentages

For each claim, provide JSON with:
1. "claim": The exact claim text (keep it short, max 100 chars)
2. "category": One of [statistic, date, named_entity, technical, financial]
3. "entities": Key terms to search for (list of 2-3 main terms)
4. "context": Brief context where this claim appears

Text to analyze:
{chunk}

Return ONLY a valid JSON array. Example format:
[
  {{"claim": "Python created in 1991", "category": "date", "entities": ["Python", "1991"], "context": "programming language"}}
]

Extract maximum {max_claims} claims. Be selective - only clear, verifiable facts."""

            try:
                message = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model="mixtral-8x7b-32768",  # Fast Groq model
                    temperature=0.1,  # Low temperature for factual extraction
                    max_tokens=1500,
                    top_p=0.9,
                )
                
                response_text = message.choices[0].message.content
                
                # Extract JSON from response
                json_match = re.search(r'\[[\s\S]*\]', response_text)
                if json_match:
                    try:
                        claims = json.loads(json_match.group())
                        all_claims.extend(claims)
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON from Groq response chunk {chunk_idx}")
                
            except Exception as e:
                print(f"Error extracting claims from chunk {chunk_idx}: {str(e)}")
        
        # Deduplicate claims
        seen = set()
        unique_claims = []
        for claim in all_claims:
            claim_text = claim.get('claim', '').lower()
            if claim_text not in seen:
                seen.add(claim_text)
                unique_claims.append(claim)
        
        return unique_claims[:max_claims]


class GroqFactAnalyzer:
    """Analyze and verify facts using Groq's language model"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        if GROQ_AVAILABLE:
            self.client = Groq(api_key=self.api_key)
    
    def analyze_claim(self, claim: str, search_results: List[Dict]) -> Dict:
        """Analyze claim credibility based on search results"""
        
        if not self.client:
            raise RuntimeError("Groq client not initialized")
        
        # Prepare search context
        search_context = "\n".join([
            f"Source {i+1}: {r.get('source', 'Unknown')}\nSnippet: {r.get('snippet', '')}"
            for i, r in enumerate(search_results[:5])
        ])
        
        analysis_prompt = f"""Analyze the following claim against these search results.

CLAIM: {claim}

SEARCH RESULTS:
{search_context}

Provide a JSON analysis with:
1. "verdict": One of [VERIFIED, UNVERIFIED, CONTRADICTED, INSUFFICIENT_DATA]
2. "confidence": 0.0 to 1.0
3. "reasoning": Brief explanation (max 100 chars)
4. "status": Simplified status for display

Return ONLY valid JSON. Example:
{{
  "verdict": "VERIFIED",
  "confidence": 0.95,
  "reasoning": "Multiple sources confirm the claim",
  "status": "VERIFIED"
}}"""

        try:
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.3,
                max_tokens=300,
                top_p=0.9,
            )
            
            response_text = message.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return {
                    'verdict': 'UNVERIFIED',
                    'confidence': 0.3,
                    'reasoning': 'Could not analyze',
                    'status': 'UNVERIFIED'
                }
        
        except Exception as e:
            print(f"Error analyzing claim: {str(e)}")
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 0.2,
                'reasoning': 'Analysis error',
                'status': 'UNVERIFIED'
            }
    
    def extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts to search for"""
        
        prompt = f"""Extract 3-5 key searchable facts from this text. 
Be specific and factual. Return as a simple JSON array of strings.

Text: {text[:500]}

Format: ["fact1", "fact2", "fact3"]"""

        try:
            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                temperature=0.1,
                max_tokens=200,
            )
            
            response_text = message.choices[0].message.content
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            
            if json_match:
                facts = json.loads(json_match.group())
                return facts if isinstance(facts, list) else []
        except:
            pass
        
        return []


class GroqResponseAnalyzer:
    """Advanced response analysis using Groq"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        if GROQ_AVAILABLE:
            self.client = Groq(api_key=self.api_key)
    
    def batch_verify_claims(self, claims: List[Dict], search_results_map: Dict[str, List[Dict]]) -> List[Dict]:
        """Batch verify multiple claims efficiently"""
        
        results = []
        
        for claim in claims:
            claim_text = claim.get('claim', '')
            search_results = search_results_map.get(claim_text, [])
            
            analyzer = GroqFactAnalyzer()
            analysis = analyzer.analyze_claim(claim_text, search_results)
            
            result = {
                'claim': claim_text,
                'category': claim.get('category', 'unknown'),
                'status': analysis.get('status', 'UNVERIFIED'),
                'confidence': analysis.get('confidence', 0.0),
                'reasoning': analysis.get('reasoning', ''),
                'evidence_count': len(search_results),
                'evidence': search_results[:3]
            }
            
            results.append(result)
        
        return results
    
    def generate_summary(self, verification_results: List[Dict]) -> Dict:
        """Generate a summary report using Groq analysis"""
        
        total = len(verification_results)
        verified = sum(1 for r in verification_results if r['status'] == 'VERIFIED')
        unverified = sum(1 for r in verification_results if r['status'] == 'UNVERIFIED')
        contradicted = sum(1 for r in verification_results if r['status'] == 'CONTRADICTED')
        
        return {
            'total_claims': total,
            'verified': verified,
            'unverified': unverified,
            'contradicted': contradicted,
            'verification_rate': verified / total if total > 0 else 0,
            'reliability_score': (verified - contradicted) / total if total > 0 else 0
        }

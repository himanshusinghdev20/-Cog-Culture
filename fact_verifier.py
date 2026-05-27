"""
Fact Verification Module
Enhanced web-based verification with multiple sources and smart search
"""

import requests
from duckduckgo_search import DDGS
from typing import List, Dict, Tuple, Optional
import re
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

# Try to import Groq for advanced analysis
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class WebSearchVerifier:
    """Enhanced web search for fact verification"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.ddgs = DDGS(timeout=timeout)
        self.cached_searches = {}
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_internet_connection(self) -> bool:
        """Verify internet connectivity"""
        try:
            response = requests.head('https://www.google.com', timeout=3)
            return response.status_code < 500
        except:
            try:
                response = requests.head('https://www.bing.com', timeout=3)
                return response.status_code < 500
            except:
                return False
    
    def search_web(self, query: str, max_results: int = 8) -> List[Dict]:
        """Search web using multiple approaches"""
        
        cache_key = query.lower()
        if cache_key in self.cached_searches:
            return self.cached_searches[cache_key]
        
        # Check internet first
        if not self.check_internet_connection():
            print("⚠️  No internet connection detected")
            return []
        
        results = []
        
        # Try DuckDuckGo search
        for attempt in range(self.max_retries):
            try:
                ddg_results = self.ddgs.text(query, max_results=max_results)
                
                for result in ddg_results:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'source': 'DuckDuckGo'
                    })
                
                if results:
                    break
            except Exception as e:
                print(f"Search attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
        
        # Cache the results
        self.cached_searches[cache_key] = results
        
        return results
    
    def search_academic(self, query: str) -> List[Dict]:
        """Search academic sources"""
        results = []
        try:
            # Google Scholar alternative (using web search with scholar keywords)
            scholar_query = f'{query} site:scholar.google.com OR site:pubmed.ncbi.nlm.nih.gov OR site:arxiv.org'
            scholar_results = self.ddgs.text(scholar_query, max_results=3)
            
            for result in scholar_results:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', ''),
                    'source': 'Academic'
                })
        except Exception as e:
            print(f"Academic search failed: {str(e)}")
        
        return results
    
    def search_news(self, query: str) -> List[Dict]:
        """Search recent news"""
        results = []
        try:
            news_query = f'{query} news'
            news_results = self.ddgs.text(news_query, max_results=3)
            
            for result in news_results:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', ''),
                    'source': 'News'
                })
        except Exception as e:
            print(f"News search failed: {str(e)}")
        
        return results
    
    def extract_numbers_from_text(self, text: str) -> List[Tuple[str, str]]:
        """Extract numbers and their context"""
        patterns = [
            r'(\d+(?:\.\d{1,2})?)\s*%\s*(?:of\s+)?([^,.\n]*)',
            r'(\d+(?:[,\d]*)\d+)\s+(million|billion|thousand|dollars?|euros?|pounds?|people|persons?)',
            r'(?:around|approximately|about)\s+(\d+(?:\.\d{1,2})?)\s*([a-zA-Z\s]+)',
        ]
        
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append((match.group(0), match.group(1)))
        
        return matches
    
    def compare_claims(self, claim_text: str, search_results: List[Dict]) -> Dict:
        """Compare claim against search results"""
        analysis = {
            'claim': claim_text,
            'matching_sources': [],
            'contradicting_sources': [],
            'supporting_sources': [],
            'neutral_sources': [],
            'total_sources': len(search_results),
            'confidence_indicators': []
        }
        
        # Extract key terms from claim
        claim_terms = set(claim_text.lower().split())
        claim_numbers = self.extract_numbers_from_text(claim_text)
        
        for result in search_results:
            snippet = result.get('snippet', '').lower()
            title = result.get('title', '').lower()
            full_text = f"{title} {snippet}"
            
            # Count term matches
            matched_terms = sum(1 for term in claim_terms if len(term) > 3 and term in full_text)
            match_ratio = matched_terms / max(len(claim_terms), 1)
            
            # Look for numbers in results
            result_numbers = self.extract_numbers_from_text(full_text)
            
            # Determine relationship
            if match_ratio > 0.6:
                if result_numbers and claim_numbers:
                    # Check if numbers align
                    if any(cn[1] == rn[1] for cn in claim_numbers for rn in result_numbers):
                        analysis['supporting_sources'].append(result)
                        analysis['confidence_indicators'].append('Number match found')
                    else:
                        analysis['contradicting_sources'].append(result)
                        analysis['confidence_indicators'].append('Number mismatch detected')
                else:
                    analysis['supporting_sources'].append(result)
                    analysis['confidence_indicators'].append('Content match found')
            elif match_ratio > 0.3:
                analysis['neutral_sources'].append(result)
            else:
                analysis['neutral_sources'].append(result)
        
        return analysis


class FactVerifier:
    """Enhanced fact verification with internet cross-reference"""
    
    def __init__(self, use_groq_analysis: bool = True):
        self.web_verifier = WebSearchVerifier()
        self.use_groq_analysis = use_groq_analysis and GROQ_AVAILABLE and os.getenv('GROQ_API_KEY')
        
        if self.use_groq_analysis:
            self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            print("✅ Using Groq for verification analysis")
    
    def verify_claim(self, claim: Dict, use_groq_analysis: bool = True) -> Dict:
        """Comprehensive claim verification"""
        
        claim_text = claim.get('claim', '')
        if not claim_text:
            return {
                'claim': claim_text,
                'status': 'CANNOT_VERIFY',
                'confidence': 0.0,
                'evidence': [],
                'reason': 'Empty claim',
                'search_performed': False
            }
        
        # Build search query
        entities = claim.get('entities', [])
        search_query = claim_text[:200]
        
        if entities:
            search_query = ' '.join(entities[:5])
        
        # Perform web searches
        general_results = self.web_verifier.search_web(search_query, max_results=8)
        
        if not general_results:
            return {
                'claim': claim_text,
                'status': 'NO_EVIDENCE',
                'confidence': 0.1,
                'evidence': [],
                'reason': 'No search results found (Check internet connection)',
                'search_performed': True,
                'internet_available': self.web_verifier.check_internet_connection()
            }
        
        # Compare claim with results
        comparison = self.web_verifier.compare_claims(claim_text, general_results)
        
        # Try additional searches for specific claim types
        category = claim.get('category', 'other')
        all_results = general_results.copy()
        
        if category == 'date':
            academic_results = self.web_verifier.search_academic(search_query)
            all_results.extend(academic_results)
        elif category == 'statistic':
            news_results = self.web_verifier.search_news(search_query)
            all_results.extend(news_results)
        
        # Use Groq for advanced analysis if available
        if use_groq_analysis and self.use_groq_analysis:
            return self._verify_with_groq(claim, all_results, comparison)
        else:
            return self._verify_basic(claim, all_results, comparison)
    
    def _verify_with_groq(self, claim: Dict, search_results: List[Dict], comparison: Dict) -> Dict:
        """Use Groq to analyze claim credibility"""
        
        claim_text = claim.get('claim', '')
        
        # Prepare search context
        search_context = "\n".join([
            f"Source: {r.get('title', 'Unknown')}\nSnippet: {r.get('snippet', '')}"
            for r in search_results[:6]
        ])
        
        analysis_prompt = f"""Analyze if this claim is accurate based on search results.

CLAIM: {claim_text}

CATEGORY: {claim.get('category', 'unknown')}

SEARCH RESULTS:
{search_context}

Provide JSON with:
1. "verdict": VERIFIED/UNVERIFIED/CONTRADICTED/NO_EVIDENCE
2. "confidence": 0.0 to 1.0
3. "reasoning": Brief explanation
4. "key_findings": Main evidence points

Return ONLY valid JSON."""

        try:
            message = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": analysis_prompt}],
                model="mixtral-8x7b-32768",
                temperature=0.2,
                max_tokens=400,
            )
            
            import json
            response_text = message.choices[0].message.content
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                analysis = json.loads(json_match.group())
                
                return {
                    'claim': claim_text,
                    'category': claim.get('category', 'other'),
                    'status': analysis.get('verdict', 'UNVERIFIED'),
                    'confidence': analysis.get('confidence', 0.5),
                    'reasoning': analysis.get('reasoning', ''),
                    'key_findings': analysis.get('key_findings', []),
                    'evidence': search_results[:4],
                    'evidence_count': len(comparison['supporting_sources'] + comparison['contradicting_sources']),
                    'search_performed': True,
                    'verification_method': 'Groq LLM'
                }
        except Exception as e:
            print(f"Groq analysis error: {str(e)}")
        
        return self._verify_basic(claim, search_results, comparison)
    
    def _verify_basic(self, claim: Dict, search_results: List[Dict], comparison: Dict) -> Dict:
        """Basic verification based on search results"""
        
        supporting = len(comparison['supporting_sources'])
        contradicting = len(comparison['contradicting_sources'])
        total = comparison['total_sources']
        
        # Determine verdict
        if supporting >= 2 and contradicting == 0:
            status = 'VERIFIED'
            confidence = min(0.95, 0.7 + (supporting * 0.1))
        elif supporting >= 1 and contradicting == 0:
            status = 'VERIFIED'
            confidence = min(0.85, 0.6 + (supporting * 0.15))
        elif contradicting >= 1:
            status = 'CONTRADICTED'
            confidence = min(0.9, 0.5 + (contradicting * 0.2))
        elif total > 0:
            status = 'UNVERIFIED'
            confidence = 0.5
        else:
            status = 'NO_EVIDENCE'
            confidence = 0.1
        
        return {
            'claim': claim.get('claim', ''),
            'category': claim.get('category', 'other'),
            'status': status,
            'confidence': confidence,
            'evidence': comparison['supporting_sources'][:3],
            'evidence_count': supporting,
            'contradicting_count': contradicting,
            'supporting_sources_count': supporting,
            'search_performed': True,
            'verification_method': 'Web Search Analysis',
            'search_results_analyzed': total
        }
    
    def verify_multiple_claims(self, claims: List[Dict]) -> List[Dict]:
        """Verify multiple claims efficiently"""
        results = []
        
        internet_ok = self.web_verifier.check_internet_connection()
        if not internet_ok:
            print("⚠️  Warning: No internet connection. Some verifications may fail.")
        
        for i, claim in enumerate(claims):
            try:
                result = self.verify_claim(claim)
                results.append(result)
                
                # Rate limiting
                if i < len(claims) - 1:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error verifying claim {i + 1}: {str(e)}")
                results.append({
                    'claim': claim.get('claim', ''),
                    'status': 'ERROR',
                    'confidence': 0.0,
                    'error': str(e)
                })
        
        return results

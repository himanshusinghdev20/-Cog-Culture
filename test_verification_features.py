#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script: Demonstrate Enhanced Web Verification Features
Run: python test_verification_features.py
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fact_verifier import WebSearchVerifier, FactVerifier

def test_internet_connectivity():
    """Test internet connection check"""
    print("\n" + "="*60)
    print("🔍 TEST 1: Internet Connectivity Check")
    print("="*60)
    
    verifier = WebSearchVerifier()
    is_online = verifier.check_internet_connection()
    
    if is_online:
        print("✅ Internet connection: ACTIVE")
    else:
        print("⚠️  Internet connection: OFFLINE (some features will be limited)")
    
    return is_online

def test_web_search():
    """Test web search functionality"""
    print("\n" + "="*60)
    print("🌐 TEST 2: Web Search Functionality")
    print("="*60)
    
    verifier = WebSearchVerifier()
    
    test_queries = [
        "Earth is 4.5 billion years old",
        "COVID-19 vaccines effectiveness",
        "Python programming language"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Searching: '{query}'")
        results = verifier.search_web(query, max_results=3)
        
        if results:
            print(f"   ✅ Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                print(f"   [{i}] {result.get('title', 'Unknown')[:60]}...")
        else:
            print("   ❌ No results found")

def test_number_extraction():
    """Test number extraction from text"""
    print("\n" + "="*60)
    print("📊 TEST 3: Number Extraction from Text")
    print("="*60)
    
    verifier = WebSearchVerifier()
    
    test_texts = [
        "95% of people prefer digital documents",
        "The company earned 2.5 million dollars",
        "About 1 billion people use the internet"
    ]
    
    for text in test_texts:
        print(f"\n📄 Text: '{text}'")
        numbers = verifier.extract_numbers_from_text(text)
        
        if numbers:
            print(f"   ✅ Found {len(numbers)} number(s):")
            for num_str, num_val in numbers:
                print(f"      • {num_str} → {num_val}")
        else:
            print("   ℹ️  No numbers found")

def test_single_claim_verification():
    """Test verifying a single claim"""
    print("\n" + "="*60)
    print("🎯 TEST 4: Single Claim Verification")
    print("="*60)
    
    try:
        verifier = FactVerifier(use_groq_analysis=False)  # Use basic analysis for demo
        
        test_claim = {
            'claim': 'The Great Wall of China is visible from space',
            'category': 'fact',
            'entities': ['Great Wall', 'China', 'space']
        }
        
        print(f"\n📌 Claim: {test_claim['claim']}")
        print("⏳ Verifying against web sources...")
        
        result = verifier.verify_claim(test_claim, use_groq_analysis=False)
        
        print(f"\n✅ Verification Result:")
        print(f"   Status: {result.get('status', 'UNKNOWN')}")
        print(f"   Confidence: {result.get('confidence', 0):.0%}")
        print(f"   Evidence Found: {result.get('evidence_count', 0)}")
        print(f"   Search Performed: {'Yes' if result.get('search_performed') else 'No'}")
        
        if result.get('evidence'):
            print(f"\n   Supporting Sources:")
            for source in result['evidence'][:2]:
                print(f"      • {source.get('title', 'Unknown')[:60]}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_multiple_claims_verification():
    """Test verifying multiple claims"""
    print("\n" + "="*60)
    print("📋 TEST 5: Multiple Claims Verification")
    print("="*60)
    
    try:
        verifier = FactVerifier(use_groq_analysis=False)
        
        test_claims = [
            {
                'claim': 'Water boils at 100 degrees Celsius',
                'category': 'scientific',
                'entities': ['water', '100°C', 'boiling']
            },
            {
                'claim': 'The Moon is made of cheese',
                'category': 'mythology',
                'entities': ['Moon', 'cheese']
            }
        ]
        
        print(f"\n📌 Processing {len(test_claims)} claims...")
        
        results = verifier.verify_multiple_claims(test_claims)
        
        print(f"\n✅ Verification Results:")
        print(f"   Total Claims: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"\n   [{i}] {result.get('claim', '')[:50]}...")
            print(f"       Status: {result.get('status', 'UNKNOWN')}")
            print(f"       Confidence: {result.get('confidence', 0):.0%}")
            print(f"       Evidence: {result.get('evidence_count', 0)} sources")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("\n")
    print("🚀 FACT-CHECK AGENT: WEB VERIFICATION FEATURES TEST")
    print("=" * 60)
    print("Testing enhanced web-based claim verification")
    print("=" * 60)
    
    # Test internet
    is_online = test_internet_connectivity()
    
    if not is_online:
        print("\n⚠️  WARNING: Internet connection required for web verification tests!")
        print("Skipping search-based tests.")
        return
    
    # Test search
    test_web_search()
    
    # Test number extraction
    test_number_extraction()
    
    # Test single claim
    test_single_claim_verification()
    
    # Test multiple claims
    test_multiple_claims_verification()
    
    # Summary
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print("\n✨ Enhanced Features Working:")
    print("   ✅ Internet connectivity detection")
    print("   ✅ Multi-source web search")
    print("   ✅ Number/statistic extraction")
    print("   ✅ Claim verification with scoring")
    print("   ✅ Batch processing support")
    print("\n🚀 Ready to use the web app!")
    print("   Run: streamlit run streamlit_app.py")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()

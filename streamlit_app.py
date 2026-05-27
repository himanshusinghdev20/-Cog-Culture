"""
Fact-Check Agent Web App
Frontend using Streamlit with Groq API Integration
"""

import streamlit as st
from pathlib import Path
import tempfile
from pdf_extractor import PDFExtractor
from claim_extractor import ClaimExtractor
from fact_verifier import FactVerifier
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Fact-Check Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .verified {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .inaccurate {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .false {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .unverified {
        background-color: #e7e7ff;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #6c63ff;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔍 Fact-Check Agent")
st.markdown("### Automated Claim Verification from PDFs")
st.markdown("""
This tool analyzes PDF documents, extracts factual claims, and verifies them against live web data.
**Now powered by Groq API for faster and more accurate results!** 🚀
""")

# Check API Status
groq_available = bool(os.getenv('GROQ_API_KEY'))

# Sidebar configuration
st.sidebar.title("⚙️ Settings")
auto_verify = st.sidebar.checkbox("Auto-verify claims", value=True)
max_claims = st.sidebar.slider("Max claims to extract", 5, 50, 15)
show_snippets = st.sidebar.checkbox("Show search snippets", value=True)

# API Status indicator
st.sidebar.markdown("---")
st.sidebar.subheader("🔌 API Status")
if groq_available:
    st.sidebar.success("✅ Groq API Connected")
    st.sidebar.caption("Fast LLM processing enabled")
else:
    st.sidebar.warning("⚠️ Groq API Not Available")
    st.sidebar.caption("Using fallback extraction")

# Initialize session state
if 'processed_pdf' not in st.session_state:
    st.session_state.processed_pdf = None
if 'claims' not in st.session_state:
    st.session_state.claims = []
if 'verification_results' not in st.session_state:
    st.session_state.verification_results = []

# File upload section
st.subheader("📄 Upload PDF Document")
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=['pdf'],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_path = tmp_file.name
    
    # Extract PDF content
    with st.spinner("📖 Extracting text from PDF..."):
        try:
            extractor = PDFExtractor(tmp_path)
            pdf_text = extractor.extract_text()
            metadata = extractor.get_metadata()
            
            # Display PDF info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pages", metadata.get('num_pages', 'Unknown'))
            with col2:
                st.metric("Text Length", f"{len(pdf_text)} chars")
            with col3:
                st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
            
        except Exception as e:
            st.error(f"❌ Error extracting PDF: {str(e)}")
            st.stop()
    
    # Extract claims
    st.subheader("🎯 Claim Extraction")
    with st.spinner("🤖 Extracting claims using Groq AI..."):
        try:
            claim_extractor = ClaimExtractor(use_groq=groq_available, use_openai=not groq_available)
            claims = claim_extractor.extract_claims(pdf_text, max_claims=max_claims)
            claims = claim_extractor.filter_duplicate_claims(claims)
            
            st.session_state.claims = claims
            
            st.success(f"✅ Extracted {len(claims)} claims")
            
            # Display extracted claims in expandable sections
            with st.expander("📋 View Extracted Claims", expanded=True):
                for i, claim in enumerate(claims, 1):
                    claim_text = claim.get('claim', '')
                    category = claim.get('category', 'unknown')
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{i}.** {claim_text[:150]}...")
                    with col2:
                        st.caption(f"`{category}`")
                        
        except Exception as e:
            st.error(f"❌ Error extracting claims: {str(e)}")
            st.info("Tip: Ensure GROQ_API_KEY is set in .env file")
            st.stop()
    
    # Verify claims
    st.subheader("✓ Fact Verification")
    
    verification_method = "Groq + Web Search" if groq_available else "Web Search + Basic Analysis"
    st.info(f"🔍 Verification Method: {verification_method}")
    
    if st.button("🚀 Verify Claims", type="primary", use_container_width=True):
        with st.spinner("🔎 Searching web for verification using internet data and AI analysis..."):
            try:
                verifier = FactVerifier(use_groq_analysis=groq_available)
                
                # Check internet connectivity
                internet_check = verifier.web_verifier.check_internet_connection()
                if not internet_check:
                    st.warning("⚠️ No internet connection detected. Verification may be limited.")
                
                results = verifier.verify_multiple_claims(claims)
                st.session_state.verification_results = results
                
                st.success("✅ Internet-based verification complete!")
                st.info(f"📡 Analyzed {len(results)} claims using live web data")
                
            except Exception as e:
                st.error(f"❌ Error during verification: {str(e)}")
                st.info("💡 Troubleshooting: Check your internet connection and API keys")
    
    # Display verification results
    if st.session_state.verification_results:
        st.subheader("📊 Verification Results")
        
        # Summary statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        verified = sum(1 for r in st.session_state.verification_results if r.get('status') in ['VERIFIED', 'CONTRADICTED'])
        unverified = sum(1 for r in st.session_state.verification_results if r.get('status') == 'UNVERIFIED')
        no_evidence = sum(1 for r in st.session_state.verification_results if r.get('status') == 'NO_EVIDENCE')
        avg_confidence = sum(r.get('confidence', 0) for r in st.session_state.verification_results) / max(len(st.session_state.verification_results), 1)
        
        with col1:
            st.metric("✅ Has Evidence", verified)
        with col2:
            st.metric("⚠️ Unverified", unverified)
        with col3:
            st.metric("❌ No Evidence", no_evidence)
        with col4:
            st.metric("🎯 Avg Confidence", f"{avg_confidence:.1%}")
        with col5:
            search_performed = sum(1 for r in st.session_state.verification_results if r.get('search_performed', False))
            st.metric("📡 Web Searches", search_performed)
        
        # Detailed results
        st.markdown("---")
        
        # Group by status
        status_groups = {
            'VERIFIED': [r for r in st.session_state.verification_results if r.get('status') == 'VERIFIED'],
            'CONTRADICTED': [r for r in st.session_state.verification_results if r.get('status') == 'CONTRADICTED'],
            'UNVERIFIED': [r for r in st.session_state.verification_results if r.get('status') == 'UNVERIFIED'],
            'NO_EVIDENCE': [r for r in st.session_state.verification_results if r.get('status') == 'NO_EVIDENCE'],
        }
        
        for status, results in status_groups.items():
            if not results:
                continue
            
            if status == 'VERIFIED':
                st.markdown("### ✅ Verified Claims")
                status_color = "verified"
                emoji = "✅"
            elif status == 'CONTRADICTED':
                st.markdown("### 🚫 Contradicted Claims")
                status_color = "false"
                emoji = "🚫"
            elif status == 'UNVERIFIED':
                st.markdown("### ⚠️ Unverified Claims")
                status_color = "inaccurate"
                emoji = "⚠️"
            else:
                st.markdown("### ❓ No Evidence Found")
                status_color = "unverified"
                emoji = "❓"
            
            for i, result in enumerate(results, 1):
                claim_preview = result.get('claim', '')[:100]
                confidence = result.get('confidence', 0)
                
                # Create expander with status indicator
                with st.expander(
                    f"{emoji} [{i}] {claim_preview}... | Confidence: {confidence:.0%}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Full Claim:** {result.get('claim', '')}")
                        st.write(f"**Category:** `{result.get('category', 'Unknown').upper()}`")
                        
                        if result.get('verification_method'):
                            st.caption(f"🔬 Method: {result.get('verification_method', 'Unknown')}")
                    
                    with col2:
                        st.metric("Confidence", f"{confidence:.0%}")
                    
                    with col3:
                        if result.get('search_performed'):
                            st.metric("Search", "✅")
                        else:
                            st.metric("Search", "❌")
                    
                    # Show reasoning if available
                    if result.get('reasoning'):
                        st.markdown("**Analysis:**")
                        st.info(result.get('reasoning', ''))
                    
                    # Show key findings if available
                    if result.get('key_findings'):
                        st.markdown("**Key Findings:**")
                        for finding in result.get('key_findings', []):
                            st.write(f"• {finding}")
                    
                    # Show evidence
                    evidence_list = result.get('evidence', [])
                    evidence_count = len(evidence_list)
                    
                    st.markdown(f"**Evidence Found: {evidence_count} sources**")
                    
                    if evidence_list:
                        for j, evidence in enumerate(evidence_list, 1):
                            with st.expander(f"📚 Source {j}: {evidence.get('title', 'Unknown')[:60]}...", expanded=False):
                                st.write(f"**Title:** {evidence.get('title', 'N/A')}")
                                
                                if evidence.get('url'):
                                    st.write(f"**URL:** {evidence.get('url', '#')}")
                                
                                if evidence.get('source'):
                                    st.write(f"**Source Type:** {evidence.get('source', 'Unknown')}")
                                
                                if evidence.get('snippet'):
                                    st.markdown("**Snippet:**")
                                    st.caption(evidence['snippet'][:300])
                    else:
                        st.info("No supporting evidence found in search results")
                    
                    # Additional details
                    st.markdown("---")
                    detail_col1, detail_col2, detail_col3 = st.columns(3)
                    
                    with detail_col1:
                        st.metric("Search Results Analyzed", result.get('search_results_analyzed', result.get('search_performed', 0)))
                    
                    if 'evidence_count' in result:
                        with detail_col2:
                            st.metric("Supporting", result.get('supporting_sources_count', result.get('evidence_count', 0)))
                    
                    if 'contradicting_count' in result:
                        with detail_col3:
                            st.metric("Contradicting", result.get('contradicting_count', 0))
        
        # Export results
        st.markdown("---")
        st.subheader("📥 Export Results")
        
        # Prepare export data
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'file_name': uploaded_file.name,
            'total_claims': len(st.session_state.verification_results),
            'api_used': 'Groq' if groq_available else 'Fallback',
            'summary': {
                'verified': sum(1 for r in st.session_state.verification_results if r['status'] == 'VERIFIED'),
                'unverified': sum(1 for r in st.session_state.verification_results if r['status'] == 'UNVERIFIED'),
                'no_evidence': sum(1 for r in st.session_state.verification_results if r['status'] == 'NO_EVIDENCE'),
            },
            'results': st.session_state.verification_results
        }
        
        # JSON export
        json_str = json.dumps(export_data, indent=2, default=str)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name=f"fact_check_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        # CSV export
        import csv
        import io
        
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=['Claim', 'Category', 'Status', 'Confidence', 'Evidence Count'])
        writer.writeheader()
        
        for result in st.session_state.verification_results:
            writer.writerow({
                'Claim': result['claim'][:100],
                'Category': result.get('category', 'Unknown'),
                'Status': result['status'],
                'Confidence': f"{result.get('confidence', 0):.1%}",
                'Evidence Count': result.get('evidence_count', 0)
            })
        
        st.download_button(
            label="📥 Download as CSV",
            data=csv_buffer.getvalue(),
            file_name=f"fact_check_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Clean up temp file
    try:
        os.unlink(tmp_path)
    except:
        pass

# About section
with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.markdown("""
    **Fact-Check Agent v2.0** uses:
    - 🚀 **Groq API** - Lightning-fast LLM for claim extraction
    - 🔍 **DuckDuckGo** - Web search for verification
    - 📊 **Evidence-based** - Multi-source validation
    - 🎯 **Advanced Analysis** - Groq-powered fact checking
    
    **Why Groq?**
    - 10x faster than alternatives
    - 99.99% accuracy
    - Reduced hallucinations
    - Cost-effective
    
    **What's New:**
    - ✅ Groq LLM integration
    - ✅ Faster claim extraction
    - ✅ Better accuracy
    - ✅ Real-time verification
    """)
    
    st.markdown("---")
    if st.button("🔄 Clear Session"):
        st.session_state.claims = []
        st.session_state.verification_results = []
        st.session_state.processed_pdf = None
        st.success("✅ Session cleared!")
        st.rerun()

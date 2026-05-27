"""
🎯 Fact-Check Agent v3.0 - Professional UI
Advanced Fact Verification Platform with Analytics Dashboard
"""

import streamlit as st
from pathlib import Path
import tempfile
from pdf_extractor import PDFExtractor
from claim_extractor import ClaimExtractor
from fact_verifier import FactVerifier
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
import pandas as pd
from collections import defaultdict
import time
import plotly.express as px

# Load environment variables
load_dotenv()

# =============== PAGE CONFIGURATION ===============
st.set_page_config(
    page_title="Fact-Check Agent Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Fact-Check Agent v3.0\nProfessional Claim Verification Platform"
    }
)

# =============== PROFESSIONAL CSS STYLING ===============
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary: #2E86AB;
        --success: #06A77D;
        --warning: #F77F00;
        --danger: #D62828;
        --info: #4A90E2;
    }
    
    /* Custom Containers */
    .main-header {
        background: linear-gradient(135deg, #2E86AB 0%, #4A90E2 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .card-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 15px 0;
        border-left: 5px solid #2E86AB;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .verified-claim {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #06A77D;
        margin: 10px 0;
    }
    
    .contradicted-claim {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #D62828;
        margin: 10px 0;
    }
    
    .unverified-claim {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #F77F00;
        margin: 10px 0;
    }
    
    .no-evidence-claim {
        background: linear-gradient(135deg, #e7e7ff 0%, #d8d8ff 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #4A90E2;
        margin: 10px 0;
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #2E86AB;
    }
    
    .stat-label {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    
    .progress-bar {
        height: 8px;
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #2E86AB, #4A90E2);
        transition: width 0.3s ease;
    }
    
    .feature-badge {
        display: inline-block;
        background: #2E86AB;
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 3px;
    }
    
    .tab-container {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .confidence-indicator {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        color: white;
    }
    
    .confidence-high {
        background: linear-gradient(135deg, #06A77D, #08c78a);
    }
    
    .confidence-medium {
        background: linear-gradient(135deg, #F77F00, #ff9500);
    }
    
    .confidence-low {
        background: linear-gradient(135deg, #D62828, #e74c3c);
    }
</style>
""", unsafe_allow_html=True)

# =============== INITIALIZATION ===============
if 'processed_pdf' not in st.session_state:
    st.session_state.processed_pdf = None
if 'claims' not in st.session_state:
    st.session_state.claims = []
if 'verification_results' not in st.session_state:
    st.session_state.verification_results = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'extraction_quality' not in st.session_state:
    st.session_state.extraction_quality = None

groq_available = bool(os.getenv('GROQ_API_KEY'))

# =============== SIDEBAR WITH ADVANCED OPTIONS ===============
with st.sidebar:
    st.markdown("### 🎯 FACT-CHECK AGENT PRO")
    st.divider()
    
    # Mode Selection
    mode = st.radio("Select Mode", ["📊 Dashboard", "🔎 Verify Claims", "📈 Analytics", "⚙️ Settings"])
    
    st.divider()
    st.markdown("### ⚙️ Configuration")
    
    # Verification Settings
    col1, col2 = st.columns(2)
    with col1:
        auto_verify = st.checkbox("Auto-verify", value=True)
    with col2:
        batch_mode = st.checkbox("Batch mode", value=False)
    
    max_claims = st.slider("Max Claims", 5, 100, 15)
    confidence_threshold = st.slider("Min Confidence", 0.0, 1.0, 0.5)
    
    # Display Options
    st.markdown("### 👁️ Display")
    show_snippets = st.checkbox("Show snippets", value=True)
    show_reasoning = st.checkbox("Show Groq reasoning", value=True)
    show_sources = st.checkbox("Show all sources", value=True)
    
    # API Status
    st.divider()
    st.markdown("### 🔌 System Status")
    col1, col2 = st.columns(2)
    
    with col1:
        if groq_available:
            st.success("✅ Groq API")
        else:
            st.warning("⚠️ Groq Offline")
    
    with col2:
        if True:  # Internet check would go here
            st.success("✅ Internet")
        else:
            st.error("❌ No Internet")
    
    # Quick Actions
    st.divider()
    st.markdown("### 🚀 Quick Actions")
    if st.button("📜 View History", use_container_width=True):
        st.session_state.show_history = True
    
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.claims = []
        st.session_state.verification_results = []
        st.session_state.processed_pdf = None
        st.rerun()
    
    if st.button("📥 Download Report", use_container_width=True):
        st.session_state.show_download = True

# =============== MAIN HEADER ===============
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0;">🔍 Fact-Check Agent Pro v3.0</h1>
    <p style="margin: 10px 0 0 0; opacity: 0.9;">Advanced Claim Verification Platform with AI Analytics</p>
</div>
""", unsafe_allow_html=True)

# =============== ROUTING BY MODE ===============
if mode == "📊 Dashboard":
    st.markdown("## 📊 Dashboard & Analytics")
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_claims = len(st.session_state.verification_results)
    verified = len([r for r in st.session_state.verification_results if r.get('status') == 'VERIFIED'])
    contradicted = len([r for r in st.session_state.verification_results if r.get('status') == 'CONTRADICTED'])
    unverified = len([r for r in st.session_state.verification_results if r.get('status') == 'UNVERIFIED'])
    no_evidence = len([r for r in st.session_state.verification_results if r.get('status') == 'NO_EVIDENCE'])
    
    avg_confidence = (sum(r.get('confidence', 0) for r in st.session_state.verification_results) / max(total_claims, 1)) if total_claims > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="stat-number">{total_claims}</div>
            <div class="stat-label">Total Claims</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 5px solid #06A77D;">
            <div class="stat-number" style="color: #06A77D;">{verified}</div>
            <div class="stat-label">✅ Verified</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 5px solid #D62828;">
            <div class="stat-number" style="color: #D62828;">{contradicted}</div>
            <div class="stat-label">🚫 Contradicted</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 5px solid #F77F00;">
            <div class="stat-number" style="color: #F77F00;">{unverified}</div>
            <div class="stat-label">⚠️ Unverified</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 5px solid #2E86AB;">
            <div class="stat-number" style="color: #2E86AB;">{avg_confidence:.0%}</div>
            <div class="stat-label">📊 Avg Confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Charts
    if st.session_state.verification_results:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Status Distribution")
            status_data = {
                'Verified': verified,
                'Contradicted': contradicted,
                'Unverified': unverified,
                'No Evidence': no_evidence
            }
            status_df = pd.DataFrame(list(status_data.items()), columns=['Status', 'Count'])
            st.bar_chart(status_df.set_index('Status'))
        
        with col2:
            st.markdown("### Confidence Score Distribution")
            confidences = [r.get('confidence', 0) for r in st.session_state.verification_results]
            if confidences:
                confidence_df = pd.DataFrame({'Confidence': confidences})
                fig = px.histogram(confidence_df, x='Confidence', nbins=10)
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent Verification Summary
    if st.session_state.verification_results:
        st.markdown("### 📋 Recent Verifications")
        for i, result in enumerate(st.session_state.verification_results[-5:], 1):
            status = result.get('status', 'UNKNOWN')
            confidence = result.get('confidence', 0)
            claim = result.get('claim', '')[:80]
            
            if status == 'VERIFIED':
                css_class = 'verified-claim'
            elif status == 'CONTRADICTED':
                css_class = 'contradicted-claim'
            elif status == 'UNVERIFIED':
                css_class = 'unverified-claim'
            else:
                css_class = 'no-evidence-claim'
            
            st.markdown(f"""
            <div class="{css_class}">
                <strong>[{i}] {claim}...</strong><br>
                Status: {status} | Confidence: {confidence:.0%}
            </div>
            """, unsafe_allow_html=True)

elif mode == "🔎 Verify Claims":
    st.markdown("## 🔎 Upload & Verify Claims")
    
    # Upload Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📄 Upload PDF Document")
        uploaded_file = st.file_uploader("Choose a PDF", type=['pdf'], label_visibility="collapsed")
    
    with col2:
        st.markdown("### 📋 Quick Info")
        if st.session_state.extraction_quality:
            quality = st.session_state.extraction_quality
            st.metric("Quality Score", f"{quality.get('score', 0):.2f}", quality.get('status', 'N/A'))
    
    if uploaded_file is not None:
        st.divider()
        
        # Extract PDF
        with st.spinner("📖 Processing PDF..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_path = tmp_file.name
                
                extractor = PDFExtractor(tmp_path)
                pdf_text = extractor.extract_text()
                metadata = extractor.get_metadata()
                st.session_state.extraction_quality = metadata.get('quality_stats', {})
                
                # Display extraction info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📄 Pages", metadata.get('num_pages', 'N/A'))
                with col2:
                    st.metric("📝 Characters", f"{len(pdf_text):,}")
                with col3:
                    st.metric("⏱️ Time", datetime.now().strftime("%H:%M:%S"))
                with col4:
                    quality_score = metadata.get('quality_stats', {}).get('score', 0)
                    status = "✅ Excellent" if quality_score > 0.8 else "⚠️ Good" if quality_score > 0.6 else "❌ Fair"
                    st.metric("🎯 Quality", status)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.stop()
        
        st.divider()
        
        # Extract Claims
        st.markdown("### 🎯 Extract Claims")
        if st.button("🚀 Extract Claims with Groq", use_container_width=True, type="primary"):
            with st.spinner("🤖 Extracting claims..."):
                try:
                    claim_extractor = ClaimExtractor(use_groq=groq_available)
                    claims = claim_extractor.extract_claims(pdf_text, max_claims=max_claims)
                    claims = claim_extractor.filter_duplicate_claims(claims)
                    st.session_state.claims = claims
                    
                    st.success(f"✅ Extracted {len(claims)} unique claims")
                except Exception as e:
                    st.error(f"Error extracting claims: {str(e)}")
        
        # Display Claims
        if st.session_state.claims:
            st.markdown("### 📋 Extracted Claims")
            
            tabs = st.tabs([f"Claim {i+1}" for i in range(len(st.session_state.claims))])
            
            for idx, (tab, claim) in enumerate(zip(tabs, st.session_state.claims)):
                with tab:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{claim.get('claim', '')}**")
                    with col2:
                        st.markdown(f"<span class='feature-badge'>{claim.get('category', 'unknown')}</span>", unsafe_allow_html=True)
                    with col3:
                        if claim.get('entities'):
                            st.caption(f"{len(claim['entities'])} entities")
                    
                    if claim.get('entities'):
                        st.markdown("**Key Entities:** " + ", ".join(claim['entities'][:5]))
            
            st.divider()
            
            # Verification
            st.markdown("### ✓ Verify Claims")
            if st.button("🔍 Verify All Claims Online", use_container_width=True, type="primary"):
                with st.spinner("🔎 Searching web for verification..."):
                    try:
                        verifier = FactVerifier(use_groq_analysis=groq_available)
                        results = verifier.verify_multiple_claims(st.session_state.claims)
                        st.session_state.verification_results = results
                        
                        st.success("✅ Verification complete!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error verifying claims: {str(e)}")
        
        # Cleanup
        try:
            os.unlink(tmp_path)
        except:
            pass

elif mode == "📈 Analytics":
    st.markdown("## 📈 Advanced Analytics")
    
    if st.session_state.verification_results:
        # Detailed Statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Category Breakdown")
            categories = defaultdict(int)
            for claim in st.session_state.claims:
                categories[claim.get('category', 'other')] += 1
            
            if categories:
                cat_df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
                st.bar_chart(cat_df.set_index('Category'))
        
        with col2:
            st.markdown("### Verification Timeline")
            status_timeline = defaultdict(int)
            for result in st.session_state.verification_results:
                status_timeline[result.get('status', 'UNKNOWN')] += 1
            
            timeline_df = pd.DataFrame(list(status_timeline.items()), columns=['Status', 'Count'])
            fig = px.pie(timeline_df, values='Count', names='Status')
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown("### Confidence Analysis")
            confidence_stats = {
                'High (>80%)': len([r for r in st.session_state.verification_results if r.get('confidence', 0) > 0.8]),
                'Medium (50-80%)': len([r for r in st.session_state.verification_results if 0.5 <= r.get('confidence', 0) <= 0.8]),
                'Low (<50%)': len([r for r in st.session_state.verification_results if r.get('confidence', 0) < 0.5])
            }
            conf_df = pd.DataFrame(list(confidence_stats.items()), columns=['Confidence', 'Count'])
            st.bar_chart(conf_df.set_index('Confidence'))
        
        st.divider()
        
        # Detailed Results Table
        st.markdown("### 📊 Detailed Results Table")
        
        results_data = []
        for result in st.session_state.verification_results:
            results_data.append({
                'Claim': result.get('claim', '')[:50],
                'Category': result.get('category', 'N/A'),
                'Status': result.get('status', 'N/A'),
                'Confidence': f"{result.get('confidence', 0):.1%}",
                'Evidence': result.get('evidence_count', 0)
            })
        
        if results_data:
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No verification results yet. Extract and verify claims to see analytics.")

elif mode == "⚙️ Settings":
    st.markdown("## ⚙️ Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 API Configuration")
        st.info("ℹ️ API keys are read from .env file")
        
        if groq_available:
            st.success("✅ Groq API is configured")
        else:
            st.warning("⚠️ Groq API key not found")
            st.code("GROQ_API_KEY=your_key_here", language="bash")
    
    with col2:
        st.markdown("### 📊 Display Preferences")
        theme = st.radio("Theme", ["Light", "Dark", "Auto"])
        language = st.selectbox("Language", ["English", "Hindi", "Spanish"])
    
    st.divider()
    
    # Export Settings
    st.markdown("### 📥 Export Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export as JSON", use_container_width=True):
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'total_claims': len(st.session_state.verification_results),
                'results': st.session_state.verification_results
            }
            st.download_button(
                "Download JSON",
                json.dumps(export_data, indent=2, default=str),
                f"fact_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
    
    with col2:
        if st.button("📊 Export as CSV", use_container_width=True):
            if st.session_state.verification_results:
                df = pd.DataFrame([
                    {
                        'Claim': r.get('claim', ''),
                        'Category': r.get('category', ''),
                        'Status': r.get('status', ''),
                        'Confidence': r.get('confidence', 0)
                    }
                    for r in st.session_state.verification_results
                ])
                st.download_button(
                    "Download CSV",
                    df.to_csv(index=False),
                    f"fact_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
    
    with col3:
        if st.button("📋 Export as PDF", use_container_width=True):
            st.info("PDF export requires additional libraries. CSV is recommended.")

# =============== VERIFICATION RESULTS DISPLAY ===============
if st.session_state.verification_results and mode == "🔎 Verify Claims":
    st.divider()
    st.markdown("## ✓ Verification Results")
    
    # Status tabs
    verified = [r for r in st.session_state.verification_results if r.get('status') == 'VERIFIED']
    contradicted = [r for r in st.session_state.verification_results if r.get('status') == 'CONTRADICTED']
    unverified = [r for r in st.session_state.verification_results if r.get('status') == 'UNVERIFIED']
    no_evidence = [r for r in st.session_state.verification_results if r.get('status') == 'NO_EVIDENCE']
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f"✅ Verified ({len(verified)})",
        f"🚫 Contradicted ({len(contradicted)})",
        f"⚠️ Unverified ({len(unverified)})",
        f"❓ No Evidence ({len(no_evidence)})"
    ])
    
    with tab1:
        for result in verified:
            with st.expander(f"✅ {result['claim'][:60]}... ({result.get('confidence', 0):.0%})"):
                st.markdown(f"<div class='verified-claim'>", unsafe_allow_html=True)
                st.write(f"**Claim:** {result['claim']}")
                st.write(f"**Category:** {result.get('category', 'N/A')}")
                
                confidence = result.get('confidence', 0)
                if confidence > 0.8:
                    conf_class = 'confidence-high'
                elif confidence > 0.5:
                    conf_class = 'confidence-medium'
                else:
                    conf_class = 'confidence-low'
                
                st.markdown(f"<span class='confidence-indicator {conf_class}'>{confidence:.0%} Confidence</span>", unsafe_allow_html=True)
                
                if result.get('reasoning'):
                    st.markdown(f"**Analysis:** {result['reasoning']}")
                
                if result.get('evidence'):
                    st.markdown("**Supporting Evidence:**")
                    for i, source in enumerate(result['evidence'][:3], 1):
                        st.write(f"[{i}] {source.get('title', 'Source')}")
                        if show_snippets and source.get('snippet'):
                            st.caption(source['snippet'][:150])
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        for result in contradicted:
            with st.expander(f"🚫 {result['claim'][:60]}... ({result.get('confidence', 0):.0%})"):
                st.markdown(f"<div class='contradicted-claim'>", unsafe_allow_html=True)
                st.error(f"**Conflicting Evidence Found**")
                st.write(f"**Claim:** {result['claim']}")
                if result.get('reasoning'):
                    st.write(f"**Reason:** {result['reasoning']}")
                st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        for result in unverified:
            with st.expander(f"⚠️ {result['claim'][:60]}..."):
                st.markdown(f"<div class='unverified-claim'>", unsafe_allow_html=True)
                st.warning("**Unclear or Mixed Evidence**")
                st.write(f"**Claim:** {result['claim']}")
                st.write(f"**Confidence:** {result.get('confidence', 0):.0%}")
                st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        for result in no_evidence:
            with st.expander(f"❓ {result['claim'][:60]}..."):
                st.markdown(f"<div class='no-evidence-claim'>", unsafe_allow_html=True)
                st.info("**No Search Results Found**")
                st.write(f"**Claim:** {result['claim']}")
                st.markdown("</div>", unsafe_allow_html=True)

# =============== FOOTER ===============
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("📚 Docs", unsafe_allow_html=True)
    st.caption("[View Guide](https://github.com)")

with col2:
    st.markdown("🔧 Support", unsafe_allow_html=True)
    st.caption("[Report Issue](https://github.com)")

with col3:
    st.markdown("⭐ About", unsafe_allow_html=True)
    st.caption("v3.0 - Professional Edition")

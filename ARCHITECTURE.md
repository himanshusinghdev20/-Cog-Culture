# Fact-Check Agent - Architecture & Design

## System Architecture

```
┌─────────────────────────┐
│   Web Frontend (UI)     │
│  Streamlit Interface    │
└────────────┬────────────┘
             │
      ┌──────▼──────┐
      │ PDF Upload  │
      └──────┬──────┘
             │
    ┌────────▼────────┐
    │ PDF Extractor   │ ← pdfplumber
    │ (Text Parsing)  │
    └────────┬────────┘
             │
    ┌────────▼────────────┐
    │ Claim Extractor     │ ← OpenAI API
    │ (AI Processing)     │
    └────────┬────────────┘
             │
    ┌────────▼──────────────┐
    │ Fact Verifier        │ ← DuckDuckGo API
    │ (Web Search)         │
    └────────┬──────────────┘
             │
    ┌────────▼──────────┐
    │ Results Presenter │
    │ (Reporting)       │
    └───────────────────┘
```

## Components Overview

### 1. PDF Extractor (`pdf_extractor.py`)
- **Purpose**: Parse PDF files and extract text
- **Technology**: pdfplumber
- **Input**: PDF file path
- **Output**: Raw text, tables, metadata
- **Error Handling**: Handles corrupted PDFs, password protection

### 2. Claim Extractor (`claim_extractor.py`)
- **Purpose**: Identify factual claims from text
- **AI Option**: OpenAI GPT-3.5/GPT-4
- **Fallback**: Regex-based extraction (no API needed)
- **Input**: Raw text
- **Output**: Structured claims with categories
  - statistic
  - date
  - financial
  - technical
  - other

### 3. Fact Verifier (`fact_verifier.py`)
- **Purpose**: Search web and verify claims
- **Technology**: DuckDuckGo Search API (free, no key needed)
- **Process**:
  1. Extract key entities from claim
  2. Build search query
  3. Get top 5 results
  4. Match evidence against claim
  5. Assign confidence score
- **Output**: Verification status & evidence

### 4. Streamlit App (`streamlit_app.py`)
- **Purpose**: User interface
- **Features**:
  - File upload (drag & drop)
  - Progress indicators
  - Results visualization
  - Export (JSON, CSV)
  - Settings panel

### 5. Advanced Verifier (`advanced_verifier.py`)
- **Purpose**: Multi-source verification
- **Sources**:
  - Wikipedia API
  - News sources
  - Local fact database
- **Usage**: Optional enhanced verification

## Data Flow

```
PDF File
   ↓
Extract Text
   ↓
Split into sentences
   ↓
AI: Identify claims
   ↓
Filter duplicates
   ↓
For each claim:
   ├─ Build search query
   ├─ Search web (DuckDuckGo)
   ├─ Extract key info
   ├─ Compare with claim
   └─ Assign status
   ↓
Generate Report
   ├─ Verified
   ├─ Unverified
   └─ No Evidence
   ↓
Export & Display
```

## Verification Logic

### Status Categories

1. **VERIFIED** (✅)
   - Multiple sources confirm claim
   - Confidence: > 0.75
   - Example: "Python created in 1991"

2. **UNVERIFIED** (⚠️)
   - Limited evidence or conflicting info
   - Confidence: 0.5 - 0.75
   - Example: Outdated statistics

3. **NO_EVIDENCE** (❌)
   - No relevant search results
   - Confidence: < 0.5
   - Example: "The Moon is 10,000 km away"

### Confidence Calculation

```python
confidence = (
    number_of_sources * 0.25 +  # More sources = higher confidence
    source_recency * 0.15 +      # Recent sources = higher confidence
    direct_quote * 0.10 +        # Direct quotes = higher confidence
    keyword_match * 0.25 +       # Strong keyword match = higher confidence
    entity_match * 0.25          # Named entity match = higher confidence
) / total_weights
```

## Deployment Architecture

```
┌──────────────────────────────────┐
│   Cloud Platform                 │
│ (Streamlit / Render / Vercel)   │
│                                  │
│  ┌──────────────────────────┐   │
│  │   Docker Container       │   │
│  │  ┌──────────────────┐    │   │
│  │  │ Python Runtime   │    │   │
│  │  ├──────────────────┤    │   │
│  │  │ Streamlit App    │    │   │
│  │  │ + Dependencies   │    │   │
│  │  └──────────────────┘    │   │
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │   Environment Variables  │   │
│  │  OPENAI_API_KEY         │   │
│  │  GOOGLE_API_KEY (opt)   │   │
│  └──────────────────────────┘   │
└──────────────────────────────────┘
         ↓                    ↑
    Internet ←──────────────→
         ↓                    ↑
┌──────────────────────────────────┐
│   External APIs                  │
│  - OpenAI (GPT-3.5/GPT-4)       │
│  - DuckDuckGo Search            │
│  - Wikipedia (optional)         │
│  - Google APIs (optional)       │
└──────────────────────────────────┘
```

## Performance Considerations

### Speed Optimization

1. **Caching**
   - Search results cached to avoid duplicate queries
   - Session state caches claims already extracted

2. **Rate Limiting**
   - 1 second delay between web searches
   - 2 seconds for API calls
   - Respects OpenAI rate limits

3. **Batch Processing**
   - Process up to 50 claims per document
   - Parallel-ready (can be enhanced)

### Scalability

- **Current**: Single-instance, suitable for < 100 concurrent users
- **Future**: Load balancing, Redis caching, database storage
- **Bottleneck**: OpenAI API token usage and cost

## Security Measures

1. **API Keys**
   - Stored in environment variables only
   - Never logged or exposed
   - Secrets managed by cloud provider

2. **File Handling**
   - PDFs processed in memory when possible
   - Temporary files deleted after use
   - No persistent file storage

3. **Input Validation**
   - PDF file type validation
   - Text length limits
   - Query sanitization

## Testing Strategy

### Unit Tests
- PDF extraction with various formats
- Claim extraction accuracy
- Verification logic
- Result formatting

### Integration Tests
- End-to-end PDF to report
- API connectivity
- Error handling

### Manual Testing
- Upload various PDFs
- Verify with known facts
- Check different claim types
- Test edge cases

## Future Enhancements

1. **Better Claim Extraction**
   - Custom ML model training
   - Multi-language support
   - Domain-specific extraction

2. **Enhanced Verification**
   - Academic paper integration
   - Citation parsing
   - Real-time data sources
   - Fact database subscription

3. **User Experience**
   - Batch processing
   - History storage
   - API for integrations
   - Mobile app

4. **Advanced Features**
   - Source attribution
   - Context awareness
   - Contradiction detection
   - Misinformation alerts

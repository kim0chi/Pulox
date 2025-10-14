# Pulox Architecture

Comprehensive system design documentation for the Pulox hybrid post-ASR correction and summarization system.

**Version:** 0.1.0
**Last Updated:** October 7, 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)
7. [Security](#security)
8. [Performance](#performance)
9. [Deployment](#deployment)
10. [Future Enhancements](#future-enhancements)

---

## System Overview

Pulox is a **three-tier desktop application** consisting of:
1. **Frontend (Electron)** - User interface and client logic
2. **Backend (FastAPI)** - REST API and ML inference
3. **Storage Layer** - File system for audio, transcripts, and models

### Architecture Pattern
- **Client-Server** - Electron frontend communicates with local Python backend via REST API
- **Microkernel** - Core transcription system with pluggable correction and summarization modules
- **Layered** - Clear separation between presentation, business logic, and data layers

---

## Architecture Diagram

### High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Electron Desktop Application                   │  │
│  │                                                              │  │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │  │ Upload  │  │Transcr  │  │Annotate  │  │Settings  │    │  │
│  │  │   &     │  │ ipts    │  │          │  │          │    │  │
│  │  │Transcr. │  │ Viewer  │  │  Editor  │  │  Panel   │    │  │
│  │  └─────────┘  └─────────┘  └──────────┘  └──────────┘    │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │            Renderer Process (renderer.js)            │  │  │
│  │  │  - UI Event Handling                                 │  │  │
│  │  │  - API Client Logic                                  │  │  │
│  │  │  - State Management                                  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                            ▲                                 │  │
│  │                            │ IPC (Context Bridge)            │  │
│  │                            ▼                                 │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │             Preload Script (preload.js)              │  │  │
│  │  │  - Security Bridge                                   │  │  │
│  │  │  - API Wrapper (window.puloxApi)                     │  │  │
│  │  │  - Electron Utilities (window.electron)              │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                            ▲                                 │  │
│  │                            │ Node.js API                     │  │
│  │                            ▼                                 │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │              Main Process (main.js)                  │  │  │
│  │  │  - Window Management                                 │  │  │
│  │  │  - Python Backend Lifecycle                          │  │  │
│  │  │  - IPC Handlers                                      │  │  │
│  │  │  - System Integration                                │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ HTTP REST API (127.0.0.1:8000)
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                     PYTHON BACKEND (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    API Layer (api.py)                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐ │  │
│  │  │ Upload   │  │Transcribe│  │Corrections│  │ Models   │ │  │
│  │  │Endpoints │  │Endpoints │  │ Endpoints │  │Management│ │  │
│  │  └──────────┘  └──────────┘  └───────────┘  └──────────┘ │  │
│  │                                                              │  │
│  │  - CORS Middleware                                          │  │
│  │  - Request Validation (Pydantic)                            │  │
│  │  - Error Handling                                           │  │
│  │  - Response Formatting                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  BUSINESS LOGIC LAYER                      │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │          ASR Module (src/asr/)                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────┐ │  │  │
│  │  │  │ WhisperASR                                      │ │  │  │
│  │  │  │  - Model Loading (GPU/CPU fallback)             │ │  │  │
│  │  │  │  - Audio Preprocessing                          │ │  │  │
│  │  │  │  - Transcription (with language detection)      │ │  │  │
│  │  │  │  - Segment Processing                           │ │  │  │
│  │  │  │  - Language Tagging                             │ │  │  │
│  │  │  └─────────────────────────────────────────────────┘ │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │     Correction Module (src/correction/) [Planned]   │  │  │
│  │  │  ┌─────────────────────────────────────────────────┐ │  │  │
│  │  │  │ ErrorCorrector                                  │ │  │  │
│  │  │  │  - Rule-based Corrections                       │ │  │  │
│  │  │  │  - MT5 Model Loading                            │ │  │  │
│  │  │  │  - Grammar Fixing                               │ │  │  │
│  │  │  │  - Text Normalization                           │ │  │  │
│  │  │  └─────────────────────────────────────────────────┘ │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Summarization Module (src/summarization/) [Planned] │  │  │
│  │  │  ┌─────────────────────────────────────────────────┐ │  │  │
│  │  │  │ Summarizer                                      │ │  │  │
│  │  │  │  - Extractive (TF-IDF, TextRank)                │ │  │  │
│  │  │  │  - Abstractive (MT5)                            │ │  │  │
│  │  │  │  - Hybrid Approach                              │ │  │  │
│  │  │  └─────────────────────────────────────────────────┘ │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │    Evaluation Module (src/evaluation/) [Planned]     │  │  │
│  │  │  ┌─────────────────────────────────────────────────┐ │  │  │
│  │  │  │ Metrics                                         │ │  │  │
│  │  │  │  - WER, CER, MER                                │ │  │  │
│  │  │  │  - ROUGE Scores                                 │ │  │  │
│  │  │  │  - BERTScore                                    │ │  │  │
│  │  │  └─────────────────────────────────────────────────┘ │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                     DATA ACCESS LAYER                      │  │
│  │                                                              │  │
│  │  - File I/O Operations                                      │  │
│  │  - Model Loading/Caching                                    │  │
│  │  - JSON Serialization                                       │  │
│  │  - Audio File Handling                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ File System I/O
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                        STORAGE LAYER                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      data/                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │  raw_audio/  │  │ transcripts/ │  │ corrections/ │     │  │
│  │  │              │  │              │  │              │     │  │
│  │  │ .wav, .mp3   │  │  .json       │  │  .json       │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌──────────────┐                        │  │
│  │  │  summaries/  │  │   samples/   │                        │  │
│  │  │              │  │              │                        │  │
│  │  │  .json       │  │ test files   │                        │  │
│  │  └──────────────┘  └──────────────┘                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      models/                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │     asr/     │  │ correction/  │  │summarization/│     │  │
│  │  │              │  │              │  │              │     │  │
│  │  │  whisper-*   │  │  mt5-small   │  │  mt5-small   │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend (Electron Application)

#### Main Process (`webapp/electron/main.js`)
**Responsibilities:**
- Application lifecycle management
- Window creation and management
- Python backend process spawning and monitoring
- IPC (Inter-Process Communication) handlers
- System integrations (file dialogs, notifications)

**Key Functions:**
```javascript
- startPythonBackend()  // Spawn Python server
- stopPythonBackend()   // Clean shutdown
- createMainWindow()    // Initialize UI window
- IPC handlers          // Bridge to renderer
```

**Process Flow:**
1. App starts → Check prerequisites
2. Spawn Python backend → Wait for health check
3. Create Electron window → Load HTML
4. Setup IPC communication
5. Show window when ready

#### Preload Script (`webapp/electron/preload.js`)
**Responsibilities:**
- Security bridge between main and renderer processes
- Expose safe APIs to renderer via `contextBridge`
- Abstract backend communication

**Exposed APIs:**
```javascript
window.electron {
  getApiUrl()           // Get backend URL
  openFileDialog()      // File picker
  showError()           // Error dialogs
  showMessage()         // Info dialogs
}

window.puloxApi {
  init()                // Initialize API client
  uploadAudio()         // Upload file
  transcribe()          // Start transcription
  getTranscripts()      // List transcripts
  getTranscript(id)     // Get specific transcript
  saveCorrection()      // Save annotation
  getCorrection(id)     // Get correction
  healthCheck()         // Backend status
}
```

#### Renderer Process (`webapp/electron/renderer/`)
**Responsibilities:**
- User interface rendering
- Event handling
- State management
- API communication via preload bridge

**Components:**
- **index.html** - DOM structure (300 lines)
- **styles.css** - Modern styling with gradients (500 lines)
- **renderer.js** - Application logic (400+ lines)

**State Management:**
```javascript
// Global State
- currentFile          // Selected audio file
- currentTranscriptId  // Active transcript
- transcripts[]        // Loaded transcripts list
```

**Key Functions:**
```javascript
- checkBackendConnection()  // Retry logic with 10 attempts
- handleFileSelect()        // Process uploaded file
- handleTranscribe()        // Trigger transcription
- openAnnotationEditor()    // Load annotation UI
- saveAnnotation()          // Save corrections
```

### 2. Backend (Python FastAPI)

#### API Layer (`webapp/api.py`)
**Responsibilities:**
- HTTP request handling
- Request validation (Pydantic models)
- Response formatting
- Error handling
- CORS middleware

**Endpoints:**

```python
# Upload & Storage
POST /upload              # Upload audio file
  - Accepts: WAV, MP3, M4A, FLAC, OGG, WEBM
  - Returns: {filename, path, size, timestamp}

# Transcription
POST /transcribe          # Transcribe audio
  - Body: {audio_filename, language?, model_size}
  - Returns: TranscriptionResponse
  - Process: Load audio → Whisper → Save transcript

# Transcripts Management
GET  /transcripts         # List all transcripts
  - Returns: {transcripts[], total}
  - Sorted by timestamp (newest first)

GET  /transcripts/{id}    # Get specific transcript
  - Returns: Full transcript data with segments

# Corrections Management
POST /corrections         # Save manual correction
  - Body: {transcript_id, original_text, corrected_text, metadata}
  - Returns: CorrectionResponse with change statistics

GET  /corrections/{id}    # Get correction
  - Returns: Correction data

GET  /corrections         # List all corrections
  - Returns: {corrections[], total}

# Audio Streaming
GET  /audio/{filename}    # Serve audio file
  - Returns: FileResponse (audio stream)

# System
GET  /health              # Health check
  - Returns: {status, timestamp, asr_model_loaded}

# WebSocket
WS   /ws/transcribe       # Real-time progress (partial)
  - Accepts: {action, filename, language, model_size}
  - Emits: Progress updates
```

**Data Models (Pydantic):**
```python
TranscriptionRequest {
  audio_filename: str
  language: str | None
  model_size: str = "base"
}

TranscriptionResponse {
  id: str
  text: str
  language: str
  duration: float
  segments: List[Dict]
  timestamp: str
}

CorrectionRequest {
  transcript_id: str
  original_text: str
  corrected_text: str
  metadata: Dict
}

CorrectionResponse {
  id: str
  transcript_id: str
  corrected_text: str
  changes: Dict
  timestamp: str
}
```

#### Business Logic Layer

**ASR Module (`src/asr/whisper_asr.py`)**
```python
class WhisperASR:
    def __init__(model_size, device):
        # Load Whisper model with GPU/CPU fallback
        # Test GPU functionality
        # Initialize device and model_size attributes

    def transcribe(audio_path, language, task, ...):
        # Load and preprocess audio
        # Run Whisper transcription
        # Process segments with language detection
        # Return structured result

    def transcribe_batch(audio_paths, output_dir, ...):
        # Process multiple files
        # Save results to JSON
        # Handle errors gracefully

    def _detect_segment_language(text):
        # Heuristic language detection
        # Returns: 'en', 'tl', or 'mixed'

    def _get_audio_duration(audio_path):
        # Calculate audio length using librosa

    def evaluate_wer(reference_path, hypothesis):
        # Calculate WER, CER, MER
        # Compare with ground truth
```

**Correction Module (Planned - `src/correction/`)**
```python
class ErrorCorrector:
    def __init__(model_name):
        # Load MT5-small model
        # Load rule-based corrections

    def correct(text, language):
        # Apply rule-based corrections
        # Run ML-based correction
        # Return corrected text + metadata

    def load_rules(rules_file):
        # Load error pattern rules

    def apply_rules(text):
        # Apply regex replacements
        # Handle common ASR errors
```

**Summarization Module (Planned - `src/summarization/`)**
```python
class Extractive Summarizer:
    def summarize(text, ratio):
        # TF-IDF sentence ranking
        # Extract top sentences
        # Return extractive summary

class AbstractiveSummarizer:
    def __init__(model_name):
        # Load MT5-small

    def summarize(text, max_length):
        # Generate abstractive summary
        # Handle bilingual content

class HybridSummarizer:
    def summarize(text, ratio, max_length):
        # Combine extractive + abstractive
        # Return hybrid summary
```

#### Data Access Layer
- File I/O operations for audio, transcripts, corrections
- JSON serialization/deserialization
- Model caching and lazy loading
- Path resolution and validation

### 3. Storage Layer

#### File System Structure
```
data/
├── raw_audio/           # Original uploaded files
│   ├── YYYYMMDD_HHMMSS_filename.wav
│   └── ...
├── transcripts/         # ASR outputs
│   ├── {id}_transcript.json
│   └── ...
├── corrections/         # Manual corrections
│   ├── {id}_corrected.json
│   └── ...
├── summaries/           # Generated summaries (future)
│   ├── {id}_summary.json
│   └── ...
└── samples/             # Test files
    └── test_tone.wav

models/
├── asr/                 # Whisper models (auto-downloaded)
│   └── (cached by Whisper library)
├── correction/          # Fine-tuned correction models (future)
│   └── mt5-filipino-en/
└── summarization/       # Fine-tuned summary models (future)
    └── mt5-summarizer/
```

#### File Formats

**Transcript JSON:**
```json
{
  "id": "20251007_143022_lecture",
  "audio_file": "20251007_143022_lecture.wav",
  "text": "Full transcript text...",
  "language": "tl",
  "duration": 3600.5,
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "Magandang umaga po sa inyong lahat.",
      "language": "tl"
    },
    ...
  ],
  "model": "base",
  "timestamp": "2025-10-07T14:30:45"
}
```

**Correction JSON:**
```json
{
  "id": "20251007_143022_lecture",
  "transcript_id": "20251007_143022_lecture",
  "timestamp": "2025-10-07T15:00:00",
  "original": "Original ASR text...",
  "corrected": "Corrected text...",
  "metadata": {
    "annotator": "John Doe",
    "subject": "Mathematics",
    "audio_quality": "Good",
    "primary_language": "Mixed (Equal)",
    "difficulty": "Moderate",
    "notes": "Some background noise"
  },
  "changes": {
    "word_changes": 15,
    "additions": 3,
    "deletions": 2,
    "similarity_ratio": 0.92
  }
}
```

---

## Data Flow

### Complete Transcription Flow

```
1. USER ACTION
   └─> User drags audio file into Electron app

2. FRONTEND (Renderer)
   ├─> handleFileSelect(file)
   ├─> Validate file type
   ├─> Display file info
   └─> User clicks "Start Transcription"

3. FRONTEND → BACKEND (Upload)
   ├─> FormData with audio file
   ├─> POST /upload
   └─> Response: {filename, path, size}

4. FRONTEND → BACKEND (Transcribe)
   ├─> POST /transcribe
   ├─> Body: {audio_filename, language, model_size}
   └─> Backend processes request

5. BACKEND PROCESSING
   ├─> API receives request
   ├─> Validate parameters (Pydantic)
   ├─> Load WhisperASR model (lazy load)
   ├─> Read audio file from disk
   ├─> whisper.transcribe(audio_path)
   │   ├─> Audio preprocessing (16kHz, pad/trim)
   │   ├─> Language detection (if auto)
   │   ├─> Mel-spectrogram generation
   │   └─> Beam search decoding
   ├─> Process segments
   │   ├─> Extract timestamps
   │   ├─> Detect segment language
   │   └─> Format output
   ├─> Save transcript to data/transcripts/
   └─> Return TranscriptionResponse

6. BACKEND → FRONTEND (Response)
   └─> JSON with full transcript

7. FRONTEND (Display)
   ├─> Show transcription complete
   ├─> Display transcript preview
   ├─> Update transcripts list
   └─> Enable "Annotate" button

8. USER ANNOTATION (Optional)
   ├─> User clicks "Annotate"
   ├─> Open annotation editor
   ├─> Side-by-side original/corrected
   ├─> User makes edits
   ├─> User clicks "Save Annotation"
   └─> POST /corrections

9. PERSISTENCE
   ├─> Correction saved to data/corrections/
   ├─> Transcript marked as annotated
   └─> Available for future model training
```

---

## Technology Stack

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Desktop Framework | Electron | 28.x | Cross-platform desktop app |
| UI Language | HTML5/CSS3/JavaScript | ES6+ | User interface |
| HTTP Client | Fetch API | Native | Backend communication |
| Build Tool | electron-builder | 24.x | Distribution packaging |
| Package Manager | npm | 9.x | Dependency management |

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Web Framework | FastAPI | 0.104+ | REST API |
| ASGI Server | Uvicorn | 0.24+ | HTTP server |
| ML Framework | PyTorch | 2.0+ | Deep learning |
| ASR Engine | OpenAI Whisper | Latest | Speech-to-text |
| NLP Library | Transformers | 4.36+ | MT5 models (future) |
| Audio Processing | librosa | 0.10+ | Audio analysis |
| Validation | Pydantic | 2.x | Request/response models |
| Package Manager | pip | Latest | Dependency management |

### ML Models

| Model | Size | Purpose | Status |
|-------|------|---------|--------|
| Whisper (tiny) | ~39M | Fast transcription | ✅ Available |
| Whisper (base) | ~74M | Balanced (recommended) | ✅ Available |
| Whisper (small) | ~244M | Higher accuracy | ✅ Available |
| Whisper (medium) | ~769M | Best accuracy | ✅ Available |
| MT5-small | ~300M | Correction & summarization | ⏳ Planned |
| Sentence-BERT | ~100M | Semantic similarity | ⏳ Planned |

---

## Design Decisions

### Why Electron + Python?

**Advantages:**
- ✅ Familiar web technologies for UI (HTML/CSS/JS)
- ✅ Python ecosystem for ML (PyTorch, Transformers)
- ✅ Desktop-native feel with offline capabilities
- ✅ Cross-platform potential (Windows/Mac/Linux)
- ✅ Easy to distribute (single installer)

**Alternatives Considered:**
- ❌ Web App Only - Requires internet, harder to install models locally
- ❌ Pure Python GUI (Tkinter/PyQt) - Less modern UI, steeper learning curve
- ❌ React Native - Good for mobile, overkill for desktop

### Why FastAPI over Flask?

**Advantages:**
- ✅ Async support (better for long-running ML tasks)
- ✅ Automatic API documentation (Swagger UI)
- ✅ Pydantic validation (type safety)
- ✅ Modern Python (type hints, async/await)
- ✅ WebSocket support (real-time progress)

### Why Local Processing over Cloud?

**Advantages:**
- ✅ No internet required (works offline)
- ✅ Data privacy (audio stays on device)
- ✅ No cloud costs
- ✅ Faster for short files
- ✅ Educational setting appropriate

**Disadvantages:**
- ❌ Slower on CPU-only machines
- ❌ Larger installation size
- ❌ Model updates require app update

### Why JSON Files over Database?

**Advantages:**
- ✅ Simple, no database setup
- ✅ Human-readable
- ✅ Easy to back up (just copy files)
- ✅ Version control friendly
- ✅ Sufficient for target scale (< 1000 files)

**When to Switch to Database:**
- If dataset grows > 1000 transcripts
- If need complex queries
- If multi-user collaboration required

---

## Security

### Electron Security

**Implemented:**
- ✅ `contextIsolation: true` - Isolate renderer from Node.js
- ✅ `nodeIntegration: false` - Disable Node in renderer
- ✅ Content Security Policy - Restrict resource loading
- ✅ Preload script - Safe API exposure
- ✅ No `eval()` or inline scripts

**Content Security Policy:**
```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self' http://127.0.0.1:8000;
               style-src 'self' 'unsafe-inline';
               script-src 'self' 'unsafe-inline';
               connect-src 'self' http://127.0.0.1:8000 ws://127.0.0.1:8000">
```

### API Security

**Implemented:**
- ✅ CORS restricted to localhost
- ✅ File upload validation (file type, size)
- ✅ Path traversal prevention
- ✅ Error messages don't leak sensitive info

**Future Enhancements:**
- ⏳ API authentication (if multi-user)
- ⏳ Rate limiting
- ⏳ Input sanitization
- ⏳ File size limits (currently unlimited)

### Data Privacy

**Current Approach:**
- ✅ All processing local (no cloud)
- ✅ No telemetry or analytics
- ✅ Audio files never leave device
- ✅ User has full control of data

**Compliance:**
- Data Protection Act (Philippines)
- GDPR-ready (if deployed in EU)
- Educational setting appropriate

---

## Performance

### Current Performance

| Metric | Tiny Model | Base Model | Small Model | Medium Model |
|--------|-----------|------------|-------------|--------------|
| Load Time | ~2s | ~3s | ~5s | ~10s |
| Transcription (1h audio, GPU) | ~5 min | ~8 min | ~15 min | ~30 min |
| Transcription (1h audio, CPU) | ~15 min | ~30 min | ~60 min | ~120 min |
| Memory Usage | ~1GB | ~1.5GB | ~3GB | ~6GB |
| Accuracy (estimated) | 75-80% | 85-90% | 90-93% | 92-95% |

### Optimization Strategies

**Model Loading:**
- ✅ Lazy loading (load only when needed)
- ✅ GPU/CPU fallback automatic
- ✅ Model caching (Whisper handles this)

**Processing:**
- ⏳ Batch processing for multiple files
- ⏳ Parallel processing (future)
- ⏳ Streaming for real-time (future)

**UI Responsiveness:**
- ✅ Async API calls
- ✅ Progress indicators
- ✅ Non-blocking UI during transcription

---

## Deployment

### Desktop Distribution

**Current Setup (electron-builder):**
```json
{
  "build": {
    "appId": "com.pulox.desktop",
    "win": {
      "target": ["nsis"],
      "icon": "assets/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true
    }
  }
}
```

**Build Process:**
```bash
cd webapp/electron
npm run build
# Output: dist/Pulox Setup 0.1.0.exe
```

**Challenges:**
- Python runtime must be installed separately
- Models downloaded on first run (~75-300MB)
- Large installer size (~500MB with bundled Python)

**Future: Standalone Distribution**
1. Use PyInstaller to compile Python backend
2. Bundle compiled backend with Electron
3. Include small models in installer
4. Download large models on demand

### Cloud Deployment (Optional)

**Architecture for Cloud:**
```
User → Electron App → Cloud API (FastAPI)
                    ↓
             ML Inference Service
                    ↓
              GPU Instance (P3/T4)
```

**Benefits:**
- Faster transcription (GPU always available)
- Smaller app size (models on server)
- Centralized updates

**Drawbacks:**
- Requires internet
- Monthly cloud costs
- Privacy concerns (audio uploaded)

---

## Future Enhancements

### Phase 1: Core ML (Next 2 Months)
1. Correction module integration
2. Summarization module integration
3. Model training pipeline

### Phase 2: UX Improvements (Months 3-4)
1. Real-time transcription
2. Speaker diarization
3. Search within transcripts
4. Export to PDF/DOCX
5. Audio playback sync with transcript

### Phase 3: Collaboration (Months 5-6)
1. Cloud sync (optional)
2. Multi-user annotation
3. Annotation version history
4. Team analytics

### Phase 4: Advanced Features (Long Term)
1. Translation (English ↔ Tagalog)
2. Question generation from lectures
3. Quiz creation
4. LMS integration (Moodle)
5. Mobile app (view-only)
6. Voice commands

---

## Diagrams

### Sequence Diagram: Transcription

```
User        Electron      Main       Preload    Renderer    API        Whisper
 |            |             |           |          |         |           |
 |--upload--->|             |           |          |         |           |
 |            |--select---->|           |          |         |           |
 |            |             |--IPC----->|          |         |           |
 |            |             |           |--upload->|         |           |
 |            |             |           |          |--POST-->|           |
 |            |             |           |          |         |--load---->|
 |            |             |           |          |         |           |
 |            |             |           |          |         |<-model----|
 |            |             |           |          |         |           |
 |            |             |           |          |         |--transcr->|
 |            |             |           |          |         |           |
 |            |             |           |          |         |<-result---|
 |            |             |           |          |<-JSON---|           |
 |            |             |           |<-result--|         |           |
 |            |             |<--IPC-----|          |         |           |
 |<--display--|             |           |          |         |           |
```

---

## Glossary

- **ASR** - Automatic Speech Recognition
- **WER** - Word Error Rate (lower is better)
- **CER** - Character Error Rate
- **ROUGE** - Recall-Oriented Understudy for Gisting Evaluation
- **BERTScore** - Semantic similarity using BERT embeddings
- **MT5** - Multilingual T5 (Text-to-Text Transfer Transformer)
- **IPC** - Inter-Process Communication (Electron main ↔ renderer)
- **CSP** - Content Security Policy
- **CORS** - Cross-Origin Resource Sharing

---

## References

- [Electron Documentation](https://www.electronjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)

---

**Maintained by:** [Your Name]
**Last Updated:** October 7, 2025
**Version:** 0.1.0

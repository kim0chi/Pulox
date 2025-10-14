"""
FastAPI Backend for Pulox Electron App
Provides REST API endpoints for ASR, correction, and summarization
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from asr.whisper_asr import WhisperASR
from correction.error_corrector import ErrorCorrector
from correction.models import CorrectionConfig, CorrectionLevel

# Initialize FastAPI app
app = FastAPI(
    title="Pulox API",
    description="Backend API for Pulox ASR and Annotation System",
    version="0.1.0"
)

# Configure CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global ASR model instance (lazy loaded)
asr_model: Optional[WhisperASR] = None

# Global error corrector instance (lazy loaded)
error_corrector: Optional[ErrorCorrector] = None

# Data directories
DATA_DIR = Path("data")
AUDIO_DIR = DATA_DIR / "raw_audio"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
CORRECTIONS_DIR = DATA_DIR / "corrections"

# Ensure directories exist
for dir_path in [AUDIO_DIR, TRANSCRIPTS_DIR, CORRECTIONS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Pydantic Models
# ============================================================================

class TranscriptionRequest(BaseModel):
    """Request model for transcription"""
    audio_filename: str
    language: Optional[str] = None  # 'en', 'tl', or None for auto-detect
    model_size: str = "base"


class TranscriptionResponse(BaseModel):
    """Response model for transcription"""
    id: str
    text: str
    language: str
    duration: float
    segments: List[Dict]
    timestamp: str


class CorrectionRequest(BaseModel):
    """Request model for saving corrections"""
    transcript_id: str
    original_text: str
    corrected_text: str
    metadata: Dict


class CorrectionResponse(BaseModel):
    """Response model for corrections"""
    id: str
    transcript_id: str
    corrected_text: str
    changes: Dict
    timestamp: str


class AnnotationMetadata(BaseModel):
    """Metadata for annotations"""
    annotator: str
    subject: Optional[str] = None
    audio_quality: Optional[str] = None
    primary_language: Optional[str] = None
    difficulty: Optional[str] = None
    notes: Optional[str] = None


class AutoCorrectionRequest(BaseModel):
    """Request model for automatic correction"""
    text: str
    language: Optional[str] = None  # 'en', 'tl', or None for auto-detect
    level: str = "standard"  # 'light', 'standard', or 'aggressive'
    use_ml: bool = False  # Enable ML-based correction (requires model download)


class AutoCorrectionResponse(BaseModel):
    """Response model for automatic correction"""
    original_text: str
    corrected_text: str
    changes: List[Dict]
    confidence_score: float
    method: str
    language: str
    processing_time: float
    summary: Dict


# ============================================================================
# Helper Functions
# ============================================================================

def get_asr_model(model_size: str = "base") -> WhisperASR:
    """Get or initialize ASR model (lazy loading)"""
    global asr_model
    if asr_model is None:
        asr_model = WhisperASR(model_size=model_size)
    return asr_model


def get_error_corrector(use_ml: bool = False) -> ErrorCorrector:
    """Get or initialize error corrector (lazy loading)"""
    global error_corrector
    if error_corrector is None:
        error_corrector = ErrorCorrector(use_ml=use_ml)
    return error_corrector


def calculate_changes(original: str, corrected: str) -> Dict:
    """Calculate statistics about changes made"""
    import difflib

    orig_words = original.split()
    corr_words = corrected.split()

    matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
    changes = {
        'word_changes': 0,
        'additions': 0,
        'deletions': 0,
        'similarity_ratio': matcher.ratio()
    }

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            changes['word_changes'] += max(i2 - i1, j2 - j1)
        elif tag == 'delete':
            changes['deletions'] += i2 - i1
        elif tag == 'insert':
            changes['additions'] += j2 - j1

    return changes


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "Pulox API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "transcribe": "/transcribe",
            "correct": "/correct",
            "annotations": "/annotations",
            "corrections": "/corrections"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "asr_model_loaded": asr_model is not None
    }


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload audio file for transcription

    Accepts: .wav, .mp3, .m4a, .flac, .ogg
    """
    # Validate file type
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = AUDIO_DIR / filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        return {
            "status": "success",
            "filename": filename,
            "path": str(file_path),
            "size": len(content),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe uploaded audio file

    - **audio_filename**: Name of uploaded audio file
    - **language**: Optional language hint ('en', 'tl', or None)
    - **model_size**: Whisper model size (tiny, base, small, medium, large)
    """
    audio_path = AUDIO_DIR / request.audio_filename

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    try:
        # Get ASR model
        asr = get_asr_model(request.model_size)

        # Transcribe
        result = asr.transcribe(
            str(audio_path),
            language=request.language
        )

        # Generate transcript ID
        transcript_id = Path(request.audio_filename).stem

        # Convert segments to serializable format
        segments = []
        for seg in result.get("segments", []):
            if hasattr(seg, '__dict__'):
                segments.append({
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                    "language": getattr(seg, 'language', None)
                })
            else:
                segments.append(seg)

        # Save transcript
        transcript_data = {
            "id": transcript_id,
            "audio_file": request.audio_filename,
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "duration": result.get("duration", 0),
            "segments": segments,
            "model": request.model_size,
            "timestamp": datetime.now().isoformat()
        }

        transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}_transcript.json"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        return TranscriptionResponse(**transcript_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.get("/transcripts")
async def list_transcripts():
    """List all available transcripts"""
    transcripts = []

    for file_path in TRANSCRIPTS_DIR.glob("*_transcript.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                transcripts.append({
                    "id": data.get("id"),
                    "audio_file": data.get("audio_file"),
                    "language": data.get("language"),
                    "duration": data.get("duration"),
                    "timestamp": data.get("timestamp"),
                    "has_correction": (CORRECTIONS_DIR / f"{data.get('id')}_corrected.json").exists()
                })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

    # Sort by timestamp (newest first)
    transcripts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return {"transcripts": transcripts, "total": len(transcripts)}


@app.get("/transcripts/{transcript_id}")
async def get_transcript(transcript_id: str):
    """Get specific transcript by ID"""
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}_transcript.json"

    if not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Transcript not found")

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load transcript: {str(e)}")


@app.post("/corrections", response_model=CorrectionResponse)
async def save_correction(request: CorrectionRequest):
    """
    Save corrected transcript

    - **transcript_id**: ID of original transcript
    - **original_text**: Original ASR text
    - **corrected_text**: Corrected text
    - **metadata**: Annotation metadata
    """
    correction_id = request.transcript_id

    # Calculate changes
    changes = calculate_changes(request.original_text, request.corrected_text)

    # Create correction data
    correction_data = {
        "id": correction_id,
        "transcript_id": request.transcript_id,
        "timestamp": datetime.now().isoformat(),
        "original": request.original_text,
        "corrected": request.corrected_text,
        "metadata": request.metadata,
        "changes": changes
    }

    # Save correction
    correction_path = CORRECTIONS_DIR / f"{correction_id}_corrected.json"
    with open(correction_path, 'w', encoding='utf-8') as f:
        json.dump(correction_data, f, ensure_ascii=False, indent=2)

    return CorrectionResponse(
        id=correction_id,
        transcript_id=request.transcript_id,
        corrected_text=request.corrected_text,
        changes=changes,
        timestamp=correction_data["timestamp"]
    )


@app.get("/corrections/{transcript_id}")
async def get_correction(transcript_id: str):
    """Get correction for specific transcript"""
    correction_path = CORRECTIONS_DIR / f"{transcript_id}_corrected.json"

    if not correction_path.exists():
        raise HTTPException(status_code=404, detail="Correction not found")

    try:
        with open(correction_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load correction: {str(e)}")


@app.get("/corrections")
async def list_corrections():
    """List all corrections"""
    corrections = []

    for file_path in CORRECTIONS_DIR.glob("*_corrected.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                corrections.append({
                    "id": data.get("id"),
                    "transcript_id": data.get("transcript_id"),
                    "timestamp": data.get("timestamp"),
                    "annotator": data.get("metadata", {}).get("annotator"),
                    "changes": data.get("changes", {}).get("word_changes", 0)
                })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

    corrections.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return {"corrections": corrections, "total": len(corrections)}


@app.post("/correct", response_model=AutoCorrectionResponse)
async def auto_correct_text(request: AutoCorrectionRequest):
    """
    Automatically correct text using rule-based and/or ML-based methods

    - **text**: Text to correct
    - **language**: Optional language hint ('en', 'tl', or None)
    - **level**: Correction level ('light', 'standard', 'aggressive')
    - **use_ml**: Enable ML-based correction (requires MT5 model download)
    """
    try:
        # Get error corrector
        corrector = get_error_corrector(use_ml=request.use_ml)

        # Parse correction level
        level_map = {
            'light': CorrectionLevel.LIGHT,
            'standard': CorrectionLevel.STANDARD,
            'aggressive': CorrectionLevel.AGGRESSIVE
        }
        level = level_map.get(request.level, CorrectionLevel.STANDARD)

        # Create config
        config = CorrectionConfig(
            level=level,
            use_rules=True,
            use_ml=request.use_ml,
            language_hint=request.language
        )

        # Perform correction
        result = corrector.correct(request.text, config)

        # Convert to response format
        return AutoCorrectionResponse(
            original_text=result.original_text,
            corrected_text=result.corrected_text,
            changes=[
                {
                    "original": c.original,
                    "corrected": c.corrected,
                    "error_type": c.error_type.value,
                    "confidence": c.confidence,
                    "description": c.description
                }
                for c in result.changes
            ],
            confidence_score=result.confidence_score,
            method=result.method,
            language=result.language,
            processing_time=result.processing_time,
            summary=result.get_changes_summary()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction failed: {str(e)}")


@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve audio file for playback"""
    audio_path = AUDIO_DIR / filename

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(audio_path)


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for real-time transcription progress

    Accepts JSON messages with format:
    {"action": "transcribe", "filename": "audio.wav", "language": "tl"}
    """
    await websocket.accept()

    try:
        while True:
            # Receive transcription request
            data = await websocket.receive_json()

            if data.get("action") == "transcribe":
                filename = data.get("filename")
                language = data.get("language")
                model_size = data.get("model_size", "base")

                audio_path = AUDIO_DIR / filename

                if not audio_path.exists():
                    await websocket.send_json({
                        "status": "error",
                        "message": "Audio file not found"
                    })
                    continue

                # Send progress updates
                await websocket.send_json({
                    "status": "loading",
                    "message": "Loading ASR model..."
                })

                asr = get_asr_model(model_size)

                await websocket.send_json({
                    "status": "transcribing",
                    "message": "Transcribing audio..."
                })

                # Transcribe (in future, can add progress callbacks)
                result = asr.transcribe(str(audio_path), language=language)

                # Send completion
                await websocket.send_json({
                    "status": "complete",
                    "message": "Transcription complete",
                    "result": {
                        "text": result["text"],
                        "language": result.get("language"),
                        "duration": result.get("duration")
                    }
                })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })


# ============================================================================
# Server Configuration
# ============================================================================

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the FastAPI server"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    print("="*60)
    print("Starting Pulox API Server")
    print("="*60)
    print(f"API Documentation: http://127.0.0.1:8000/docs")
    print(f"Alternative Docs: http://127.0.0.1:8000/redoc")
    print("="*60)

    start_server()

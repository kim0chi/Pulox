# Changelog

All notable changes to the Pulox project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### To Be Added
- Automatic error correction module
- Automatic summarization module
- Model training pipeline
- Comprehensive test suite
- Production deployment

---

## [0.1.0] - 2025-10-07

### Added - Core Infrastructure

#### ASR Module
- Initial Whisper ASR integration (`src/asr/whisper_asr.py`)
- Support for multiple Whisper model sizes (tiny, base, small, medium)
- Auto-language detection for English and Tagalog
- Segment-level language tagging
- GPU/CPU fallback support
- Batch transcription capability
- WER evaluation stub

#### Backend API
- FastAPI REST API (`webapp/api.py`)
- Endpoints:
  - `POST /upload` - Upload audio files
  - `POST /transcribe` - Transcribe audio with Whisper
  - `GET /transcripts` - List all transcripts
  - `GET /transcripts/{id}` - Get specific transcript
  - `POST /corrections` - Save manual corrections
  - `GET /corrections/{id}` - Get correction data
  - `GET /corrections` - List all corrections
  - `GET /audio/{filename}` - Stream audio files
  - `WebSocket /ws/transcribe` - Real-time progress (partial)
  - `GET /health` - Health check endpoint
- CORS middleware for Electron frontend
- File upload handling with validation
- JSON response formatting
- Error handling and logging

#### Desktop Application (Electron)
- Complete Electron desktop app (`webapp/electron/`)
- Main process with Python backend auto-start
- Security-hardened preload script
- Modern UI with 4 main tabs:
  - Upload & Transcribe - Drag & drop interface
  - Transcripts - Browse all transcriptions
  - Annotations - Side-by-side editor
  - Settings - Configuration panel
- Features:
  - Drag & drop file upload
  - Progress tracking with visual feedback
  - Connection status monitoring with retry logic
  - Model selection (tiny/base/small/medium)
  - Language selection (auto/English/Tagalog)
  - Metadata management (annotator, subject, quality)
  - Real-time change tracking in annotations
  - Audio playback support
- Responsive design with professional styling
- DevTools integration for development

#### Annotation Tools
- Streamlit-based annotation UI (`src/utils/annotation_tool.py`)
- Side-by-side original/corrected transcript view
- Language detection helpers
- Diff visualization
- Metadata tracking
- Export to CSV functionality
- Inter-annotator agreement tracking (planned)

#### Project Structure
- Created complete directory structure:
  - `src/{asr,correction,summarization,evaluation,utils}/`
  - `data/{raw_audio,transcripts,corrections,summaries}/`
  - `models/{asr,correction,summarization}/`
  - `webapp/electron/`
  - `tests/`, `notebooks/`, `configs/`, `docs/`
- Python package structure with `__init__.py` files
- Git-friendly with `.gitkeep` in empty dirs

#### Installation & Setup
- Windows batch installers:
  - `install_electron_deps.bat` - One-click dependency installer
  - `run_electron_dev.bat` - Quick launcher
- Python requirements:
  - `requirements.txt` - Full dependencies
  - `requirements-electron.txt` - Minimal for desktop app
- Node.js `package.json` with electron-builder config
- Comprehensive installation guide (`INSTALLATION_GUIDE.md`)
- Electron setup guide (`ELECTRON_SETUP.md`)

#### Documentation
- Data collection plan (`docs/data_collection_plan.md`)
  - UCLM High School data collection strategy
  - Target: 20-40 hours of classroom recordings
  - 5-phase collection and annotation plan
  - Recording protocols and quality guidelines
  - Metadata schema and file structure
- Project status tracker (`PROJECT_STATUS.md`)
- Comprehensive README (`README.md`)
- Installation troubleshooting guide
- API documentation in code comments

### Changed

#### Bug Fixes
- Fixed character encoding issues in `whisper_asr.py`
  - Removed problematic Unicode punctuation marks
  - Fixed Windows console encoding errors
- Updated Whisper API usage to modern `model.transcribe()` method
- Added missing `model_size` attribute in WhisperASR class
- Fixed Content Security Policy blocking API requests in Electron
- Added retry logic for backend connection (10 attempts with 500ms delay)

#### Optimizations
- Lazy loading of Whisper models
- Efficient file handling in API
- Compressed frontend assets
- Minimal Python dependencies for faster installation

### Infrastructure

#### Development Tools
- Python virtual environment support
- Git repository initialization
- EditorConfig for consistent formatting
- Development mode with auto-reload

#### Dependencies
- Python: whisper, torch, torchaudio, fastapi, uvicorn, librosa, soundfile
- Node.js: electron, axios, electron-builder

---

## [0.0.1] - 2025-10-01

### Added
- Initial project setup
- Basic directory structure
- Requirements file
- Test Whisper integration

---

## Version History

- **0.1.0** (2025-10-07) - Alpha release with transcription and desktop app
- **0.0.1** (2025-10-01) - Initial project setup

---

## Upcoming in 0.2.0

### Planned Features
- [ ] Correction module with MT5-small
- [ ] Rule-based error correction
- [ ] Summarization module (extractive + abstractive)
- [ ] Training pipeline for correction model
- [ ] Training pipeline for summarization model
- [ ] API endpoints for correction and summarization
- [ ] UI integration for correction and summarization
- [ ] Configuration system (YAML files)
- [ ] Evaluation metrics implementation

### Planned Improvements
- [ ] Comprehensive test suite (target 80%+ coverage)
- [ ] Jupyter notebooks for training
- [ ] Docker containerization
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Performance optimizations
- [ ] Better error handling
- [ ] Logging improvements

### Planned Documentation
- [ ] Architecture documentation
- [ ] API reference guide
- [ ] Training guide
- [ ] Deployment guide
- [ ] Contributing guidelines

---

## Notes

### Breaking Changes
- None yet (first release)

### Deprecations
- None yet

### Security
- No known security issues
- Content Security Policy implemented in Electron
- Context isolation enabled
- Node integration disabled in renderer

### Known Issues
1. WebSocket real-time progress incomplete
2. Electron build untested on clean Windows
3. No automated tests yet
4. Correction and summarization modules not implemented
5. No training data collected yet

---

## Contributors

- [Your Name] - Project Lead & Primary Developer

---

## Links

- [Project Status](PROJECT_STATUS.md)
- [Roadmap](ROADMAP.md)
- [Installation Guide](INSTALLATION_GUIDE.md)
- [Electron Setup](ELECTRON_SETUP.md)

---

**Legend:**
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

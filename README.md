# Pulox

**Hybrid Post-ASR Correction & Summarization System for English-Tagalog Classroom Lectures**

[![Status](https://img.shields.io/badge/status-alpha-yellow)](docs/project/status.md)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](docs/project/changelog.md)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)](docs/setup/installation.md)

## Overview

Pulox is an intelligent desktop application that automatically transcribes, corrects, and summarizes classroom lectures delivered in mixed English and Tagalog (Filipino). Designed specifically for Philippine educational settings where code-switching is common.

### Key Features

- ðŸŽ™ï¸ **Automatic Transcription** - OpenAI Whisper for accurate speech-to-text
- âœï¸ **Error Correction** - Post-ASR grammar and spelling correction (in development)
- ðŸ“ **Summarization** - Automatic lecture summary generation (in development)
- ðŸŒ **Bilingual Support** - Handles English, Tagalog, and code-switched content
- ðŸ’» **Desktop App** - Modern Electron-based interface
- ðŸ”§ **Annotation Tools** - Manual correction and quality improvement

---

## Quick Start

### Prerequisites

- Python 3.8+ â€” [Download](https://www.python.org/downloads/)
- Node.js 16+ â€” [Download](https://nodejs.org/)
- FFmpeg â€” [Installation Guide](docs/setup/installation.md#issue-5-ffmpeg-not-found)

### Installation

1. Clone or download the project

   ```bash
   cd Pulox
   ```

2. Run the installer

   ```bash
   scripts/install_electron_deps.bat
   ```

3. Start the application

   ```bash
   scripts/run_electron_dev.bat
   ```

> ðŸ“– For detailed instructions, see the [Installation Guide](docs/setup/installation.md).

---

## Usage

### Transcribing Audio

1. Launch Pulox and click **Upload & Transcribe**
2. Drag and drop an audio file (WAV, MP3, M4A, etc.)
3. Select language and model size
4. Click **Start Transcription**

### Viewing & Annotating

- Browse transcripts in the **Transcripts** tab
- Click **View** to see the full transcript
- Click **Annotate** to make corrections and add metadata

### Exporting Data

- Transcripts: `data/transcripts/`
- Corrections: `data/corrections/`
- Access via file system or API

---

## Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   Electron Desktop App          â”‚
â”‚                                 â”‚
â”‚  â€¢ Upload Interface             â”‚
â”‚  â€¢ Transcript Viewer            â”‚
â”‚  â€¢ Annotation Editor            â”‚
â”‚  â€¢ Settings Panel               â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
             â”‚ HTTP REST API
             â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   FastAPI Backend (Python)      â”‚
â”‚                                 â”‚
â”‚  â€¢ ASR Module (Whisper)         â”‚
â”‚  â€¢ Correction Module (MT5)      â”‚
â”‚  â€¢ Summarization (MT5)          â”‚
â”‚  â€¢ Evaluation Metrics           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

> 📖 For detailed roadmap, see [Roadmap](docs/project/roadmap.md).

---

## Documentation

- **[Installation Guide](docs/setup/installation.md)** — Setup instructions
- **[Electron Setup](docs/setup/electron-setup.md)** — Desktop app guide
- **[Project Status](docs/project/status.md)** — Current progress tracker
- **[Roadmap](docs/project/roadmap.md)** — Future plans
- **[Changelog](docs/project/changelog.md)** — Version history
- **[Architecture](docs/project/architecture.md)** — System design
- **[Data Collection Plan](docs/project/data-collection-plan.md)** — Dataset planning

---

## Development

### Setup Development Environment

```bash
# Install Python dependencies
pip install -r requirements-electron.txt

# Install Node.js dependencies
cd webapp/electron
npm install

# Run in development mode
npm run dev
```

### Running Tests

```bash
# Run Python tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Building for Distribution

```bash
# Build Windows installer
cd webapp/electron
npm run build
```

Output: `dist/Pulox Setup 0.1.0.exe`

---

## API Reference

### Transcription Endpoints

```http
POST /upload            # Upload audio file
POST /transcribe        # Start transcription
GET  /transcripts       # List all transcripts
GET  /transcripts/{id}  # Get specific transcript
GET  /audio/{filename}  # Download audio file
```

### Annotation Endpoints

```http
POST /corrections       # Save correction
GET  /corrections/{id}  # Get specific correction
GET  /corrections       # List all corrections
```

### Future Endpoints (Planned)

```http
POST /correct           # Auto-correct transcript
POST /summarize         # Generate summary
POST /batch/transcribe  # Batch processing
```

---

## Contributing

We welcome contributions! Areas where help is needed:

- 🤖 **ML Development** — Correction and summarization modules
- 🎙️ **Data Collection** — Recording classroom lectures
- ✏️ **Data Annotation** — Transcription correction
- 🧪 **Testing** — Write tests and find bugs
- 📚 **Documentation** — Improve docs and guides

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **OpenAI Whisper** — State-of-the-art ASR
- **Hugging Face** — Transformers library
- **FastAPI** — Modern Python web framework
- **Electron** — Cross-platform desktop apps

---

## FAQ

**Q: Does this work on macOS or Linux?**  
A: The backend works on all platforms. The Electron app should work but is untested. Currently optimized for Windows.

**Q: Can I use models other than Whisper?**  
A: Yes, you can modify `src/asr/whisper_asr.py` to use other ASR systems.

**Q: How accurate is the transcription?**  
A: Depends on audio quality and language mix. Expect 80-90% accuracy with Whisper base model.

**Q: Do I need a GPU?**  
A: No, but GPU significantly speeds up transcription. The app works on CPU-only systems.

**Q: Can I use this for other languages?**  
A: Whisper supports 90+ languages. You'd need to modify the correction and summarization modules for other language pairs.

**Q: Is this production-ready?**  
A: No, this is alpha software. Transcription works well, but correction and summarization are still in development.

---

**Status:** Alpha • **Version:** 0.1.0 • **Last Updated:** October 2025


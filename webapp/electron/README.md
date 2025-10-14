# Pulox Desktop Application

Desktop application for Pulox - English-Tagalog lecture transcription and annotation system.

## Architecture

```
┌─────────────────────┐
│  Electron Frontend  │  (This app)
│  - Upload UI        │
│  - Transcripts      │
│  - Annotation Tool  │
└──────────┬──────────┘
           │ HTTP API
┌──────────▼──────────┐
│  Python Backend     │  (FastAPI)
│  - Whisper ASR      │
│  - File Management  │
│  - Data Storage     │
└─────────────────────┘
```

## Prerequisites

- **Node.js** (v16 or higher)
- **Python** (3.8 or higher)
- **FFmpeg** (for audio processing)

## Setup

### 1. Install Python Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

From this directory (`webapp/electron/`):

```bash
npm install
```

## Running the App

### Development Mode

```bash
npm run dev
```

This will:
1. Start the Python FastAPI backend (port 8000)
2. Launch Electron with DevTools open
3. Auto-reload on changes

### Production Mode

```bash
npm start
```

Runs without DevTools.

## Building Distributable

### Build for Windows

```bash
npm run build
```

This creates:
- Installer: `dist/Pulox Setup 0.1.0.exe`
- Portable: `dist/win-unpacked/`

### Build Directory Only (Testing)

```bash
npm run build:dir
```

Creates unpacked directory without installer (faster for testing).

## Project Structure

```
electron/
├── main.js              # Main process (Electron)
├── preload.js           # Security bridge
├── package.json         # Node dependencies & build config
├── renderer/            # Frontend UI
│   ├── index.html       # Main HTML
│   ├── styles.css       # Styling
│   └── renderer.js      # Frontend logic
└── assets/              # Icons and images
    └── icon.png         # App icon
```

## Features

### 1. Upload & Transcribe
- Drag & drop or click to upload audio files
- Supported formats: WAV, MP3, M4A, FLAC, OGG, WEBM
- Choose language (auto-detect, English, Tagalog)
- Select Whisper model size (tiny to medium)
- Real-time progress tracking

### 2. Transcripts Management
- View all transcribed audio files
- See annotation status
- Quick access to view/annotate

### 3. Annotation Editor
- Side-by-side original and corrected text
- Metadata fields (annotator, subject, quality, etc.)
- Notes section for observations
- Change tracking and statistics

### 4. Settings
- Default model selection
- Backend connection status
- About information

## API Endpoints

The Python backend provides:

- `POST /upload` - Upload audio file
- `POST /transcribe` - Transcribe uploaded audio
- `GET /transcripts` - List all transcripts
- `GET /transcripts/{id}` - Get specific transcript
- `POST /corrections` - Save annotation
- `GET /corrections/{id}` - Get correction
- `GET /audio/{filename}` - Stream audio file
- `WebSocket /ws/transcribe` - Real-time transcription

## Troubleshooting

### Backend won't start

1. Check Python is installed: `python --version`
2. Check dependencies: `pip install -r ../../requirements.txt`
3. Manually test backend: `python ../api.py`

### "Module not found" errors

Install missing Python packages:
```bash
pip install fastapi uvicorn python-multipart
```

### FFmpeg not found

Windows (Chocolatey):
```bash
choco install ffmpeg
```

Or download from: https://ffmpeg.org/download.html

### Build fails

1. Delete `node_modules/` and reinstall: `npm install`
2. Check Node.js version: `node --version` (should be v16+)
3. Try building without ASAR: `npm run build -- --config.asar=false`

## Development Tips

### Debugging

1. Open DevTools: `npm run dev`
2. View Python logs in terminal
3. Check Network tab for API calls
4. Use `window.puloxDebug` in console

### Modifying UI

1. Edit `renderer/index.html` for structure
2. Edit `renderer/styles.css` for styling
3. Edit `renderer/renderer.js` for logic
4. Refresh app to see changes (Ctrl+R)

### Adding API Endpoints

1. Add endpoint in `../api.py`
2. Add method in `preload.js` under `window.puloxApi`
3. Call from `renderer.js`

## Packaging for Distribution

The app bundles:
- Electron runtime
- Node.js dependencies
- Frontend assets

Python backend must be installed separately or bundled with PyInstaller (future enhancement).

### Future: Standalone Executable

To create fully standalone app:

1. Use PyInstaller to compile Python code:
   ```bash
   pyinstaller --onefile ../api.py
   ```

2. Update `package.json` build config to include:
   ```json
   "extraResources": ["python-dist/"]
   ```

3. Modify `main.js` to use bundled Python executable

## License

MIT

## Support

For issues, check:
- Python backend logs
- Electron DevTools console
- Network requests in DevTools

Common issues: https://github.com/[your-repo]/pulox/issues

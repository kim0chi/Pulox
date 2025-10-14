# Pulox Electron Desktop App - Setup Guide

This guide will help you get the Pulox desktop application running.

## Quick Start

### Step 1: Install Python Dependencies

From the project root directory:

```bash
pip install -r requirements.txt
```

### Step 2: Install Node.js Dependencies

Navigate to the Electron app directory and install:

```bash
cd webapp/electron
npm install
```

### Step 3: Run the Application

```bash
npm run dev
```

The app will:
1. Start the Python backend server on http://127.0.0.1:8000
2. Launch the Electron desktop window
3. Open with DevTools for debugging

## What You'll See

### Main Interface

1. **Upload & Transcribe Tab**
   - Drag & drop audio files or click to select
   - Choose language (Auto, English, Tagalog)
   - Select Whisper model size (tiny, base, small, medium)
   - Start transcription and view progress
   - See results with transcript preview

2. **Transcripts Tab**
   - View all previously transcribed audio
   - See which transcripts have been annotated
   - Quick access to view or annotate

3. **Annotations Tab**
   - Edit transcripts side-by-side (original vs corrected)
   - Add metadata (annotator name, subject, quality, etc.)
   - Save corrections with change tracking

4. **Settings Tab**
   - Configure default model size
   - Check backend connection status
   - View API information

## Testing the App

### Test 1: Upload & Transcribe

1. Run the app: `npm run dev`
2. Go to "Upload & Transcribe" tab
3. Click "Select File" or drag an audio file
4. Choose language and model (use "tiny" for faster testing)
5. Click "Start Transcription"
6. Wait for completion (progress bar will show status)
7. View the transcript result

### Test 2: View Transcripts

1. Go to "Transcripts" tab
2. You should see your transcribed file
3. Click "View" to see the full transcript
4. Click "Annotate" to open the annotation editor

### Test 3: Annotate Transcript

1. From Transcripts tab, click "Annotate" on any transcript
2. App switches to "Annotations" tab
3. Original transcript appears on the left (read-only)
4. Edit the corrected version on the right
5. Fill in metadata (your name, subject, etc.)
6. Click "Save Annotation"
7. See confirmation with change statistics

## Architecture Overview

```
┌────────────────────────────────┐
│   Electron Desktop App         │
│   (Node.js + HTML/CSS/JS)      │
│                                │
│   ┌─────────────────────────┐  │
│   │  Main Process           │  │
│   │  - Window management    │  │
│   │  - Python backend spawn │  │
│   │  - IPC handlers         │  │
│   └────────────┬────────────┘  │
│                │                │
│   ┌────────────▼────────────┐  │
│   │  Renderer Process       │  │
│   │  - UI logic             │  │
│   │  - API calls            │  │
│   │  - Event handlers       │  │
│   └─────────────────────────┘  │
└────────────────┬───────────────┘
                 │ HTTP API
┌────────────────▼───────────────┐
│   Python FastAPI Backend       │
│   (uvicorn server)             │
│                                │
│   - Whisper ASR                │
│   - File management            │
│   - Data storage               │
│   - Endpoints:                 │
│     • POST /upload             │
│     • POST /transcribe         │
│     • GET /transcripts         │
│     • POST /corrections        │
│     • WebSocket /ws/transcribe │
└────────────────────────────────┘
```

## Key Files

### Backend (Python)
- `webapp/api.py` - FastAPI server with all endpoints

### Frontend (Electron)
- `webapp/electron/main.js` - Electron main process
- `webapp/electron/preload.js` - Security bridge (exposes APIs to renderer)
- `webapp/electron/renderer/index.html` - UI structure
- `webapp/electron/renderer/styles.css` - Styling
- `webapp/electron/renderer/renderer.js` - Frontend logic

### Configuration
- `webapp/electron/package.json` - Node dependencies & build config

## Common Commands

```bash
# Development mode with DevTools
npm run dev

# Production mode (no DevTools)
npm start

# Build Windows installer
npm run build

# Build directory only (faster, for testing)
npm run build:dir

# Install new npm package
npm install <package-name>
```

## Building for Distribution

### Create Windows Installer

```bash
cd webapp/electron
npm run build
```

Output: `dist/Pulox Setup 0.1.0.exe`

### Note on Python Backend

The current build only packages the Electron frontend. Users need Python installed.

For a fully standalone app (future enhancement):
1. Use PyInstaller to compile Python backend
2. Bundle compiled Python with Electron
3. Update electron-builder config to include Python dist

## Troubleshooting

### Issue: "Cannot connect to backend"

**Solution:**
1. Check Python is installed: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Test backend manually: `python webapp/api.py`
4. Check if port 8000 is in use

### Issue: "Module 'whisper' not found"

**Solution:**
```bash
pip install openai-whisper torch torchaudio
```

### Issue: "FFmpeg not found"

**Solution (Windows):**
```bash
choco install ffmpeg
```

Or download from https://ffmpeg.org/

### Issue: npm install fails

**Solution:**
1. Check Node.js version: `node --version` (need v16+)
2. Delete `node_modules/` and `package-lock.json`
3. Run `npm install` again

### Issue: Electron won't start

**Solution:**
1. Check logs in terminal
2. Try: `npm cache clean --force`
3. Reinstall: `rm -rf node_modules && npm install`

## Development Workflow

### Making UI Changes

1. Edit files in `webapp/electron/renderer/`
2. Save changes
3. Reload app (Ctrl+R or Cmd+R in the app window)
4. Or restart: Stop app and run `npm run dev` again

### Adding New Features

1. **Add Backend Endpoint** (if needed)
   - Edit `webapp/api.py`
   - Add new route with `@app.get()` or `@app.post()`

2. **Expose to Renderer**
   - Edit `webapp/electron/preload.js`
   - Add method to `window.puloxApi`

3. **Use in Frontend**
   - Edit `webapp/electron/renderer/renderer.js`
   - Call the new API method

4. **Update UI**
   - Edit `webapp/electron/renderer/index.html` for structure
   - Edit `webapp/electron/renderer/styles.css` for styling

## Next Steps

1. ✅ Test basic transcription workflow
2. ✅ Test annotation workflow
3. ✅ Verify data is saved correctly
4. 📦 Package as standalone executable
5. 🚀 Deploy to UCLM for testing

## Resources

- Electron docs: https://www.electronjs.org/docs
- FastAPI docs: https://fastapi.tiangolo.com
- Whisper docs: https://github.com/openai/whisper

## Support

For issues or questions:
1. Check the logs in terminal
2. Open DevTools (F12) and check Console
3. Review this guide
4. Check the README files in each directory

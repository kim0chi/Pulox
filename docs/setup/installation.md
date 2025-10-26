# Pulox Electron App - Installation Guide

## Quick Install (Recommended)

Run the automated installer:
```bash
.\install_electron_deps.bat
```

If this fails, follow the **Manual Installation** below.

---

## Manual Installation

### Prerequisites

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
   - ✅ During installation, check "Add Python to PATH"

2. **Node.js 16+** - [Download](https://nodejs.org/)
   - Use LTS (Long Term Support) version

3. **FFmpeg** - Required for audio processing
   - **Windows (Chocolatey):**
     ```bash
     choco install ffmpeg
     ```
   - **Windows (Manual):**
     - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
     - Extract and add to PATH

### Step 1: Install Python Dependencies

#### Option A: Minimal Install (Recommended for Electron app)

```bash
pip install -r requirements-electron.txt
```

This installs only what's needed to run the Electron app backend.

#### Option B: One-by-one (If above fails)

```bash
# Core packages
pip install openai-whisper
pip install torch torchaudio

# Backend API
pip install fastapi
pip install "uvicorn[standard]"
pip install python-multipart

# Audio processing
pip install librosa soundfile numpy

# Utilities
pip install tqdm python-dotenv jiwer
```

#### Option C: Full Install (For development)

```bash
pip install -r requirements.txt
```

This installs everything including Streamlit, NLP models, etc.

### Step 2: Install Node.js Dependencies

```bash
cd webapp\electron
npm install
```

If you get errors, try:
```bash
npm cache clean --force
npm install
```

---

## Common Installation Issues

### Issue 1: Whisper Installation Fails

**Error:** `KeyError: '__version__'` or build wheel error

**Solution:**
```bash
# Install latest version without version constraint
pip install -U openai-whisper

# Or install specific known-good version
pip install git+https://github.com/openai/whisper.git
```

### Issue 2: PyTorch Installation Issues

**Error:** Torch installation taking too long or failing

**Solution - Install PyTorch separately first:**

CPU-only (Smaller, faster install):
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

GPU (CUDA 11.8):
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

GPU (CUDA 12.1):
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Then install the rest:
```bash
pip install openai-whisper fastapi "uvicorn[standard]" python-multipart
```

### Issue 3: "Microsoft Visual C++ 14.0 is required"

**Solution:** Install Visual Studio Build Tools
- Download: [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
- Or install via Chocolatey: `choco install visualstudio2019buildtools`

### Issue 4: npm install fails

**Solution:**
```bash
# Clear cache
npm cache clean --force

# Delete existing modules
cd webapp\electron
rmdir /s /q node_modules
del package-lock.json

# Reinstall
npm install
```

### Issue 5: FFmpeg not found

**Solution:**

1. Check if installed:
   ```bash
   ffmpeg -version
   ```

2. If not found, install:
   - **Chocolatey:** `choco install ffmpeg`
   - **Manual:** Download from ffmpeg.org and add to PATH

3. Restart terminal after installation

---

## Verify Installation

After installation, verify everything works:

### Test Python Backend

```bash
python webapp\api.py
```

You should see:
```
🚀 Starting Pulox API Server
📍 API Documentation: http://127.0.0.1:8000/docs
```

Open http://127.0.0.1:8000/docs in browser to see API docs.

Press `Ctrl+C` to stop.

### Test Electron App

```bash
cd webapp\electron
npm run dev
```

You should see:
- Python backend starting in terminal
- Electron window opening
- Connection status showing "Connected ●"

---

## Alternative: Docker Installation (Advanced)

If you continue having installation issues, you can run the backend in Docker:

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy requirements
COPY requirements-electron.txt .

# Install Python packages
RUN pip install -r requirements-electron.txt

# Copy source
COPY . .

# Run API
CMD ["python", "webapp/api.py"]
```

Build and run:
```bash
docker build -t pulox-backend .
docker run -p 8000:8000 pulox-backend
```

Then run Electron separately pointing to the Docker backend.

---

## Minimum System Requirements

- **OS:** Windows 10/11, macOS 10.15+, or Linux
- **RAM:** 4GB minimum, 8GB recommended (16GB for medium/large Whisper models)
- **Storage:** 2GB free space (more for models)
- **CPU:** Any modern processor (GPU optional but recommended for faster transcription)

---

## Next Steps

Once installed:

1. **Run the app:**
   ```bash
   .\run_electron_dev.bat
   ```
   or
   ```bash
   cd webapp\electron && npm run dev
   ```

2. **Test basic workflow:**
   - Upload an audio file
   - Transcribe it (use "tiny" model for quick test)
   - Annotate the transcript
   - Save annotation

3. **Read documentation:**
   - `ELECTRON_SETUP.md` - Full setup and usage guide
   - `webapp/electron/README.md` - Developer docs

---

## Getting Help

If you're still having issues:

1. **Check the error message** - Most errors indicate what's missing
2. **Update pip:** `python -m pip install --upgrade pip`
3. **Use virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements-electron.txt
   ```
4. **Try minimal install** - Install only core packages one by one
5. **Check Python version:** `python --version` (need 3.8+)
6. **Check Node.js version:** `node --version` (need 16+)

---

## Success Checklist

- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed
- ✅ FFmpeg installed and in PATH
- ✅ Python packages installed (`pip list | grep whisper`)
- ✅ Node packages installed (`webapp/electron/node_modules` exists)
- ✅ Backend starts: `python webapp/api.py`
- ✅ Frontend starts: `cd webapp/electron && npm run dev`
- ✅ App window opens and shows "Connected"

If all checkboxes are checked, you're ready to use Pulox! 🎉

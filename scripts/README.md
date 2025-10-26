# Pulox Scripts

This directory contains utility scripts for setting up and running the Pulox application.

## Available Scripts

### Windows Batch Scripts

#### `install_electron_deps.bat`
Installs all required dependencies for the Pulox desktop application.

**What it does:**
- Installs Python dependencies from `requirements.txt`
- Installs Node.js dependencies for the Electron app
- Sets up the development environment

**Usage:**
```bash
cd E:\Code\Pulox
scripts\install_electron_deps.bat
```

**Prerequisites:**
- Python 3.8+ installed and in PATH
- Node.js 16+ installed and in PATH
- Internet connection for downloading packages

---

#### `run_electron_dev.bat`
Launches the Pulox desktop application in development mode.

**What it does:**
- Starts the FastAPI backend server (port 8000)
- Launches the Electron desktop app with DevTools enabled
- Enables hot-reload for frontend changes

**Usage:**
```bash
cd E:\Code\Pulox
scripts\run_electron_dev.bat
```

**Prerequisites:**
- Dependencies installed (run `install_electron_deps.bat` first)
- FFmpeg installed and in PATH

**Ports used:**
- 8000: FastAPI backend server

---

### PowerShell Scripts

#### `setup_windows.ps1`
Automated Windows setup script for complete environment configuration.

**What it does:**
- Checks for Python installation
- Checks for Node.js installation
- Verifies FFmpeg availability
- Creates virtual environment
- Installs all dependencies
- Validates the installation

**Usage:**
```powershell
cd E:\Code\Pulox
.\scripts\setup_windows.ps1
```

**Prerequisites:**
- PowerShell 5.1 or higher
- Administrator privileges (recommended)
- Internet connection

---

## Troubleshooting

### "Python not found"
Ensure Python is installed and added to your PATH:
1. Download Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart your terminal

### "Node.js not found"
Ensure Node.js is installed and added to your PATH:
1. Download Node.js from https://nodejs.org/
2. Install using the default settings
3. Restart your terminal

### "FFmpeg not found"
Install FFmpeg using one of these methods:

**Chocolatey (recommended):**
```bash
choco install ffmpeg
```

**Manual installation:**
1. Download from https://ffmpeg.org/download.html
2. Extract to a directory (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your PATH

### Script fails with "execution policy" error
If running PowerShell scripts fails:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Development Workflow

1. **First time setup:**
   ```bash
   scripts\install_electron_deps.bat
   ```

2. **Run in development mode:**
   ```bash
   scripts\run_electron_dev.bat
   ```

3. **Build for production:**
   ```bash
   cd webapp\electron
   npm run build
   ```

---

## Additional Resources

- [Installation Guide](../docs/setup/installation.md) - Detailed setup instructions
- [Electron Setup](../docs/setup/electron-setup.md) - Desktop app specific guide
- [Project Status](../docs/project/status.md) - Current development status

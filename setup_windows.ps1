# Pulox Setup Script for Windows PowerShell
# Run with: .\setup_windows.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       PULOX PROJECT SETUP (WINDOWS)     " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Check Python
if (-not (Test-CommandExists "python")) {
    Write-Host "❌ Python is not installed. Please install Python 3.11" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Check if Python is 3.11
if ($pythonVersion -notmatch "3\.11") {
    Write-Host "⚠️ Warning: Python 3.11 is recommended. You have: $pythonVersion" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') { exit 1 }
}

# Check Git
if (-not (Test-CommandExists "git")) {
    Write-Host "❌ Git is not installed. Please install Git" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git found" -ForegroundColor Green

# Check ffmpeg
if (-not (Test-CommandExists "ffmpeg")) {
    Write-Host "⚠️ ffmpeg not found. Whisper needs ffmpeg to process audio files." -ForegroundColor Yellow
    Write-Host "To install ffmpeg:" -ForegroundColor Yellow
    Write-Host "  1. Install Chocolatey if not installed" -ForegroundColor Yellow
    Write-Host "  2. Run: choco install ffmpeg" -ForegroundColor Yellow
    Write-Host "  OR download from: https://ffmpeg.org/download.html" -ForegroundColor Yellow
    $continue = Read-Host "Continue without ffmpeg? (y/n)"
    if ($continue -ne 'y') { exit 1 }
} else {
    Write-Host "✅ ffmpeg found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Creating project structure..." -ForegroundColor Cyan

# Create directories
$directories = @(
    "data\raw_audio",
    "data\transcripts",
    "data\corrections",
    "data\summaries",
    "data\samples",
    "src\asr",
    "src\correction",
    "src\summarization",
    "src\utils",
    "src\evaluation",
    "models\asr",
    "models\correction",
    "models\summarization",
    "configs",
    "notebooks",
    "tests",
    "docs",
    "webapp\templates",
    "webapp\static"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
    # Create .gitkeep file
    $gitkeep = Join-Path $dir ".gitkeep"
    if (-not (Test-Path $gitkeep)) {
        New-Item -ItemType File -Path $gitkeep -Force | Out-Null
    }
}

Write-Host "✅ Directory structure created" -ForegroundColor Green

# Create __init__.py files
$initFiles = @(
    "src\__init__.py",
    "src\asr\__init__.py",
    "src\correction\__init__.py",
    "src\summarization\__init__.py",
    "src\utils\__init__.py",
    "src\evaluation\__init__.py"
)

foreach ($file in $initFiles) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
    }
}

Write-Host "✅ Python module files created" -ForegroundColor Green

# Initialize git repository
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

# Create or check virtual environment
Write-Host ""
Write-Host "Setting up Python virtual environment..." -ForegroundColor Cyan

$venvPath = ".venv311"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment with Python 3.11..." -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "✅ Virtual environment created: $venvPath" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists: $venvPath" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet

# Create requirements.txt if it doesn't exist
if (-not (Test-Path "requirements.txt")) {
    Write-Host "Creating requirements.txt..." -ForegroundColor Cyan
    @"
# Core ASR
openai-whisper==20231117
torch==2.1.0
torchaudio==2.1.0

# Audio processing
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1
ffmpeg-python==0.2.0

# NLP and ML
transformers==4.36.0
sentence-transformers==2.2.2
nltk==3.8.1
spacy==3.7.2
langdetect==1.0.9

# Data handling
pandas==2.1.3
numpy==1.24.3
tqdm==4.66.1

# Evaluation
jiwer==3.0.3
rouge-score==0.1.2
bert-score==0.3.13
evaluate==0.4.1

# Development
python-dotenv==1.0.0
pytest==7.4.3
black==23.11.0

# Web interface
streamlit==1.28.2
fastapi==0.104.1
uvicorn==0.24.0

# Optional TTS
gtts==2.5.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
    Write-Host "✅ requirements.txt created" -ForegroundColor Green
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies (this may take several minutes)..." -ForegroundColor Cyan
Write-Host "Installing core packages first..." -ForegroundColor Yellow

# Install PyTorch first (CPU version for simplicity, change if you have CUDA)
$hasCuda = $false
if (Test-CommandExists "nvidia-smi") {
    nvidia-smi | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $hasCuda = $true
        Write-Host "✅ CUDA detected. Installing GPU version of PyTorch..." -ForegroundColor Green
        pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121
    }
}

if (-not $hasCuda) {
    Write-Host "Installing CPU version of PyTorch..." -ForegroundColor Yellow
    pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0
}

# Install remaining requirements
Write-Host "Installing remaining packages..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Download spaCy models
Write-Host ""
Write-Host "Downloading spaCy language models..." -ForegroundColor Cyan
python -m spacy download en_core_web_sm
python -m spacy download xx_ent_wiki_sm
Write-Host "✅ spaCy models downloaded" -ForegroundColor Green

# Create .gitignore if it doesn't exist
if (-not (Test-Path ".gitignore")) {
    Write-Host "Creating .gitignore..." -ForegroundColor Cyan
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv*/
.env

# Data
data/raw_audio/*
!data/raw_audio/.gitkeep
data/transcripts/*
!data/transcripts/.gitkeep
data/corrections/*
!data/corrections/.gitkeep
data/summaries/*
!data/summaries/.gitkeep

# Models
models/**/*.pt
models/**/*.bin
*.pth

# Jupyter
.ipynb_checkpoints
*.ipynb

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ .gitignore created" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "       SETUP COMPLETE!                   " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ All components installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure ffmpeg is installed (if not done already)" -ForegroundColor Yellow
Write-Host "   choco install ffmpeg" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test the setup:" -ForegroundColor Yellow
Write-Host "   python test_initial_setup.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start the annotation tool:" -ForegroundColor Yellow
Write-Host "   streamlit run src\utils\annotation_tool.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test Whisper on sample audio:" -ForegroundColor Yellow
Write-Host "   python -c `"from src.asr.whisper_asr import WhisperASR; asr = WhisperASR('tiny'); print('Ready!')`"" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan
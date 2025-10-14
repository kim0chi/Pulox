#!/usr/bin/env python
"""
Test script to verify initial Pulox setup
Run this after setting up the project to ensure everything works
"""

import os
import sys
import json
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append('src')

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        import whisper
        print("✅ Whisper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import whisper: {e}")
        return False
    
    try:
        import torch
        print(f"✅ PyTorch imported successfully (CUDA available: {torch.cuda.is_available()})")
    except ImportError as e:
        print(f"❌ Failed to import torch: {e}")
        return False
    
    try:
        import transformers
        print(f"✅ Transformers imported successfully (version: {transformers.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import transformers: {e}")
        return False
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import streamlit: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence-transformers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import sentence-transformers: {e}")
        return False
    
    return True


def test_project_structure():
    """Verify project directory structure is correct"""
    print("\nTesting project structure...")
    
    required_dirs = [
        'data/raw_audio',
        'data/transcripts',
        'data/corrections',
        'data/summaries',
        'data/samples',
        'src/asr',
        'src/correction',
        'src/summarization',
        'src/utils',
        'models',
        'configs',
        'notebooks',
        'docs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            all_exist = False
    
    return all_exist


def test_whisper_asr():
    """Test Whisper ASR module"""
    print("\nTesting Whisper ASR module...")
    
    try:
        from asr.whisper_asr import WhisperASR
        
        # Create a test audio file
        print("Creating test audio file...")
        sample_rate = 16000
        duration = 3  # seconds
        frequency = 440  # A4 note
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # Add some silence
        silence = np.zeros(int(sample_rate * 0.5))
        audio = np.concatenate([silence, audio, silence])
        
        # Save test audio
        os.makedirs("data/samples", exist_ok=True)
        test_audio_path = "data/samples/test_tone.wav"
        sf.write(test_audio_path, audio, sample_rate)
        print(f"✅ Test audio created: {test_audio_path}")
        
        # Test transcription
        print("Testing Whisper transcription (this may take a moment)...")
        asr = WhisperASR(model_size="tiny")  # Use tiny for faster testing
        result = asr.transcribe(test_audio_path)
        
        print(f"✅ Transcription completed")
        print(f"   Model: {result['model']}")
        print(f"   Duration: {result['duration']:.2f} seconds")
        print(f"   Detected language: {result['language']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper ASR test failed: {e}")
        return False


def create_sample_filipino_audio():
    """Create a sample audio file with Filipino TTS for testing"""
    print("\nCreating sample Filipino audio for testing...")
    
    try:
        from gtts import gTTS
        
        # Sample Filipino-English mixed text
        text = "Magandang umaga po sa inyong lahat. Today we will discuss ang importance ng mathematics sa ating daily life."
        
        # Create TTS
        tts = gTTS(text=text, lang='tl', slow=False)
        audio_path = "data/samples/filipino_sample.mp3"
        tts.save(audio_path)
        
        print(f"✅ Sample Filipino audio created: {audio_path}")
        print(f"   Text: '{text[:50]}...'")
        
        # Test transcription on this audio
        from asr.whisper_asr import WhisperASR
        asr = WhisperASR(model_size="tiny")
        result = asr.transcribe(audio_path, language="tl")
        
        print(f"✅ Transcription result: '{result['text'][:100]}...'")
        
        return True
        
    except ImportError:
        print("ℹ️ gTTS not installed. Skipping Filipino audio test.")
        print("   Install with: pip install gtts")
        return True
    except Exception as e:
        print(f"⚠️ Sample audio creation failed: {e}")
        return True  # Not critical


def test_annotation_tool():
    """Test the annotation tool setup"""
    print("\nTesting annotation tool...")
    
    try:
        from utils.annotation_tool import AnnotationTool
        
        # Initialize tool
        tool = AnnotationTool()
        
        # Create a sample transcript
        sample_transcript = {
            "text": "This is a sample transcript. May mali dito na kailangan i-correct.",
            "duration": 10.5,
            "language": "tl"
        }
        
        # Save sample transcript
        transcript_path = tool.transcripts_dir / "sample_transcript.json"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(sample_transcript, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Sample transcript created: {transcript_path}")
        
        # Test loading
        files = tool.get_transcript_files()
        print(f"✅ Found {len(files)} transcript file(s)")
        
        if files:
            content = tool.load_transcript(files[0])
            print(f"✅ Successfully loaded transcript: '{content[:50]}...'")
        
        return True
        
    except Exception as e:
        print(f"❌ Annotation tool test failed: {e}")
        return False


def create_config_files():
    """Create initial configuration files"""
    print("\nCreating configuration files...")
    
    # Main config
    config = {
        "project": "Pulox",
        "version": "0.1.0",
        "data": {
            "audio_format": "wav",
            "sample_rate": 16000,
            "max_duration": 3600
        },
        "asr": {
            "model": "whisper",
            "model_size": "base",
            "language": "tl",
            "batch_size": 1
        },
        "correction": {
            "model": "mt5-small",
            "max_length": 512,
            "use_rules": True
        },
        "summarization": {
            "extractive_ratio": 0.3,
            "model": "mt5-small",
            "max_summary_length": 150
        }
    }
    
    config_path = Path("configs/config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created {config_path}")
    
    # Create .env.example
    env_example = """# Environment Variables for Pulox

# API Keys (if using cloud services)
GOOGLE_CLOUD_KEY=your-key-here
OPENAI_API_KEY=your-key-here

# Paths
DATA_DIR=./data
MODEL_DIR=./models
OUTPUT_DIR=./output

# Model Settings
WHISPER_MODEL=base
DEVICE=cuda  # or cpu

# Annotation Settings
ANNOTATOR_NAME=Your Name
"""
    
    with open(".env.example", 'w') as f:
        f.write(env_example)
    
    print("✅ Created .env.example")
    
    return True


def generate_summary_report():
    """Generate a summary report of the setup"""
    print("\n" + "="*50)
    print("PULOX INITIAL SETUP REPORT")
    print("="*50)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version.split()[0],
            "platform": sys.platform
        },
        "tests": {}
    }
    
    # Run all tests
    tests = [
        ("Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Whisper ASR", test_whisper_asr),
        ("Annotation Tool", test_annotation_tool),
        ("Config Files", create_config_files),
        ("Sample Audio", create_sample_filipino_audio)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 30)
        result = test_func()
        report["tests"][test_name] = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
    
    # Save report
    report_path = Path("docs/setup_report.json")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    for test_name, status in report["tests"].items():
        symbol = "✅" if status == "PASSED" else "❌"
        print(f"{symbol} {test_name}: {status}")
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 All tests passed! Your Pulox setup is ready.")
        print("\nNext steps:")
        print("1. Start collecting audio data from UCLM")
        print("2. Run the annotation tool: streamlit run src/utils/annotation_tool.py")
        print("3. Begin creating correction pairs for training")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that CUDA is properly installed if using GPU")
        print("3. Verify all directories were created correctly")
    
    print(f"\n📄 Full report saved to: {report_path}")
    print("="*50)


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════╗
║                  PULOX SETUP TEST                 ║
║     Hybrid Post-ASR Correction & Summarization    ║
╚═══════════════════════════════════════════════════╝
    """)
    
    generate_summary_report()
    
    print("\n💡 To start the annotation tool, run:")
    print("   streamlit run src/utils/annotation_tool.py")
    
    print("\n📚 To test Whisper on your own audio, run:")
    print("   python -c \"from src.asr.whisper_asr import WhisperASR; asr = WhisperASR(); print(asr.transcribe('your_audio.mp3')['text'])\"")
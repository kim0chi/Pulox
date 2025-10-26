"""
Quick test script to verify Whisper works on Windows
"""
import os
import sys
import numpy as np
import soundfile as sf

def test_whisper_installation():
    """Test that Whisper is properly installed"""
    print("Testing Whisper installation on Windows...")
    
    try:
        import whisper
        print("✅ Whisper imported successfully")
        
        # Check available models
        print("\nAvailable Whisper models:")
        for model in ['tiny', 'base', 'small', 'medium', 'large']:
            print(f"  - {model}")
        
        # Create a test audio file
        print("\nCreating test audio file...")
        os.makedirs("data/samples", exist_ok=True)
        
        # Generate 3 seconds of silence
        sample_rate = 16000
        duration = 3
        audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
        
        # Add a simple tone
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio += 0.1 * np.sin(2 * np.pi * 440 * t)  # A4 note
        
        # Save test audio
        test_file = "data/samples/test_tone.wav"
        sf.write(test_file, audio, sample_rate)
        print(f"✅ Test audio saved to: {test_file}")
        
        # Load Whisper model
        print("\nLoading Whisper model (tiny)...")
        model = whisper.load_model("tiny")
        print("✅ Model loaded successfully")
        
        # Test transcription
        print("\nTesting transcription...")
        result = model.transcribe(test_file)
        print("✅ Transcription completed!")
        print(f"   Result: '{result['text']}'")
        print(f"   Language detected: {result['language']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Whisper: {e}")
        print("\nTry reinstalling with:")
        print("  pip install openai-whisper")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ffmpeg():
    """Check if ffmpeg is available"""
    print("\nTesting ffmpeg availability...")
    
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            shell=True  # Needed on Windows
        )
        if result.returncode == 0:
            print("✅ ffmpeg is installed")
            version_line = result.stdout.split('\n')[0]
            print(f"   Version: {version_line}")
            return True
        else:
            raise Exception("ffmpeg not found")
    except Exception as e:
        print(f"❌ ffmpeg not found: {e}")
        print("\nTo install ffmpeg:")
        print("  1. Run PowerShell as Administrator")
        print("  2. Install Chocolatey if needed")
        print("  3. Run: choco install ffmpeg")
        print("\nOr download from: https://ffmpeg.org/download.html")
        return False

def test_torch():
    """Test PyTorch installation"""
    print("\nTesting PyTorch installation...")
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        
        import torchaudio
        print(f"✅ Torchaudio version: {torchaudio.__version__}")
        
        return True
    except Exception as e:
        print(f"❌ PyTorch error: {e}")
        return False

def main():
    print("="*50)
    print("PULOX WINDOWS COMPATIBILITY TEST")
    print("="*50)
    
    results = {
        "FFmpeg": test_ffmpeg(),
        "PyTorch": test_torch(),
        "Whisper": test_whisper_installation()
    }
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    all_passed = True
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component}: {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("\n🎉 All tests passed! Your Windows setup is ready for Pulox!")
        print("\nNext: Run the annotation tool:")
        print("  streamlit run src\\utils\\annotation_tool.py")
    else:
        print("\n⚠️ Some components need attention. See errors above.")
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
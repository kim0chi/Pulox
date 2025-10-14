"""
Whisper ASR Module for English-Tagalog Classroom Lectures
"""
import os
import json
import whisper
import torch
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import librosa
import soundfile as sf
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TranscriptionSegment:
    """Data class for transcript segments"""
    start: float
    end: float
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None

class WhisperASR:
    def __init__(self, model_size: str = "base", device: str = None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Fallback to CPU if GPU fails
        try:
            self.model = whisper.load_model(model_size, device=device)
            # Test if GPU works
            if device == "cuda":
                test_tensor = torch.randn(1, 80, 3000).to(device)
                _ = self.model.encoder(test_tensor)
        except Exception as e:
            print(f"GPU failed ({e}), falling back to CPU")
            device = "cpu"
            self.model = whisper.load_model(model_size, device=device)

        self.device = device
        self.model_size = model_size
        print(f"✅ Using device: {self.device}")

    def transcribe(
        self,
        audio_path: str,
        language: str = None,
        task: str = "transcribe",
        temperature: float = 0.0,
        beam_size: int = 5,
        best_of: int = 5,
        fp16: bool = True,
        condition_on_previous_text: bool = True,
        initial_prompt: str = None,
        word_timestamps: bool = False,
        prepend_punctuations: str = "\"'([{-",
        append_punctuations: str = "\"'.,!?:)]}",
        **kwargs
    ) -> Dict:
        """
        Transcribe audio file with Filipino/English optimization

        Args:
            audio_path: Path to audio file
            language: Language hint ('en', 'tl', or None for auto-detect)
            task: 'transcribe' or 'translate'
            temperature: Sampling temperature (0 for greedy)
            beam_size: Beam search width
            best_of: Number of candidates when sampling
            fp16: Use half-precision
            condition_on_previous_text: Use previous text as context
            initial_prompt: Initial prompt for better context
            word_timestamps: Generate word-level timestamps

        Returns:
            Dictionary with transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing: {audio_path}")

        # Optimize initial prompt for Filipino-English context
        if initial_prompt is None and language == "tl":
            initial_prompt = "Ito ay isang lecture sa classroom. This is a classroom lecture."

        # Full transcription using modern Whisper API
        result = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            temperature=temperature,
            beam_size=beam_size,
            best_of=best_of,
            fp16=fp16 and self.device == "cuda",
            condition_on_previous_text=condition_on_previous_text,
            initial_prompt=initial_prompt,
            word_timestamps=word_timestamps,
            prepend_punctuations=prepend_punctuations,
            append_punctuations=append_punctuations,
            **kwargs
        )

        # Process segments
        segments = []
        for seg in result.get("segments", []):
            segment = TranscriptionSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
                language=self._detect_segment_language(seg["text"])
            )
            segments.append(segment)

        return {
            "text": result["text"],
            "segments": segments,
            "language": result.get("language", language),
            "duration": self._get_audio_duration(audio_path),
            "model": self.model_size
        }

    def transcribe_batch(
        self,
        audio_paths: List[str],
        output_dir: str = None,
        **transcribe_kwargs
    ) -> List[Dict]:
        """
        Transcribe multiple audio files

        Args:
            audio_paths: List of audio file paths
            output_dir: Directory to save transcriptions
            **transcribe_kwargs: Arguments for transcribe method

        Returns:
            List of transcription results
        """
        results = []

        for audio_path in tqdm(audio_paths, desc="Transcribing"):
            try:
                result = self.transcribe(audio_path, **transcribe_kwargs)
                results.append(result)

                # Save to file if output directory specified
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    base_name = os.path.splitext(os.path.basename(audio_path))[0]
                    output_path = os.path.join(output_dir, f"{base_name}_transcript.json")

                    # Convert segments to serializable format
                    serializable_result = result.copy()
                    serializable_result["segments"] = [
                        {
                            "start": seg.start,
                            "end": seg.end,
                            "text": seg.text,
                            "language": seg.language
                        } for seg in result["segments"]
                    ]

                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(serializable_result, f, ensure_ascii=False, indent=2)

            except Exception as e:
                logger.error(f"Error transcribing {audio_path}: {e}")
                results.append({"error": str(e), "audio_path": audio_path})

        return results

    def _detect_segment_language(self, text: str) -> str:
        """
        Simple language detection for segments

        Args:
            text: Text segment

        Returns:
            'en', 'tl', or 'mixed'
        """
        # Common Tagalog words
        tagalog_markers = [
            'ang', 'ng', 'mga', 'sa', 'na', 'ay', 'at', 'ka', 'ko', 'mo',
            'naman', 'lang', 'ba', 'po', 'kasi', 'pero', 'yung', 'hindi',
            'ito', 'yan', 'dito', 'para', 'kung', 'siya', 'niya', 'kaniya'
        ]

        # Common English words
        english_markers = [
            'the', 'is', 'are', 'was', 'were', 'have', 'has', 'been',
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'and', 'or', 'but', 'if', 'then', 'that', 'this'
        ]

        words = text.lower().split()
        tagalog_count = sum(1 for word in words if word in tagalog_markers)
        english_count = sum(1 for word in words if word in english_markers)

        if tagalog_count > english_count * 2:
            return 'tl'
        elif english_count > tagalog_count * 2:
            return 'en'
        else:
            return 'mixed'
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds"""
        audio, sr = librosa.load(audio_path, sr=None)
        return len(audio) / sr
    
    def evaluate_wer(
        self,
        reference_path: str,
        hypothesis: str
    ) -> Dict[str, float]:
        """
        Calculate Word Error Rate
        
        Args:
            reference_path: Path to reference transcript
            hypothesis: Generated transcript
            
        Returns:
            Dictionary with WER metrics
        """
        from jiwer import wer, cer, mer
        
        with open(reference_path, 'r', encoding='utf-8') as f:
            reference = f.read()
        
        return {
            'wer': wer(reference, hypothesis),
            'cer': cer(reference, hypothesis),
            'mer': mer(reference, hypothesis)
        }


# Quick test function
def test_whisper():
    """Test Whisper with a sample audio file"""
    
    # Create a sample audio file (1 second of silence)
    sample_rate = 16000
    duration = 1  # seconds
    audio = np.zeros(int(sample_rate * duration))
    
    # Save sample audio
    os.makedirs("data/samples", exist_ok=True)
    sample_path = "data/samples/test_audio.wav"
    sf.write(sample_path, audio, sample_rate)
    
    # Test transcription
    asr = WhisperASR(model_size="tiny")  # Use tiny for quick testing
    result = asr.transcribe(sample_path)
    
    print("Test completed!")
    print(f"Transcription: {result['text']}")
    print(f"Duration: {result['duration']} seconds")
    print(f"Model: {result['model']}")
    
    return result


if __name__ == "__main__":
    # Run test
    test_whisper()
    
    # Example with actual audio
    # asr = WhisperASR(model_size="base")
    # result = asr.transcribe("path/to/your/audio.mp3", language="tl")
    # print(result["text"])
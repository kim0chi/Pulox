"""
Main Error Correction Module
Combines rule-based and ML-based correction for Filipino-English text
"""
import time
import re
from typing import Optional, List
import logging

# Optional ML dependencies (only needed if use_ml=True)
try:
    import torch
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    HAS_ML_DEPS = True
except ImportError:
    HAS_ML_DEPS = False
    torch = None
    T5ForConditionalGeneration = None
    T5Tokenizer = None

from .rules import CorrectionRules
from .models import (
    CorrectionResult, CorrectionChange, CorrectionConfig,
    CorrectionLevel, ErrorType
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorCorrector:
    """
    Hybrid error correction system for Filipino-English code-switched text

    Features:
    - Rule-based corrections for common patterns
    - ML-based correction using T5/MT5 models
    - Language-aware processing
    - Confidence scoring
    """

    def __init__(
        self,
        model_name: str = "google/mt5-small",
        device: str = None,
        use_ml: bool = True
    ):
        """
        Initialize error corrector

        Args:
            model_name: Hugging Face model name (default: mt5-small)
            device: 'cuda', 'cpu', or None for auto-detect
            use_ml: Whether to load ML model (set False for rules-only)
        """
        self.rules = CorrectionRules()
        self.use_ml = use_ml and HAS_ML_DEPS  # Only use ML if dependencies available
        self.ml_model = None
        self.tokenizer = None

        if device is None:
            device = "cuda" if (torch and torch.cuda.is_available()) else "cpu"
        self.device = device

        # Load ML model if requested and dependencies available
        if use_ml and not HAS_ML_DEPS:
            logger.warning("ML dependencies (torch, transformers) not installed. Using rules-only mode.")
            logger.warning("Install with: pip install torch transformers")

        if self.use_ml:
            try:
                logger.info(f"Loading correction model: {model_name}")
                self.tokenizer = T5Tokenizer.from_pretrained(model_name)
                self.ml_model = T5ForConditionalGeneration.from_pretrained(model_name)
                self.ml_model.to(self.device)
                self.ml_model.eval()
                logger.info(f"✅ Correction model loaded on {self.device}")
            except Exception as e:
                logger.warning(f"Could not load ML model: {e}")
                logger.warning("Falling back to rule-based correction only")
                self.use_ml = False

    def correct(
        self,
        text: str,
        config: Optional[CorrectionConfig] = None
    ) -> CorrectionResult:
        """
        Correct text using hybrid approach

        Args:
            text: Input text to correct
            config: Correction configuration

        Returns:
            CorrectionResult with corrected text and metadata
        """
        if config is None:
            config = CorrectionConfig()

        start_time = time.time()
        changes = []
        corrected_text = text

        # Step 1: Detect language
        language = self._detect_language(text) if not config.language_hint else config.language_hint
        logger.info(f"[ErrorCorrector] Detected language: '{language}' (hint: {config.language_hint})")

        # Step 2: Apply rule-based corrections
        if config.use_rules:
            corrected_text, rule_changes = self.rules.apply_rules(corrected_text, language)

            # Convert rule changes to CorrectionChange objects
            for change_desc in rule_changes:
                changes.append(CorrectionChange(
                    original="",  # Rules don't track exact original
                    corrected="",
                    error_type=self._classify_error_type(change_desc),
                    confidence=1.0,  # Rules are deterministic
                    description=change_desc
                ))

        # Step 3: Apply ML-based corrections (if available and enabled)
        if config.use_ml and self.use_ml and self.ml_model is not None:
            ml_corrected, ml_confidence = self._ml_correct(
                corrected_text,
                language,
                config.level
            )

            # Only apply ML correction if confidence is high enough
            if ml_confidence >= config.min_confidence and ml_corrected != corrected_text:
                # Track ML changes
                ml_changes = self._find_differences(corrected_text, ml_corrected)
                changes.extend(ml_changes)
                corrected_text = ml_corrected

        # Step 4: Final cleanup
        corrected_text = self._final_cleanup(corrected_text)

        # Calculate overall confidence
        if changes:
            confidence = sum(c.confidence for c in changes) / len(changes)
        else:
            confidence = 1.0 if corrected_text == text else 0.8

        processing_time = time.time() - start_time

        # Determine method used
        method = "rules" if not self.use_ml else ("ml" if not config.use_rules else "hybrid")

        logger.info(f"[ErrorCorrector] Correction complete: {len(changes)} changes, confidence: {confidence:.3f}, method: {method}")

        return CorrectionResult(
            original_text=text,
            corrected_text=corrected_text,
            changes=changes,
            confidence_score=round(confidence, 3),
            method=method,
            language=language,
            processing_time=round(processing_time, 3)
        )

    def _ml_correct(
        self,
        text: str,
        language: str,
        level: CorrectionLevel
    ) -> tuple[str, float]:
        """
        Apply ML-based correction using T5/MT5 model

        Args:
            text: Text to correct
            language: Language hint
            level: Correction level

        Returns:
            (corrected_text, confidence_score)
        """
        if self.ml_model is None:
            return text, 0.0

        try:
            # Prepare prompt based on language and level
            prompt = self._create_ml_prompt(text, language, level)

            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)

            # Generate correction
            with torch.no_grad():
                outputs = self.ml_model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                    output_scores=True,
                    return_dict_in_generate=True
                )

            # Decode
            corrected = self.tokenizer.decode(outputs.sequences[0], skip_special_tokens=True)

            # Calculate confidence from generation scores
            # This is a simplified confidence metric
            if hasattr(outputs, 'sequences_scores'):
                confidence = torch.exp(outputs.sequences_scores[0]).item()
            else:
                confidence = 0.8  # Default confidence

            return corrected, min(confidence, 1.0)

        except Exception as e:
            logger.error(f"ML correction failed: {e}")
            return text, 0.0

    def _create_ml_prompt(self, text: str, language: str, level: CorrectionLevel) -> str:
        """Create prompt for ML model based on language and level"""

        if language == 'tl':
            base_prompt = "Correct the following Tagalog text: "
        elif language == 'en':
            base_prompt = "Correct the following English text: "
        else:
            base_prompt = "Correct the following Filipino-English code-switched text: "

        if level == CorrectionLevel.LIGHT:
            base_prompt += "(fix only obvious errors) "
        elif level == CorrectionLevel.AGGRESSIVE:
            base_prompt += "(fix all errors and improve fluency) "

        return base_prompt + text

    def _detect_language(self, text: str) -> str:
        """
        Detect primary language of text

        Returns:
            'en', 'tl', or 'mixed'
        """
        # Use the language detection from ASR whisper_asr.py logic
        tagalog_markers = [
            'ang', 'ng', 'mga', 'sa', 'na', 'ay', 'at', 'ka', 'ko', 'mo',
            'po', 'nga', 'ba', 'lang', 'naman'
        ]
        english_markers = [
            'the', 'is', 'are', 'was', 'were', 'have', 'has', 'been',
            'will', 'and', 'or', 'but', 'this', 'that'
        ]

        words = text.lower().split()
        tl_count = sum(1 for w in words if w in tagalog_markers)
        en_count = sum(1 for w in words if w in english_markers)

        # Lower threshold (1.5x instead of 2x) to be more sensitive to code-switching
        # Filipino classrooms often have 30-60% English technical terms
        if tl_count > en_count * 1.5:
            return 'tl'
        elif en_count > tl_count * 1.5:
            return 'en'
        else:
            return 'mixed'

    def _classify_error_type(self, description: str) -> ErrorType:
        """Classify error type from description"""
        desc_lower = description.lower()

        if 'punctuation' in desc_lower or 'space' in desc_lower:
            return ErrorType.PUNCTUATION
        elif 'capital' in desc_lower:
            return ErrorType.CAPITALIZATION
        elif 'confusion' in desc_lower or 'phonetic' in desc_lower:
            return ErrorType.PHONETIC
        elif 'grammar' in desc_lower or 'article' in desc_lower:
            return ErrorType.GRAMMAR
        elif 'spell' in desc_lower:
            return ErrorType.SPELLING
        else:
            return ErrorType.WORD_CHOICE

    def _find_differences(self, original: str, corrected: str) -> List[CorrectionChange]:
        """Find differences between original and corrected text"""
        import difflib

        changes = []
        orig_words = original.split()
        corr_words = corrected.split()

        matcher = difflib.SequenceMatcher(None, orig_words, corr_words)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes.append(CorrectionChange(
                    original=' '.join(orig_words[i1:i2]),
                    corrected=' '.join(corr_words[j1:j2]),
                    error_type=ErrorType.WORD_CHOICE,
                    confidence=0.85,
                    description=f"ML: '{' '.join(orig_words[i1:i2])}' → '{' '.join(corr_words[j1:j2])}'"
                ))
            elif tag == 'delete':
                changes.append(CorrectionChange(
                    original=' '.join(orig_words[i1:i2]),
                    corrected='',
                    error_type=ErrorType.GRAMMAR,
                    confidence=0.8,
                    description=f"ML: Removed '{' '.join(orig_words[i1:i2])}'"
                ))
            elif tag == 'insert':
                changes.append(CorrectionChange(
                    original='',
                    corrected=' '.join(corr_words[j1:j2]),
                    error_type=ErrorType.GRAMMAR,
                    confidence=0.8,
                    description=f"ML: Added '{' '.join(corr_words[j1:j2])}'"
                ))

        return changes

    def _final_cleanup(self, text: str) -> str:
        """Final text cleanup"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        # Trim
        text = text.strip()
        # Ensure single space after punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        return text

    def correct_batch(
        self,
        texts: List[str],
        config: Optional[CorrectionConfig] = None
    ) -> List[CorrectionResult]:
        """
        Correct multiple texts

        Args:
            texts: List of texts to correct
            config: Correction configuration

        Returns:
            List of CorrectionResults
        """
        return [self.correct(text, config) for text in texts]


# Quick test
if __name__ == "__main__":
    print("Error Corrector Test")
    print("="*60)

    # Test with rules only (no ML model download)
    corrector = ErrorCorrector(use_ml=False)

    test_texts = [
        "dis is a example of incorrect grammar",
        "magandang umaga po sa inyong lahat  .",
        "ang punction ng dat program ay pra sa calculation",
        "kung saan  ba   yan?",
        "the bery importante lesson is about ang values"
    ]

    for text in test_texts:
        result = corrector.correct(text)
        print(f"\nOriginal:  {result.original_text}")
        print(f"Corrected: {result.corrected_text}")
        print(f"Method:    {result.method}")
        print(f"Language:  {result.language}")
        print(f"Changes:   {result.get_changes_summary()['total_changes']}")
        if result.changes:
            for change in result.changes[:3]:  # Show first 3 changes
                print(f"  - {change.description}")

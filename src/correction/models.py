"""
Data models for error correction module
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class CorrectionLevel(Enum):
    """Correction aggressiveness levels"""
    LIGHT = "light"          # Only obvious errors
    STANDARD = "standard"    # Balanced correction
    AGGRESSIVE = "aggressive" # Maximum correction


class ErrorType(Enum):
    """Types of errors that can be corrected"""
    SPELLING = "spelling"
    GRAMMAR = "grammar"
    PUNCTUATION = "punctuation"
    CAPITALIZATION = "capitalization"
    WORD_CHOICE = "word_choice"
    PHONETIC = "phonetic"
    CODE_SWITCH = "code_switch"


@dataclass
class CorrectionChange:
    """Individual change made during correction"""
    original: str
    corrected: str
    error_type: ErrorType
    confidence: float
    description: str


@dataclass
class CorrectionResult:
    """Result of text correction"""
    original_text: str
    corrected_text: str
    changes: List[CorrectionChange] = field(default_factory=list)
    confidence_score: float = 1.0
    method: str = "hybrid"  # 'rules', 'ml', or 'hybrid'
    language: str = "mixed"  # 'en', 'tl', or 'mixed'
    processing_time: float = 0.0

    def get_changes_summary(self) -> Dict:
        """Get summary statistics of changes"""
        if not self.changes:
            return {
                "total_changes": 0,
                "by_type": {},
                "average_confidence": 1.0
            }

        by_type = {}
        for change in self.changes:
            error_type = change.error_type.value
            if error_type not in by_type:
                by_type[error_type] = 0
            by_type[error_type] += 1

        avg_confidence = sum(c.confidence for c in self.changes) / len(self.changes)

        return {
            "total_changes": len(self.changes),
            "by_type": by_type,
            "average_confidence": round(avg_confidence, 3)
        }

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "original_text": self.original_text,
            "corrected_text": self.corrected_text,
            "changes": [
                {
                    "original": c.original,
                    "corrected": c.corrected,
                    "error_type": c.error_type.value,
                    "confidence": c.confidence,
                    "description": c.description
                }
                for c in self.changes
            ],
            "confidence_score": self.confidence_score,
            "method": self.method,
            "language": self.language,
            "processing_time": self.processing_time,
            "summary": self.get_changes_summary()
        }


@dataclass
class CorrectionConfig:
    """Configuration for correction process"""
    level: CorrectionLevel = CorrectionLevel.STANDARD
    use_rules: bool = True
    use_ml: bool = True
    language_hint: Optional[str] = None  # 'en', 'tl', or None for auto-detect
    preserve_code_switching: bool = True
    min_confidence: float = 0.7  # Minimum confidence to apply ML corrections


# Quick test
if __name__ == "__main__":
    # Test CorrectionResult
    result = CorrectionResult(
        original_text="dis is a example",
        corrected_text="this is an example",
        changes=[
            CorrectionChange(
                original="dis",
                corrected="this",
                error_type=ErrorType.PHONETIC,
                confidence=0.95,
                description="D → TH correction"
            ),
            CorrectionChange(
                original="a example",
                corrected="an example",
                error_type=ErrorType.GRAMMAR,
                confidence=1.0,
                description="a → an before vowel"
            )
        ],
        confidence_score=0.975,
        method="hybrid"
    )

    print("Correction Result Test")
    print("="*50)
    print(f"Original:  {result.original_text}")
    print(f"Corrected: {result.corrected_text}")
    print(f"\nSummary: {result.get_changes_summary()}")
    print(f"\nFull dict:\n{result.to_dict()}")

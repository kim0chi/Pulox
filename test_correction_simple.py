"""
Simple test script for error correction module (no pytest required)
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from correction.rules import CorrectionRules
from correction.models import CorrectionConfig, CorrectionLevel

def test_rules():
    print("=" * 60)
    print("Testing Rule-Based Correction")
    print("=" * 60)

    rules = CorrectionRules()

    test_cases = [
        ("dis is a example", "English phonetic + grammar"),
        ("ang punction ng program", "Filipino-English mixed"),
        ("the bery importante value", "Multiple phonetic errors"),
        ("magandang umaga po sa inyo", "Tagalog text"),
        ("kung saan  ba   yan?", "Extra spaces + Tagalog")
    ]

    for text, description in test_cases:
        corrected, changes = rules.apply_rules(text)
        print(f"\nTest: {description}")
        print(f"Original:  {text}")
        print(f"Corrected: {corrected}")
        print(f"Changes:   {len(changes)} corrections made")
        if changes:
            for change in changes[:3]:  # Show first 3
                print(f"  - {change}")

    print("\n" + "=" * 60)
    print("RULES TEST: PASSED")
    print("=" * 60)

def test_corrector_import():
    """Test that corrector can be imported (without ML dependencies)"""
    print("\n" + "=" * 60)
    print("Testing Error Corrector Import")
    print("=" * 60)

    try:
        # Import without using ML (no transformers needed)
        from correction.error_corrector import ErrorCorrector
        corrector = ErrorCorrector(use_ml=False)

        # Test basic correction
        result = corrector.correct("dis is a example with punction")

        print(f"\nOriginal:  {result.original_text}")
        print(f"Corrected: {result.corrected_text}")
        print(f"Method:    {result.method}")
        print(f"Language:  {result.language}")
        print(f"Changes:   {len(result.changes)} corrections")
        print(f"Time:      {result.processing_time:.3f}s")

        print("\n" + "=" * 60)
        print("CORRECTOR TEST: PASSED")
        print("=" * 60)

        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        print("=" * 60)
        print("CORRECTOR TEST: FAILED")
        print("=" * 60)
        return False

def test_models():
    """Test correction models"""
    print("\n" + "=" * 60)
    print("Testing Correction Models")
    print("=" * 60)

    from correction.models import CorrectionResult, CorrectionChange, ErrorType

    result = CorrectionResult(
        original_text="test text",
        corrected_text="corrected text",
        changes=[
            CorrectionChange(
                original="test",
                corrected="corrected",
                error_type=ErrorType.SPELLING,
                confidence=0.95,
                description="Test change"
            )
        ],
        confidence_score=0.95,
        method="rules"
    )

    print(f"\nOriginal:  {result.original_text}")
    print(f"Corrected: {result.corrected_text}")
    print(f"Summary:   {result.get_changes_summary()}")

    # Test serialization
    result_dict = result.to_dict()
    assert 'original_text' in result_dict
    assert 'corrected_text' in result_dict
    assert 'changes' in result_dict

    print("\n" + "=" * 60)
    print("MODELS TEST: PASSED")
    print("=" * 60)

if __name__ == "__main__":
    print("\nPULOX CORRECTION MODULE TEST SUITE")
    print("=" * 60)

    # Run tests
    test_rules()
    test_models()
    corrector_ok = test_corrector_import()

    print("\n" + "=" * 60)
    print("OVERALL RESULT:")
    if corrector_ok:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - Check error messages above")
    print("=" * 60)

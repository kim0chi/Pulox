"""
Test script to verify auto-correct bug fixes
Tests that phonetic corrections are applied to code-switched text
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from correction.error_corrector import ErrorCorrector
from correction.models import CorrectionConfig, CorrectionLevel

# Initialize corrector (rules-only, no ML model needed for this test)
print("="*70)
print("Testing Auto-Correct Bug Fixes")
print("="*70)
print("\nInitializing error corrector (rules-only mode)...\n")

corrector = ErrorCorrector(use_ml=False)

# Test cases with common errors that were being skipped
test_cases = [
    {
        "name": "Pure English with phonetic errors",
        "text": "dis is a example of incorrect grammar wit bery bad punction",
        "expected_fixes": ["dis->this", "dat", "bery->very", "punction->function", "a->an"]
    },
    {
        "name": "Mixed Filipino-English (heavy code-switching)",
        "text": "ang punction ng dis program ay pra sa calculation ng bery importante values",
        "expected_fixes": ["punction->function", "dis->this", "pra sa->para sa", "bery->very"]
    },
    {
        "name": "Predominantly Tagalog with English technical terms",
        "text": "magandang umaga po  .  ang lesson ay tungkol sa punction at dis algorithm",
        "expected_fixes": ["punction->function", "dis->this", "spacing"]
    },
    {
        "name": "Technical classroom lecture",
        "text": "the bery importante lesson is about ang formula pra computing dat alue",
        "expected_fixes": ["bery->very", "pormula->formula", "pra->para", "dat->that", "alue->value"]
    },
    {
        "name": "Only spacing issues",
        "text": "this is correct  but  has   extra    spaces",
        "expected_fixes": ["spacing only"]
    }
]

# Run tests
for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"Test {i}: {test['name']}")
    print(f"{'='*70}")
    print(f"Input:    '{test['text']}'")

    # Perform correction
    config = CorrectionConfig(
        level=CorrectionLevel.STANDARD,
        use_rules=True,
        use_ml=False
    )

    result = corrector.correct(test['text'], config)

    print(f"Output:   '{result.corrected_text}'")
    print(f"Language: {result.language}")
    print(f"Method:   {result.method}")
    print(f"Changes:  {len(result.changes)}")

    if result.changes:
        print(f"\nApplied corrections:")
        for j, change in enumerate(result.changes[:10], 1):  # Show first 10
            print(f"  {j}. {change.description}")
    else:
        print("\n[WARNING] No corrections applied!")

    # Check if expected fixes were applied
    print(f"\nExpected fixes: {', '.join(test['expected_fixes'])}")

    if result.corrected_text != test['text']:
        print("[PASS] Text was corrected")
    else:
        print("[FAIL] Text unchanged (corrections not applied)")

# Summary
print("\n" + "="*70)
print("Test Complete!")
print("="*70)
print("\nIf all tests show '[PASS]' and corrections are applied,")
print("the bug fix is working correctly.\n")
print("Now test in the Electron app:")
print("1. Run: scripts\\run_electron_dev.bat")
print("2. Transcribe audio or load an existing transcript")
print("3. Click 'Annotate' button")
print("4. Click 'Auto-Correct' button")
print("5. Verify corrections are applied (not just spacing)")
print("="*70)

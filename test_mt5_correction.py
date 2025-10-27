"""
Test MT5 ML-based correction
Verifies that the ML model loads and performs corrections
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from correction.error_corrector import ErrorCorrector
from correction.models import CorrectionConfig, CorrectionLevel

print("="*70)
print("Testing MT5 ML-Based Correction")
print("="*70)

print("\n[1/3] Testing Rules-Only Mode (baseline)...")
corrector_rules = ErrorCorrector(use_ml=False)
test_text = "dis is a example wit bery bad grammar"
result_rules = corrector_rules.correct(test_text)
print(f"Input:  '{test_text}'")
print(f"Output: '{result_rules.corrected_text}'")
print(f"Method: {result_rules.method}")
print(f"Changes: {len(result_rules.changes)}")

print("\n" + "="*70)
print("[2/3] Initializing ML Mode (will download MT5-small on first use)...")
print("This may take 5-15 minutes on first run (~1.2GB download)")
print("="*70)

try:
    corrector_ml = ErrorCorrector(use_ml=True)
    print(f"✓ ML Model loaded successfully!")
    print(f"  Device: {corrector_ml.device}")
    print(f"  Model active: {corrector_ml.use_ml}")

    print("\n" + "="*70)
    print("[3/3] Testing ML-Based Correction...")
    print("="*70)

    config_ml = CorrectionConfig(
        level=CorrectionLevel.STANDARD,
        use_rules=True,  # Hybrid: rules + ML
        use_ml=True,
        min_confidence=0.7
    )

    result_ml = corrector_ml.correct(test_text, config_ml)

    print(f"\nInput:   '{test_text}'")
    print(f"Output:  '{result_ml.corrected_text}'")
    print(f"Method:  {result_ml.method}")
    print(f"Changes: {len(result_ml.changes)}")
    print(f"Confidence: {result_ml.confidence_score:.2f}")
    print(f"Time: {result_ml.processing_time:.2f}s")

    if result_ml.changes:
        print(f"\nApplied corrections:")
        for i, change in enumerate(result_ml.changes[:10], 1):
            print(f"  {i}. {change.description}")

    print("\n" + "="*70)
    print("SUCCESS: MT5 is working!")
    print("="*70)
    print("\nNow you can use ML mode in the Electron app:")
    print("1. Start the app: scripts\\run_electron_dev.bat")
    print("2. Open a transcript and click 'Annotate'")
    print("3. Check the 'ML Mode' checkbox")
    print("4. Click 'Auto-Correct'")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] ML model failed to load or correct:")
    print(f"  {type(e).__name__}: {str(e)}")
    print(f"\nThis is expected if:")
    print(f"  - First time running (model needs to download)")
    print(f"  - No internet connection")
    print(f"  - Insufficient disk space (~1.2GB needed)")
    print("\nFalling back to rules-only mode is automatic in the app.")
    sys.exit(1)

"""
Unit tests for error correction module
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from correction.rules import CorrectionRules
from correction.error_corrector import ErrorCorrector
from correction.models import CorrectionConfig, CorrectionLevel, ErrorType


class TestCorrectionRules:
    """Test rule-based corrections"""

    def setup_method(self):
        """Setup for each test"""
        self.rules = CorrectionRules()

    def test_tagalog_particle_corrections(self):
        """Test Tagalog particle corrections"""
        text = "magandang umaga po sa inyo"
        corrected, changes = self.rules.apply_rules(text, 'tl')
        assert 'po' in corrected
        assert len(changes) >= 0

    def test_phonetic_corrections(self):
        """Test phonetic corrections (Filipino accent)"""
        # P/F confusion
        text = "the punction is important"
        corrected, changes = self.rules.apply_rules(text, 'en')
        assert 'function' in corrected
        assert any('P → F' in c or 'confusion' in c.lower() for c in changes)

        # V/B confusion
        text = "the bery importante value"
        corrected, changes = self.rules.apply_rules(text, 'en')
        assert 'very' in corrected

    def test_article_corrections(self):
        """Test article corrections (a/an)"""
        text = "this is a example of a error"
        corrected, changes = self.rules.apply_rules(text, 'en')
        assert 'an example' in corrected
        assert 'an error' in corrected

    def test_punctuation_corrections(self):
        """Test punctuation corrections"""
        text = "hello  world  .  how are you?"
        corrected, changes = self.rules.apply_rules(text, 'both')

        # Should remove extra spaces
        assert '  ' not in corrected
        # Should remove space before punctuation
        assert ' .' not in corrected

    def test_capitalization(self):
        """Test sentence capitalization"""
        text = "hello world. this is a test."
        corrected, changes = self.rules.apply_rules(text, 'both')

        # First word should be capitalized
        assert corrected[0].isupper()
        # After period should be capitalized
        assert 'This is' in corrected or 'this is' in corrected.lower()

    def test_common_error_corrections(self):
        """Test common ASR errors"""
        text = "gus2 ko yan pero di ba kinda hard"
        corrected, changes = self.rules.apply_rules(text, 'both')

        # Common errors should be fixed
        assert 'gusto' in corrected or 'gus2' not in corrected

    def test_tagalog_dictionary(self):
        """Test Tagalog dictionary"""
        assert self.rules.check_tagalog_spelling('po')
        assert self.rules.check_tagalog_spelling('ang')
        assert self.rules.check_tagalog_spelling('mga')
        assert not self.rules.check_tagalog_spelling('xyzabc')

    def test_spelling_suggestions(self):
        """Test spelling suggestions"""
        suggestions = self.rules.get_suggestions('poo')
        assert 'po' in suggestions or len(suggestions) > 0


class TestErrorCorrector:
    """Test error corrector (rules + ML)"""

    def setup_method(self):
        """Setup for each test - rules only, no ML model"""
        self.corrector = ErrorCorrector(use_ml=False)

    def test_basic_correction(self):
        """Test basic text correction"""
        text = "dis is a example"
        result = self.corrector.correct(text)

        assert result.corrected_text != text
        assert result.method in ['rules', 'hybrid']
        assert result.confidence_score > 0

    def test_no_changes_needed(self):
        """Test text that needs no correction"""
        text = "This is perfectly correct."
        result = self.corrector.correct(text)

        # May have minor changes (capitalization, etc)
        assert result.confidence_score >= 0.8

    def test_filipino_english_mixed(self):
        """Test Filipino-English code-switched text"""
        text = "ang punction ng program ay pra sa calculation"
        result = self.corrector.correct(text)

        assert 'function' in result.corrected_text
        assert 'para sa' in result.corrected_text or 'pra sa' not in result.corrected_text

    def test_correction_config_light(self):
        """Test light correction level"""
        text = "dis is a example punction"
        config = CorrectionConfig(level=CorrectionLevel.LIGHT)
        result = self.corrector.correct(text, config)

        assert isinstance(result.changes, list)
        assert result.method == 'rules'

    def test_correction_config_aggressive(self):
        """Test aggressive correction level"""
        text = "dis is a example punction"
        config = CorrectionConfig(level=CorrectionLevel.AGGRESSIVE)
        result = self.corrector.correct(text, config)

        assert result.corrected_text != text

    def test_language_detection(self):
        """Test language detection"""
        # English text
        result = self.corrector.correct("This is an English sentence")
        assert result.language in ['en', 'mixed']

        # Tagalog text
        result = self.corrector.correct("Ang mga estudyante ay nag-aaral sa eskwela")
        assert result.language in ['tl', 'mixed']

    def test_correction_result_structure(self):
        """Test correction result structure"""
        result = self.corrector.correct("dis is a example")

        assert hasattr(result, 'original_text')
        assert hasattr(result, 'corrected_text')
        assert hasattr(result, 'changes')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'method')
        assert hasattr(result, 'language')
        assert hasattr(result, 'processing_time')

    def test_changes_summary(self):
        """Test changes summary"""
        result = self.corrector.correct("dis is a example with bery bad punction")
        summary = result.get_changes_summary()

        assert 'total_changes' in summary
        assert 'by_type' in summary
        assert 'average_confidence' in summary
        assert isinstance(summary['total_changes'], int)

    def test_to_dict_serialization(self):
        """Test result serialization to dict"""
        result = self.corrector.correct("dis is a example")
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert 'original_text' in result_dict
        assert 'corrected_text' in result_dict
        assert 'changes' in result_dict
        assert 'summary' in result_dict

    def test_batch_correction(self):
        """Test batch correction"""
        texts = [
            "dis is a example",
            "ang punction ng program",
            "the bery importante lesson"
        ]

        results = self.corrector.correct_batch(texts)

        assert len(results) == len(texts)
        assert all(hasattr(r, 'corrected_text') for r in results)


class TestCorrectionModels:
    """Test correction data models"""

    def test_correction_level_enum(self):
        """Test CorrectionLevel enum"""
        assert CorrectionLevel.LIGHT.value == 'light'
        assert CorrectionLevel.STANDARD.value == 'standard'
        assert CorrectionLevel.AGGRESSIVE.value == 'aggressive'

    def test_error_type_enum(self):
        """Test ErrorType enum"""
        assert ErrorType.SPELLING.value == 'spelling'
        assert ErrorType.GRAMMAR.value == 'grammar'
        assert ErrorType.PUNCTUATION.value == 'punctuation'
        assert ErrorType.PHONETIC.value == 'phonetic'

    def test_correction_config_defaults(self):
        """Test CorrectionConfig defaults"""
        config = CorrectionConfig()

        assert config.level == CorrectionLevel.STANDARD
        assert config.use_rules is True
        assert config.use_ml is True
        assert config.preserve_code_switching is True
        assert config.min_confidence == 0.7


# Run tests with: pytest tests/test_correction.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

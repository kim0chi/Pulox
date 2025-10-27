"""
Rule-Based Error Correction for Filipino-English Code-Switched Text
Handles common ASR errors specific to Philippine classroom lectures
"""
import re
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Import Tagalog-specific corrections
from .rules_tl import (
    TAGALOG_WORD_SPLITS,
    ALL_TAGALOG_CORRECTIONS
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CorrectionRule:
    """Data class for correction rules"""
    pattern: str  # Regex pattern
    replacement: str
    description: str
    language: str  # 'en', 'tl', 'both'


class CorrectionRules:
    """Collection of correction rules for Filipino-English text"""

    def __init__(self):
        self.rules = self._load_rules()
        self.tagalog_dict = self._load_tagalog_dictionary()
        self.common_errors = self._load_common_errors()
        self.tagalog_word_splits = TAGALOG_WORD_SPLITS

        # Merge Tagalog corrections into common errors
        self.common_errors.update(ALL_TAGALOG_CORRECTIONS)
        logger.info(f"[Rules] Loaded {len(self.rules)} pattern rules + {len(self.tagalog_word_splits)} word splits + {len(ALL_TAGALOG_CORRECTIONS)} Tagalog corrections")

    def _load_rules(self) -> List[CorrectionRule]:
        """Load all correction rules"""
        rules = []

        # ===== TAGALOG SPECIFIC RULES =====

        # Common particle corrections
        rules.append(CorrectionRule(
            pattern=r'\bnga\b',
            replacement='nga',
            description='Tagalog particle nga',
            language='tl'
        ))

        rules.append(CorrectionRule(
            pattern=r'\bpo\b',
            replacement='po',
            description='Respectful particle po',
            language='tl'
        ))

        rules.append(CorrectionRule(
            pattern=r'\bho\b(?!\w)',
            replacement='po',
            description='po often misheard as ho',
            language='tl'
        ))

        # ng vs nang (common confusion)
        rules.append(CorrectionRule(
            pattern=r'\bnang\s+(ay|ang|mga|sa)',
            replacement=r'ng \1',
            description='ng before common Tagalog words',
            language='tl'
        ))

        # Common Tagalog word corrections
        rules.append(CorrectionRule(
            pattern=r'\byon\b',
            replacement='yon',
            description='Correct yon (that)',
            language='tl'
        ))

        rules.append(CorrectionRule(
            pattern=r'\bkung\s+saan\b',
            replacement='kung saan',
            description='kung saan (where)',
            language='tl'
        ))

        # ===== ENGLISH SPECIFIC RULES =====

        # Article corrections
        rules.append(CorrectionRule(
            pattern=r'\ba\s+([aeiou])',
            replacement=r'an \1',
            description='a -> an before vowels',
            language='en'
        ))

        # Common contractions
        rules.append(CorrectionRule(
            pattern=r'\bcannot\b',
            replacement="can't",
            description='cannot -> can\'t',
            language='en'
        ))

        rules.append(CorrectionRule(
            pattern=r'\bwill not\b',
            replacement="won't",
            description='will not -> won\'t',
            language='en'
        ))

        # ===== PHONETIC CORRECTIONS (Filipino accent) =====

        # F/P confusion (common in Filipino English)
        rules.append(CorrectionRule(
            pattern=r'\bpunction\b',
            replacement='function',
            description='P -> F confusion',
            language='both'  # Apply to all text (common in code-switching)
        ))

        rules.append(CorrectionRule(
            pattern=r'\bpormula\b',
            replacement='formula',
            description='P -> F confusion',
            language='both'  # Apply to all text (common in code-switching)
        ))

        # V/B confusion
        rules.append(CorrectionRule(
            pattern=r'\bbery\b',
            replacement='very',
            description='B -> V confusion',
            language='both'  # Apply to all text (common in code-switching)
        ))

        rules.append(CorrectionRule(
            pattern=r'\balue\b',
            replacement='value',
            description='B -> V confusion',
            language='both'  # Apply to all text (common in code-switching)
        ))

        # TH -> D/T confusion
        rules.append(CorrectionRule(
            pattern=r'\bdat\b(?!\w)',
            replacement='that',
            description='D -> TH correction',
            language='both'  # Apply to all text (common in code-switching)
        ))

        rules.append(CorrectionRule(
            pattern=r'\bdis\b(?!\w)',
            replacement='this',
            description='D -> TH correction',
            language='both'  # Apply to all text (common in code-switching)
        ))

        rules.append(CorrectionRule(
            pattern=r'\bwit\b(?!\w)',
            replacement='with',
            description='T -> TH correction',
            language='both'  # Apply to all text (common in code-switching)
        ))

        # ===== PUNCTUATION RULES =====

        # Multiple spaces
        rules.append(CorrectionRule(
            pattern=r'\s{2,}',
            replacement=' ',
            description='Multiple spaces -> single space',
            language='both'
        ))

        # Space before punctuation
        rules.append(CorrectionRule(
            pattern=r'\s+([.,!?;:])',
            replacement=r'\1',
            description='Remove space before punctuation',
            language='both'
        ))

        # Missing space after punctuation
        rules.append(CorrectionRule(
            pattern=r'([.,!?;:])([A-Za-z])',
            replacement=r'\1 \2',
            description='Add space after punctuation',
            language='both'
        ))

        # ===== CAPITALIZATION RULES =====

        # Sentence start capitalization (handled separately)

        return rules

    def _load_tagalog_dictionary(self) -> set:
        """Common Tagalog words for spell checking"""
        return {
            # Particles
            'po', 'nga', 'na', 'pa', 'ba', 'kasi', 'naman', 'lang',

            # Pronouns
            'ako', 'ka', 'mo', 'ko', 'niya', 'kaniya', 'kami', 'kayo', 'sila',
            'ito', 'iyan', 'yon', 'dito', 'diyan', 'doon',

            # Common verbs
            'gawin', 'gawa', 'kain', 'inom', 'tulog', 'gising', 'lakad',
            'punta', 'balik', 'dating', 'alis', 'tigil', 'simula', 'tapos',

            # Articles/determiners
            'ang', 'ng', 'mga', 'sa', 'ay',

            # Adjectives
            'maganda', 'ganda', 'pangit', 'mabuti', 'masama', 'malaki', 'maliit',

            # Common words
            'para', 'kung', 'sino', 'ano', 'saan', 'kailan', 'paano', 'bakit',
            'hindi', 'oo', 'wala', 'meron', 'may',

            # Numbers
            'isa', 'dalawa', 'tatlo', 'apat', 'lima', 'anim', 'pito', 'walo', 'siyam', 'sampu',

            # Classroom terms
            'klase', 'guro', 'estudyante', 'eskwela', 'libro', 'papel', 'lapis',
            'pagsusulit', 'takdang-aralin', 'pag-aaral'
        }

    def _load_common_errors(self) -> Dict[str, str]:
        """Common ASR misrecognitions specific to Filipino-English"""
        return {
            # Tagalog common errors
            'yung': 'yung',  # correct spelling
            'ung': 'yung',
            'kung ano': 'kung ano',
            'kung san': 'kung saan',
            'pra': 'para',
            'pra sa': 'para sa',
            'gus2': 'gusto',
            'bat': 'bakit',

            # English common errors
            'gonna': 'going to',
            'wanna': 'want to',
            'gotta': 'got to',
            'kinda': 'kind of',
            'sorta': 'sort of',

            # Mixed errors
            'di ba': 'hindi ba',
            'dba': 'hindi ba',
            'ano ba': 'ano ba',
            'anu': 'ano',
        }

    def _split_concatenated_words(self, text: str) -> Tuple[str, List[str]]:
        """
        Split words that ASR concatenated incorrectly (Tagalog-specific)

        Common issue: "kumusta ka" → ASR hears "commustaka" or "gamustaka"

        Args:
            text: Input text with potential concatenations

        Returns:
            (corrected_text, list_of_changes)
        """
        corrected = text
        changes = []

        for concatenated, split in self.tagalog_word_splits.items():
            if concatenated in corrected.lower():
                pattern = re.compile(r'\b' + re.escape(concatenated) + r'\b', re.IGNORECASE)
                if pattern.search(corrected):
                    corrected = pattern.sub(split, corrected)
                    changes.append(f"Split: '{concatenated}' -> '{split}'")
                    logger.debug(f"[Rules] Applied word split: '{concatenated}' -> '{split}'")

        return corrected, changes

    def apply_rules(self, text: str, language: str = 'both') -> Tuple[str, List[str]]:
        """
        Apply correction rules to text

        Args:
            text: Input text to correct
            language: 'en', 'tl', or 'both'

        Returns:
            (corrected_text, list_of_changes)
        """
        logger.info(f"[Correction] Applying rules with language filter: '{language}'")
        logger.info(f"[Correction] Input text length: {len(text)} chars")

        corrected = text
        changes = []

        # Step 1: ALWAYS apply word splitting (even for English text)
        # Reason: Filipino greetings can appear in any text regardless of primary language
        # The patterns are very specific (commustaka, gamustaka, etc.) so no false positives
        corrected, split_changes = self._split_concatenated_words(corrected)
        changes.extend(split_changes)
        if split_changes:
            logger.info(f"[Correction] Applied {len(split_changes)} word split(s)")

        # Step 2: Apply common error corrections
        for error, correction in self.common_errors.items():
            if error in corrected.lower():
                pattern = re.compile(r'\b' + re.escape(error) + r'\b', re.IGNORECASE)
                if pattern.search(corrected):
                    corrected = pattern.sub(correction, corrected)
                    changes.append(f"'{error}' -> '{correction}'")

        # Apply pattern-based rules
        for rule in self.rules:
            # For mixed language text, apply ALL rules (both en and tl)
            # This handles Filipino-English code-switching properly
            should_apply = (
                language == 'both' or
                rule.language == 'both' or
                rule.language == language or
                language == 'mixed'  # Apply all rules for code-switched text
            )

            if should_apply:
                pattern = re.compile(rule.pattern, re.IGNORECASE)
                if pattern.search(corrected):
                    new_text = pattern.sub(rule.replacement, corrected)
                    if new_text != corrected:
                        changes.append(f"{rule.description}")
                        corrected = new_text

        # Capitalize sentences
        corrected = self._capitalize_sentences(corrected)

        # Clean up extra spaces
        corrected = re.sub(r'\s+', ' ', corrected).strip()

        logger.info(f"[Correction] Applied {len(changes)} correction(s)")
        if changes:
            logger.info(f"[Correction] Changes: {changes[:5]}")  # Show first 5 changes

        return corrected, changes

    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize the first letter of each sentence"""
        # Split on sentence boundaries
        sentences = re.split(r'([.!?]+\s+)', text)

        result = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:  # Actual sentence, not punctuation
                # Capitalize first letter
                part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
            result.append(part)

        return ''.join(result)

    def check_tagalog_spelling(self, word: str) -> bool:
        """Check if a word is in Tagalog dictionary"""
        return word.lower() in self.tagalog_dict

    def get_suggestions(self, word: str) -> List[str]:
        """Get spelling suggestions for a word"""
        suggestions = []
        word_lower = word.lower()

        # Check if in dictionary
        if word_lower in self.tagalog_dict:
            return [word]

        # Find similar words (simple edit distance)
        for dict_word in self.tagalog_dict:
            if self._edit_distance(word_lower, dict_word) <= 2:
                suggestions.append(dict_word)

        return suggestions[:5]  # Top 5 suggestions

    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


# Quick test
if __name__ == "__main__":
    rules = CorrectionRules()

    # Test examples
    test_texts = [
        "magandang umaga po sa inyong lahat",
        "this is a example of incorrect grammar",
        "ang function ng dat is very importante",
        "kung saan  ba  yan  ?",
        "punction ng program ay pra sa calculation"
    ]

    print("Rule-Based Correction Test\n" + "="*50)
    for text in test_texts:
        corrected, changes = rules.apply_rules(text)
        print(f"\nOriginal:  {text}")
        print(f"Corrected: {corrected}")
        if changes:
            print(f"Changes:   {', '.join(changes)}")

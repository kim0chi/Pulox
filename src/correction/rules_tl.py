"""
Tagalog-Specific ASR Error Corrections
Handles common mishearings and concatenations in Filipino/Tagalog speech recognition
"""

# ===== WORD SPLITS (Concatenated Words) =====
# ASR often concatenates common Tagalog phrases into single words
TAGALOG_WORD_SPLITS = {
    # Greetings (most common ASR errors)
    'commustaka': 'kumusta ka',
    'gamustaka': 'kumusta ka',
    'kumustaka': 'kumusta ka',
    'camustaka': 'kumusta ka',
    'kamustaka': 'kumusta ka',

    'magandangumaga': 'magandang umaga',
    'magandanumaga': 'magandang umaga',
    'magandanghapon': 'magandang hapon',
    'magandanhapon': 'magandang hapon',
    'magandanggabi': 'magandang gabi',
    'magandangabi': 'magandang gabi',

    # Other common concatenations
    'kumustana': 'kumusta na',
    'anoba': 'ano ba',
    'saanba': 'saan ba',
    'sinoyan': 'sino yan',
    'ayokona': 'ayoko na',

    # Classroom phrases
    'takdangaralin': 'takdang aralin',
    'takdangara lin': 'takdang aralin',
    'pagaaralan': 'pag-aaralan',
    'pagaaral': 'pag-aaral',
    'pagsusulat': 'pagsusulat',  # Already correct, but catch variations

    # Polite particles concatenated
    'kapo': 'ka po',
    'napo': 'na po',
    'yonpo': 'yon po',
    'bapo': 'ba po',
}

# ===== COMMON TAGALOG ASR ERRORS =====
# Single word corrections for common mishearings
TAGALOG_ASR_ERRORS = {
    # Polite particle (most common!)
    'ho': 'po',  # "ho" is often heard instead of "po"

    # Question words
    'anu': 'ano',
    'ano-ano': 'ano ano',
    'saan-saan': 'saan saan',
    'bat': 'bakit',
    'bkit': 'bakit',
    'pano': 'paano',
    'panu': 'paano',
    'kelan': 'kailan',
    'klan': 'kailan',

    # Prepositions
    'pra': 'para',
    'pra sa': 'para sa',
    'sa sa': 'sa',  # Duplication error
    'ng ng': 'ng',  # Duplication error

    # Common adverbs/particles
    'na nga': 'na nga',
    'nga ba': 'nga ba',
    'lang lang': 'lang',  # Duplication
    'naman naman': 'naman',  # Duplication

    # Pronouns
    'ako ako': 'ako',  # Duplication
    'ikaw ikaw': 'ikaw',  # Duplication

    # Common verbs
    'gawa': 'gawa',
    'gawin': 'gawin',
    'kain': 'kain',
    'kainin': 'kainin',

    # Articles (ng vs nang confusion handled by existing rules)

    # Demonstratives
    'yan yan': 'yan',  # Duplication
    'yun': 'yun',
    'yon': 'yon',

    # Common classroom words
    'klase': 'klase',
    'aralin': 'aralin',
    'leksyon': 'leksyon',
    'guro': 'guro',
    'estudyante': 'estudyante',
    'iskolar': 'iskolar',

    # Numbers (mishearings)
    'tatlong': 'tatlong',
    'apat na': 'apat na',
}

# ===== TAGALOG CLASSROOM TERMS =====
# Subject-specific vocabulary that ASR often mishears
TAGALOG_CLASSROOM_TERMS = {
    # Math terms
    'matematika': 'matematika',
    'algebra': 'algebra',
    'geometry': 'geometry',
    'kalkulasyon': 'kalkulasyon',
    'numero': 'numero',

    # Science terms
    'siyensya': 'siyensya',
    'kimika': 'kimika',
    'pisika': 'pisika',
    'biolo hiya': 'biolohiya',
    'biolohiya': 'biolohiya',

    # General education
    'edukasyon': 'edukasyon',
    'pag-aaral': 'pag-aaral',
    'pag-aralan': 'pag-aralan',
    'pagsusulit': 'pagsusulit',
    'takdang-aralin': 'takdang-aralin',
    'takdang aralin': 'takdang aralin',

    # Actions
    'magsulat': 'magsulat',
    'magbasa': 'magbasa',
    'makinig': 'makinig',
    'sagutin': 'sagutin',
    'pakiulit': 'pakiulit',
    'ulitin': 'ulitin',

    # Comprehension
    'maintindihan': 'maintindihan',
    'naintindihan': 'naintindihan',
    'intindihin': 'intindihin',
    'malinaw': 'malinaw',
}

# ===== COMMON TAGALOG PHRASES =====
# Multi-word phrases that often get mangled
TAGALOG_COMMON_PHRASES = {
    # Greetings
    'kumusta ka': 'kumusta ka',
    'kumusta po': 'kumusta po',
    'kumusta na': 'kumusta na',
    'magandang umaga': 'magandang umaga',
    'magandang umaga po': 'magandang umaga po',
    'magandang hapon': 'magandang hapon',
    'magandang gabi': 'magandang gabi',

    # Polite expressions
    'salamat po': 'salamat po',
    'maraming salamat': 'maraming salamat',
    'opo': 'opo',
    'hindi po': 'hindi po',
    'oo po': 'oo po',

    # Classroom expressions
    'hindi ko maintindihan': 'hindi ko maintindihan',
    'hindi ko alam': 'hindi ko alam',
    'malinaw ba': 'malinaw ba',
    'gets nyo ba': 'gets nyo ba',
    'alam nyo na ba': 'alam nyo na ba',
    'may tanong ba': 'may tanong ba',
    'walang tanong': 'walang tanong',

    # Questions
    'ano ba yan': 'ano ba yan',
    'saan ba yan': 'saan ba yan',
    'sino ba yan': 'sino ba yan',
    'paano ba yan': 'paano ba yan',
    'bakit ba': 'bakit ba',

    # Instructions
    'pakiusap po': 'pakiusap po',
    'pakisagot': 'pakisagot',
    'pakibasa': 'pakibasa',
    'pakisulat': 'pakisulat',
}

# ===== TAGALOG-ENGLISH CODE-SWITCHING PATTERNS =====
# Common patterns where Tagalog and English mix
TAGALOG_ENGLISH_PATTERNS = {
    # Filler words
    'kasi naman': 'kasi naman',
    'e di': 'e di',
    'e ano': 'e ano',
    'tapos naman': 'tapos naman',
    'kaya nga': 'kaya nga',

    # Transition words
    'so ibig sabihin': 'so ibig sabihin',
    'which means na': 'which means na',
    'ganito kasi': 'ganito kasi',
    'kasi nga': 'kasi nga',
}

# ===== EXPORT ALL CORRECTIONS =====
# Combine all corrections into one dictionary
ALL_TAGALOG_CORRECTIONS = {}
ALL_TAGALOG_CORRECTIONS.update(TAGALOG_ASR_ERRORS)
ALL_TAGALOG_CORRECTIONS.update(TAGALOG_CLASSROOM_TERMS)
# Note: TAGALOG_WORD_SPLITS handled separately due to different logic

# For debugging/testing
if __name__ == "__main__":
    print("Tagalog Correction Rules Loaded")
    print("="*60)
    print(f"Word Splits: {len(TAGALOG_WORD_SPLITS)} patterns")
    print(f"ASR Errors: {len(TAGALOG_ASR_ERRORS)} corrections")
    print(f"Classroom Terms: {len(TAGALOG_CLASSROOM_TERMS)} terms")
    print(f"Common Phrases: {len(TAGALOG_COMMON_PHRASES)} phrases")
    print(f"Code-Switching: {len(TAGALOG_ENGLISH_PATTERNS)} patterns")
    print(f"\nTotal Corrections: {len(ALL_TAGALOG_CORRECTIONS)}")

    # Show some examples
    print("\nExample Word Splits:")
    for i, (wrong, correct) in enumerate(list(TAGALOG_WORD_SPLITS.items())[:5], 1):
        print(f"  {i}. '{wrong}' -> '{correct}'")

    print("\nExample ASR Errors:")
    for i, (wrong, correct) in enumerate(list(TAGALOG_ASR_ERRORS.items())[:5], 1):
        print(f"  {i}. '{wrong}' -> '{correct}'")

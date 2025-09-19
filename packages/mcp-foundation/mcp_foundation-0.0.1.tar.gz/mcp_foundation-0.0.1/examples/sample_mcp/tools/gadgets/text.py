"""Text processing gadgets."""

import hashlib
import re
from collections import Counter
from typing import Dict, Any
from fastmcp import Context
from mcp_foundation.server.context import get_mcp
from ..utils.validate import validate_required_param

mcp = get_mcp()

MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', ' ': '/'
}


@mcp.tool()
async def reverse_text(
    ctx: Context,
    text: str
) -> Dict[str, Any]:
    """
    Reverse any text string with various reversal options.
    
    Args:
        text: Text to reverse
        
    Returns:
        Dictionary containing different types of reversals
    """
    validate_required_param("text", text)
    
    return {
        "original": text,
        "reversed": text[::-1],
        "words_reversed": " ".join(text.split()[::-1]),
        "lines_reversed": "\n".join(text.split("\n")[::-1]),
        "length": len(text)
    }


@mcp.tool()
async def count_words(
    ctx: Context,
    text: str
) -> Dict[str, Any]:
    """
    Analyze text for word count, character count, and other statistics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary containing comprehensive text statistics
    """
    validate_required_param("text", text)
    
    lines = text.split('\n')
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Character analysis
    char_count = len(text)
    char_count_no_spaces = len(text.replace(' ', ''))
    
    # Word frequency
    word_freq = Counter(word.lower().strip('.,!?;:"()[]{}') for word in words)
    most_common = word_freq.most_common(5)
    
    return {
        "characters": {
            "total": char_count,
            "without_spaces": char_count_no_spaces,
            "spaces": char_count - char_count_no_spaces
        },
        "words": {
            "total": len(words),
            "unique": len(set(word.lower() for word in words)),
            "average_length": sum(len(word) for word in words) / len(words) if words else 0
        },
        "lines": len(lines),
        "sentences": len(sentences),
        "paragraphs": len([p for p in text.split('\n\n') if p.strip()]),
        "most_common_words": most_common,
        "reading_time_minutes": len(words) / 200  # Average reading speed
    }


@mcp.tool()
async def text_to_morse(
    ctx: Context,
    text: str
) -> Dict[str, Any]:
    """
    Convert text to Morse code.
    
    Args:
        text: Text to convert to Morse code
        
    Returns:
        Dictionary containing Morse code and metadata
    """
    validate_required_param("text", text)
    
    morse_result = []
    unsupported_chars = []
    
    for char in text.upper():
        if char in MORSE_CODE:
            morse_result.append(MORSE_CODE[char])
        elif char.isalnum() or char.isspace():
            if char not in unsupported_chars:
                unsupported_chars.append(char)
            morse_result.append('?')
        else:
            morse_result.append(' ')
    
    morse_text = ' '.join(morse_result)
    
    return {
        "original": text,
        "morse": morse_text,
        "dots_and_dashes": morse_text.replace('/', ' / '),
        "unsupported_characters": unsupported_chars,
        "character_count": len(text),
        "morse_length": len(morse_text)
    }


@mcp.tool()
async def analyze_text(
    ctx: Context,
    text: str
) -> Dict[str, Any]:
    """
    Perform comprehensive text analysis including readability metrics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary containing detailed text analysis
    """
    validate_required_param("text", text)
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    syllables = sum(_count_syllables(word) for word in words)
    
    # Readability metrics
    avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
    avg_syllables_per_word = syllables / len(words) if words else 0
    
    # Simple Flesch Reading Ease approximation
    if sentences and words:
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
    else:
        flesch_score = 0
    
    # Text complexity
    unique_words = len(set(word.lower() for word in words))
    lexical_diversity = unique_words / len(words) if words else 0
    
    return {
        "basic_stats": {
            "characters": len(text),
            "words": len(words),
            "sentences": len(sentences),
            "syllables": syllables
        },
        "averages": {
            "words_per_sentence": round(avg_words_per_sentence, 2),
            "syllables_per_word": round(avg_syllables_per_word, 2),
            "characters_per_word": round(len(text) / len(words), 2) if words else 0
        },
        "readability": {
            "flesch_reading_ease": round(flesch_score, 1),
            "reading_level": _get_reading_level(flesch_score),
            "lexical_diversity": round(lexical_diversity, 3)
        },
        "text_type": _classify_text_type(text)
    }


@mcp.tool()
async def generate_hash(
    ctx: Context,
    text: str,
    algorithm: str = "sha256"
) -> Dict[str, Any]:
    """
    Generate cryptographic hash of text using various algorithms.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Dictionary containing hash values and metadata
    """
    validate_required_param("text", text)
    validate_required_param("algorithm", algorithm)
    
    algorithm = algorithm.lower()
    supported_algorithms = ["md5", "sha1", "sha256", "sha512"]
    
    if algorithm not in supported_algorithms:
        raise ValueError(f"Unsupported algorithm. Use one of: {', '.join(supported_algorithms)}")
    
    # Generate primary hash
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    primary_hash = hash_obj.hexdigest()
    
    # Generate all hashes for comparison
    all_hashes = {}
    for alg in supported_algorithms:
        h = hashlib.new(alg)
        h.update(text.encode('utf-8'))
        all_hashes[alg] = h.hexdigest()
    
    return {
        "text": text,
        "algorithm": algorithm,
        "hash": primary_hash,
        "all_hashes": all_hashes,
        "text_length": len(text),
        "hash_length": len(primary_hash)
    }


def _count_syllables(word: str) -> int:
    """Estimate syllable count in a word."""
    word = word.lower().strip('.,!?;:"()[]{}')
    if not word:
        return 0
    
    vowels = 'aeiouy'
    syllable_count = 0
    prev_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            syllable_count += 1
        prev_was_vowel = is_vowel
    
    # Handle silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    return max(1, syllable_count)


def _get_reading_level(flesch_score: float) -> str:
    """Convert Flesch score to reading level description."""
    if flesch_score >= 90:
        return "Very Easy (5th grade)"
    elif flesch_score >= 80:
        return "Easy (6th grade)"
    elif flesch_score >= 70:
        return "Fairly Easy (7th grade)"
    elif flesch_score >= 60:
        return "Standard (8th-9th grade)"
    elif flesch_score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    elif flesch_score >= 30:
        return "Difficult (College level)"
    else:
        return "Very Difficult (Graduate level)"


def _classify_text_type(text: str) -> str:
    """Simple text type classification."""
    if len(text.split()) < 10:
        return "Short text/phrase"
    elif '?' in text and text.count('?') / len(text.split()) > 0.1:
        return "Question-heavy text"
    elif '!' in text and text.count('!') / len(text.split()) > 0.1:
        return "Exclamatory text"
    elif text.count('.') > text.count('!') + text.count('?'):
        return "Formal/declarative text"
    else:
        return "Mixed content"

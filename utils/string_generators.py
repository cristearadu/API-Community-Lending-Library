import random
from typing import List, Dict


def generate_unicode_username(language: str = None) -> str:
    """
    Generate random Unicode usernames in different languages.

    Args:
        language (str, optional): Specific language to generate ('chinese', 'bulgarian',
                                'arabic', 'korean', 'japanese'). If None, picks randomly.

    Returns:
        str: A random username in the specified language
    """
    unicode_ranges = {
        "chinese": (0x4E00, 0x9FFF),  # Common Chinese characters
        "bulgarian": (0x0410, 0x044F),  # Cyrillic alphabet
        "arabic": (0x0627, 0x064A),  # Basic Arabic letters only (أ to ي)
        "korean": (0xAC00, 0xD7AF),  # Korean Hangul
        "japanese": (0x3042, 0x3096)  # Japanese Hiragana letters only (あ to ゖ)
    }
    length = random.randint(4, 8)
    if language is None:
        language = random.choice(list(unicode_ranges.keys()))
    start, end = unicode_ranges[language]
    username = "".join(chr(random.randint(start, end)) for _ in range(length))

    return username


def generate_unicode_test_cases() -> List[Dict[str, str]]:
    """
    Generate test cases with Unicode usernames in different languages.

    Returns:
        List[Dict[str, str]]: List of dictionaries containing username and language
    """
    test_cases = []
    languages = ["chinese", "bulgarian", "arabic", "korean", "japanese"]

    for language in languages:
        username = generate_unicode_username(language)
        test_cases.append({"username": username, "language": language})

    return test_cases

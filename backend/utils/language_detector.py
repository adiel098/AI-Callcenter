"""
Language detection utility based on phone number country code
"""
from typing import Tuple, Optional
import re


# Mapping of country codes to languages and ElevenLabs voice IDs
COUNTRY_CODE_LANGUAGE_MAP = {
    "+972": {
        "language": "he",  # Hebrew
        "language_name": "Hebrew",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel - ElevenLabs Hebrew voice
        "country": "Israel"
    },
    "+1": {
        "language": "en",  # English
        "language_name": "English",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel - default ElevenLabs voice
        "country": "USA/Canada"
    },
    "+44": {
        "language": "en",  # English
        "language_name": "English",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "country": "UK"
    },
    "+33": {
        "language": "fr",  # French
        "language_name": "French",
        "voice_id": "ThT5KcBeYPX3keUQqHPh",  # ElevenLabs French voice
        "country": "France"
    },
    "+49": {
        "language": "de",  # German
        "language_name": "German",
        "voice_id": "ErXwobaYiN019PkySvjV",  # ElevenLabs German voice
        "country": "Germany"
    },
    "+34": {
        "language": "es",  # Spanish
        "language_name": "Spanish",
        "voice_id": "VR6AewLTigWG4xSOukaG",  # ElevenLabs Spanish voice
        "country": "Spain"
    },
    "+39": {
        "language": "it",  # Italian
        "language_name": "Italian",
        "voice_id": "XB0fDUnXU5powFXDhCwa",  # ElevenLabs Italian voice
        "country": "Italy"
    },
    "+61": {
        "language": "en",  # English
        "language_name": "English",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "country": "Australia"
    },
    "+971": {
        "language": "ar",  # Arabic
        "language_name": "Arabic",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # You'll need to configure Arabic voice
        "country": "UAE"
    },
    "+91": {
        "language": "en",  # English (India primarily uses English for business)
        "language_name": "English",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "country": "India"
    }
}


def extract_country_code(phone_number: str) -> Optional[str]:
    """
    Extract country code from phone number

    Args:
        phone_number: Phone number in international format (e.g., +972501234567)

    Returns:
        Country code (e.g., +972) or None if not found
    """
    # Remove any spaces, dashes, or parentheses
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone_number)

    # Match country codes (+ followed by 1-4 digits)
    match = re.match(r'(\+\d{1,4})', clean_phone)
    if match:
        country_code = match.group(1)

        # Check for exact match in our map
        if country_code in COUNTRY_CODE_LANGUAGE_MAP:
            return country_code

        # For codes like +1XXX, try +1
        for code in COUNTRY_CODE_LANGUAGE_MAP.keys():
            if clean_phone.startswith(code):
                return code

    return None


def detect_language_from_phone(phone_number: str) -> Tuple[str, str]:
    """
    Detect language and country code from phone number

    Args:
        phone_number: Phone number in international format

    Returns:
        Tuple of (language_code, country_code)
        Defaults to ('en', '+1') if not detected
    """
    country_code = extract_country_code(phone_number)

    if country_code and country_code in COUNTRY_CODE_LANGUAGE_MAP:
        language = COUNTRY_CODE_LANGUAGE_MAP[country_code]["language"]
        return (language, country_code)

    # Default to English if unable to detect
    return ("en", "+1")


def get_voice_for_language(language: str) -> str:
    """
    Get ElevenLabs voice ID for a given language

    Args:
        language: Language code (e.g., 'he', 'en', 'fr')

    Returns:
        ElevenLabs voice ID
    """
    # Find first matching language in our map
    for country_data in COUNTRY_CODE_LANGUAGE_MAP.values():
        if country_data["language"] == language:
            return country_data["voice_id"]

    # Default to Rachel (English) if not found
    return "21m00Tcm4TlvDq8ikWAM"


def get_language_info(phone_number: str) -> dict:
    """
    Get comprehensive language information from phone number

    Args:
        phone_number: Phone number in international format

    Returns:
        Dictionary with language, country_code, language_name, voice_id, country
    """
    country_code = extract_country_code(phone_number)

    if country_code and country_code in COUNTRY_CODE_LANGUAGE_MAP:
        info = COUNTRY_CODE_LANGUAGE_MAP[country_code].copy()
        info["country_code"] = country_code
        return info

    # Default to English/USA
    return {
        "language": "en",
        "language_name": "English",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "country": "Unknown",
        "country_code": "+1"
    }


def get_deepgram_language_code(language: str) -> str:
    """
    Convert language code to Deepgram API format

    Args:
        language: Language code (e.g., 'he', 'en')

    Returns:
        Deepgram language code (e.g., 'he-IL', 'en-US')
    """
    language_map = {
        "he": "he",  # Hebrew
        "en": "en-US",  # English
        "fr": "fr",  # French
        "de": "de",  # German
        "es": "es",  # Spanish
        "it": "it",  # Italian
        "ar": "ar"  # Arabic
    }

    return language_map.get(language, "en-US")

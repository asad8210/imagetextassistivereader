import os
import uuid
import logging
import time
import re
from typing import Dict, Optional
from gtts import gTTS
from gtts.lang import gTTSError
from playsound import playsound, PlaysoundException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("braille_tts.log"), logging.StreamHandler()]
)

# English Braille map (Grade 1)
english_braille_map: Dict[str, str] = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
    'A': '⠁', 'B': '⠃', 'C': '⠉', 'D': '⠙', 'E': '⠑',
    'F': '⠋', 'G': '⠛', 'H': '⠓', 'I': '⠊', 'J': '⠚',
    'K': '⠅', 'L': '⠇', 'M': '⠍', 'N': '⠝', 'O': '⠕',
    'P': '⠏', 'Q': '⠟', 'R': '⠗', 'S': '⠎', 'T': '⠞',
    'U': '⠥', 'V': '⠧', 'W': '⠺', 'X': '⠭', 'Y': '⠽', 'Z': '⠵',
    '0': '⠚', '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙',
    '5': '⠑', '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊',
    ' ': ' ', '.': '⠲', ',': '⠂', '\n': '\n', '!': '⠖',
    '?': '⠦', '-': '⠤', "'": '⠄', '"': '⠶', ';': '⠆',
    ':': '⠒', '(': '⠶', ')': '⠶', '/': '⠌'
}

# Hindi Braille map (Bharati Braille)
hindi_braille_map: Dict[str, str] = {
    # Vowels
    "अ": "⠁", "आ": "⠡", "इ": "⠊", "ई": "⠒", "उ": "⠥",
    "ऊ": "⠳", "ए": "⠑", "ऐ": "⠣", "ओ": "⠕", "औ": "⠷",
    "ऋ": "⠗",
    # Consonants
    "क": "⠅", "ख": "⠩", "ग": "⠛", "घ": "⠣", "ङ": "⠻",
    "च": "⠉", "छ": "⠡", "ज": "⠚", "झ": "⠒", "ञ": "⠱",
    "ट": "⠞", "ठ": "⠾", "ड": "⠙", "ढ": "⠹", "ण": "⠻",
    "त": "⠞", "थ": "⠮", "द": "⠙", "ध": "⠹", "न": "⠝",
    "प": "⠏", "फ": "⠟", "ब": "⠃", "भ": "⠫", "म": "⠍",
    "य": "⠽", "र": "⠗", "ल": "⠇", "व": "⠧", "श": "⠱",
    "ष": "⠳", "स": "⠎", "ह": "⠓",
    # Conjuncts
    "क्ष": "⠅⠰⠎", "ज्ञ": "⠛⠰⠝", "त्र": "⠞⠗", "श्र": "⠱⠗",
    "ग्य": "⠛⠽",
    # Special consonants
    "ड़": "⠻", "ढ़": "⠻⠄", "फ़": "⠋", "ज़": "⠵",
    # Vowel signs
    "ा": "⠡", "ि": "⠊", "ी": "⠒", "ु": "⠥", "ू": "⠳",
    "े": "⠑", "ै": "⠣", "ो": "⠕", "ौ": "⠷", "ृ": "⠗",
    # Other signs
    "्": "⠄", "ं": "⠈", "ः": "⠘", "ँ": "⠨",
    # Numbers (same as English, used with number sign)
    "०": "⠚", "१": "⠁", "२": "⠃", "३": "⠉", "४": "⠙",
    "५": "⠑", "६": "⠋", "७": "⠛", "८": "⠓", "९": "⠊",
    # Punctuation
    "।": "⠲", ",": "⠂", "?": "⠦", "!": "⠖", "\"": "⠶",
    "'": "⠄", ";": "⠆", ":": "⠒", ".": "⠲", "-": "⠤",
    "(": "⠶", ")": "⠶", "/": "⠌"
}

def detect_language(text: str) -> str:
    """
    Detect the primary language of the text based on Unicode ranges.
    Args:
        text: Input text.
    Returns:
        'hi' for Hindi (Devanagari), 'en' for English (Latin).
    """
    if not text:
        return 'hi'  # Default to Hindi
    devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
    latin_count = len(re.findall(r'[A-Za-z0-9]', text))
    return 'hi' if devanagari_count >= latin_count else 'en'

def convert_to_braille(text: str, language: Optional[str] = None) -> str:
    """
    Convert text to Braille with a language prefix, using Bharati Braille for Hindi.
    Args:
        text: Input text (English or Hindi).
        language: Optional language code ('en' or 'hi'). If None, auto-detect.
    Returns:
        Braille string with language prefix.
    """
    if not text or not isinstance(text, str):
        logging.warning("Invalid input: text is empty or not a string")
        return ""

    # Determine language
    lang = language if language in ['en', 'hi'] else detect_language(text)
    braille_map = hindi_braille_map if lang == 'hi' else english_braille_map
    prefix = "Hindi: " if lang == 'hi' else "English: "

    # Convert prefix to Braille
    prefix_braille = ''.join(braille_map.get(c, '⠿') for c in prefix)

    # Convert text to Braille
    result = []
    is_number = False

    for char in text:
        if char.isdigit() or char in hindi_braille_map.get('०', ''):  # Handle both English and Hindi digits
            if not is_number:
                result.append('⠼')  # Number sign
                is_number = True
            result.append(braille_map.get(char, '⠿'))
        else:
            is_number = False
            result.append(braille_map.get(char, '⠿'))

    braille_text = prefix_braille + ' ' + ''.join(result)
    logging.debug(f"Converted '{text}' to Braille ({lang}): {braille_text}")
    return braille_text

def _generate_and_play_audio(text: str, lang: str, filename: str) -> None:
    """
    Helper function to generate, play, and clean up audio.
    Args:
        text: Text to speak.
        lang: Language code ('en' or 'hi').
        filename: Path to save the audio file.
    """
    try:
        # Convert text to speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        logging.info(f"Generated audio file: {filename}")

        # Play the audio file
        playsound(filename)
        logging.info(f"Played audio file: {filename}")

        # Retry file deletion
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                    logging.info(f"Removed audio file: {filename}")
                break
            except OSError as e:
                logging.warning(f"Failed to remove {filename} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                else:
                    logging.error(f"Could not remove {filename} after {max_retries} attempts")

    except gTTSError as e:
        logging.error(f"Text-to-speech error: {e}")
        raise
    except PlaysoundException as e:
        logging.error(f"Playback error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in audio generation: {e}")
        raise

def speak(text: str, lang: str = 'hi') -> None:
    """
    Convert text to speech (defaults to Hindi), save it, play it, and clean up.
    Args:
        text: Text to speak (English or Hindi).
        lang: Language code ('en' for English, 'hi' for Hindi, defaults to 'hi').
    """
    if not text or not isinstance(text, str):
        logging.warning("Invalid input: text is empty or not a string")
        return

    try:
        # Ensure static/audio directory exists
        audio_dir = os.path.join('static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)

        # Generate unique filename
        filename = os.path.join(audio_dir, f"{uuid.uuid4()}.mp3")
        _generate_and_play_audio(text, lang, filename)

    except Exception as e:
        logging.error(f"Failed to speak: {e}")

def speak_english(text: str) -> None:
    """
    Convert English text to speech, save it, play it, and clean up.
    Args:
        text: English text to speak.
    """
    if not text or not isinstance(text, str):
        logging.warning("Invalid input: text is empty or not a string")
        return

    try:
        # Ensure static/audio directory exists
        audio_dir = os.path.join('static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)

        # Generate unique filename
        filename = os.path.join(audio_dir, f"{uuid.uuid4()}.mp3")
        _generate_and_play_audio(text, lang='en', filename)

    except Exception as e:
        logging.error(f"Failed to speak English text: {e}")

if __name__ == "__main__":
    # Example usage
    texts = [
        ("Hello, world!", "en"),
        ("नमस्ते, दुनिया!", "hi"),
        ("123", "en"),
        ("१२३", "hi"),
    ]
    for text, lang in texts:
        braille = convert_to_braille(text, lang)
        print(f"Text: '{text}', Language: {lang or 'auto'}, Braille: {braille}")
        if lang == "en":
            speak_english(text)
        else:
            speak(text, lang or detect_language(text))

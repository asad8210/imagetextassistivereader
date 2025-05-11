import os
import uuid
from gtts import gTTS
from playsound import playsound

# Braille conversion map (simplified)
braille_map = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵', ' ': ' ', '.': '⠲', ',': '⠂', '\n': '\n',
    '!': '⠖', '?': '⠦', '-': '⠤', "'": '⠄', '0': '⠴',
    '1': '⠂', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
    '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊'
}

def convert_to_braille(text):
    """
    Convert text to Braille representation.
    """
    return ''.join(braille_map.get(char.lower(), '?') for char in text)

# Inside the 'speak' function, save the file in the static folder
def speak(text):
    """
    Convert text to speech, save it, play it, and then delete the file.
    """
    try:
        # Ensure the static/audio directory exists
        audio_dir = 'static/audio'
        os.makedirs(audio_dir, exist_ok=True)

        # Generate a unique filename to avoid conflicts
        filename = os.path.join(audio_dir, f"{uuid.uuid4()}.mp3")

        # Convert text to speech
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        # Play the audio file
        playsound(filename)

        # Remove the audio file after playback
        if os.path.exists(filename):
            os.remove(filename)
            print(f"[INFO] Removed audio file: {filename}")

    except Exception as e:
        print(f"[ERROR] Text-to-speech failed: {e}")

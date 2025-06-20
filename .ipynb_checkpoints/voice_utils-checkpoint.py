# voice_utils.py
import speech_recognition as sr
from elevenlabs import play, generate
from config import ELEVEN_API_KEY, ELEVENLABS_VOICE_ID

import elevenlabs
elevenlabs.set_api_key(ELEVEN_API_KEY)

def transcribe():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("🎤 Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("🎤 Listening (up to 15s)...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)

    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        print(f"📝 Transcribed: {text}")
        return text.lower().strip()
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError as e:
        return f"STT error: {e}"

def speak(text):
    try:
        audio = generate(
            text=text,
            voice=ELEVENLABS_VOICE_ID,
            api_key=ELEVEN_API_KEY
        )
        print(f"🗣️ Speaking: {text}")
        play(audio)
    except Exception as e:
        print(f"❌ TTS error: {e}")

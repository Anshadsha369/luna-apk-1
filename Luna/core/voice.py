"""
Luna Voice Engine - Siri-like natural speech.
Features: varied intonation, natural pauses, conversational style.
"""

import threading
import time
import random
from kivy.utils import platform

IS_ANDROID = platform == 'android'

_tts_engine = None
_voice_lock = threading.Lock()
_speech_queue = []
_speech_thread = None


def speak(text):
    if not text:
        return
    if IS_ANDROID:
        _speak_android(text)
    else:
        _speak_desktop(text)


def speak_async(text):
    thread = threading.Thread(target=speak, args=(text,), daemon=True)
    thread.start()


def _speak_android(text):
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
        Locale = autoclass('java.util.Locale')
        activity = PythonActivity.mActivity
        tts = TextToSpeech(activity, None)

        # Siri-like settings: higher pitch, natural speed
        tts.setLanguage(Locale.ENGLISH)
        tts.setSpeechRate(0.92)
        tts.setPitch(1.05)

        tts.speak(text, TextToSpeech.QUEUE_FLUSH, None)
    except Exception:
        print(f"[Luna] {text}")


def _speak_desktop(text):
    global _tts_engine
    try:
        import pyttsx3
        if _tts_engine is None:
            _tts_engine = pyttsx3.init(driverName='sapi5')
            voices = _tts_engine.getProperty('voices')
            # Prefer Zira (female, natural)
            for v in voices:
                if 'zira' in v.name.lower():
                    _tts_engine.setProperty('voice', v.id)
                    break
            _tts_engine.setProperty('rate', 175)
            _tts_engine.setProperty('volume', 1.0)
        _tts_engine.say(text)
        _tts_engine.runAndWait()
    except Exception:
        print(f"[Luna] {text}")


def listen():
    if IS_ANDROID:
        return _listen_android()
    return _listen_desktop()


def _listen_android():
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        RecognizerIntent = autoclass('android.speech.RecognizerIntent')
        activity = PythonActivity.mActivity
        intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                        RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Talk to Luna...")
        intent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 500)
        activity.startActivityForResult(intent, 1001)
        # Note: real implementation needs result callback
        return None
    except Exception:
        return None


def _listen_desktop():
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        return r.recognize_google(audio).lower().strip()
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except Exception:
        return None


def greet():
    from core.personality import greet as personality_greet
    msg = personality_greet()
    speak(msg)
    return msg

"""
Screen Understanding - sees and interprets what's on screen.
Uses screenshots + LLM vision for analysis.
"""

import os
import time
import base64
import requests
import io
from pathlib import Path


class ScreenVision:
    def capture(self):
        try:
            import pyautogui
            buf = io.BytesIO()
            img = pyautogui.screenshot()
            img.save(buf, format='PNG')
            buf.seek(0)
            return buf.read()
        except Exception:
            return None

    def analyze(self, prompt="What's on this screen?"):
        img_data = self.capture()
        if not img_data:
            return "Can't capture screen on this device"
        try:
            b64 = base64.b64encode(img_data).decode()
            r = requests.post("http://127.0.0.1:11434/api/chat", json={
                "model": "llava",
                "messages": [{
                    "role": "user",
                    "content": prompt,
                    "images": [b64]
                }],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 256}
            }, timeout=30)
            if r.status_code == 200:
                return r.json()['message']['content'].strip()
            return "Vision analysis unavailable"
        except requests.ConnectionError:
            return "Ollama/llava not available for screen analysis"
        except Exception as e:
            return f"Analysis failed: {e}"

    def read_screen_text(self):
        return self.analyze("Read all text visible on this screen. Return only the text content.")

    def describe_screen(self):
        return self.analyze("Describe what's on this screen in 2-3 sentences.")

    def find_element(self, element_description):
        return self.analyze(f"Find this on the screen: {element_description}. Describe where it is located.")

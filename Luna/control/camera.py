"""
Camera Vision - identifies objects, plants, products, text, people.
Requires device camera and optionally Ollama with vision model (llava).
"""

import os
import tempfile
import base64
import requests
from kivy.utils import platform

IS_ANDROID = platform == 'android'
OLLAMA_HOST = "http://127.0.0.1:11434"


class CameraVision:
    def capture(self):
        if IS_ANDROID:
            return self._capture_android()
        return None

    def _capture_android(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            MediaStore = autoclass('android.provider.MediaStore')
            activity = PythonActivity.mActivity
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            temp_file = f"/sdcard/Pictures/Luna/capture_{int(time.time())}.jpg"
            os.makedirs("/sdcard/Pictures/Luna", exist_ok=True)
            uri = autoclass('android.net.Uri').fromFile(autoclass('java.io.File')(temp_file))
            intent.putExtra(MediaStore.EXTRA_OUTPUT, uri)
            activity.startActivityForResult(intent, 1002)
            return temp_file
        except Exception:
            return None

    def analyze_image(self, image_path, prompt="What's in this image?"):
        if not os.path.exists(image_path):
            return "Image not found"
        try:
            with open(image_path, 'rb') as f:
                image_b64 = base64.b64encode(f.read()).decode()
            r = requests.post(f"{OLLAMA_HOST}/api/chat", json={
                "model": "llava",
                "messages": [{
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64]
                }],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 256}
            }, timeout=30)
            if r.status_code == 200:
                return r.json()['message']['content'].strip()
            return "Vision analysis unavailable"
        except requests.ConnectionError:
            return "Ollama offline (need llava model for vision)"
        except Exception as e:
            return f"Analysis failed: {e}"

    def identify_object(self, image_path):
        return self.analyze_image(image_path, "Identify this object. What is it? Give me just the name.")

    def read_text(self, image_path):
        return self.analyze_image(image_path, "Read any text visible in this image. Return only the text.")

    def describe_scene(self, image_path):
        return self.analyze_image(image_path, "Describe this scene briefly.")

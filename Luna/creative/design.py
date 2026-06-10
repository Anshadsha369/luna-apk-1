"""
Creative Assistant - generates images, music concepts, designs.
Integrates with local AI models for creative work.
"""

import json
import os
import subprocess
import requests


class CreativeAssistant:
    def generate_image_prompt(self, idea):
        try:
            r = requests.post("http://127.0.0.1:11434/api/generate", json={
                "model": "mistral",
                "prompt": f"Create a detailed image generation prompt for: {idea}. Return only the prompt, no explanation.",
                "stream": False,
                "options": {"num_predict": 100}
            }, timeout=10)
            if r.status_code == 200:
                return r.json()['response'].strip()
        except Exception:
            pass
        return f"Image prompt: {idea}"

    def generate_image(self, prompt, output_path):
        try:
            import requests
            r = requests.post("http://127.0.0.1:7860/sdapi/v1/txt2img", json={
                "prompt": prompt,
                "steps": 20,
                "width": 512,
                "height": 512,
            }, timeout=60)
            if r.status_code == 200:
                import base64
                img_data = r.json()['images'][0]
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(img_data))
                return f"Image saved to {output_path}"
            return "Stable Diffusion unavailable. Start with: python stable_diffusion_webui.py"
        except requests.ConnectionError:
            return "Stable Diffusion not running. Start with: python stable_diffusion_webui.py"
        except Exception as e:
            return f"Image generation failed: {e}"

    def generate_code(self, description):
        try:
            r = requests.post("http://127.0.0.1:11434/api/generate", json={
                "model": "codellama",
                "prompt": f"Write code for: {description}. Include clear comments. Return only the code.",
                "stream": False,
                "options": {"num_predict": 500}
            }, timeout=30)
            if r.status_code == 200:
                return r.json()['response'].strip()
            return "Code generation unavailable"
        except requests.ConnectionError:
            return "Ollama offline (install codellama: ollama pull codellama)"
        except Exception as e:
            return f"Code gen error: {e}"

    def debug_code(self, code_snippet):
        try:
            r = requests.post("http://127.0.0.1:11434/api/generate", json={
                "model": "codellama",
                "prompt": f"Debug this code and explain issues:\n```\n{code_snippet}\n```\nReturn the fix and explanation.",
                "stream": False,
                "options": {"num_predict": 400}
            }, timeout=30)
            if r.status_code == 200:
                return r.json()['response'].strip()
            return "Debug capability unavailable"
        except Exception:
            return "Debug unavailable"

    def design_idea(self, concept, type="logo"):
        try:
            r = requests.post("http://127.0.0.1:11443/api/generate", json={
                "model": "mistral",
                "prompt": f"Describe a {type} design concept for: {concept}. Include colors, style, and layout ideas.",
                "stream": False,
                "options": {"num_predict": 200}
            }, timeout=15)
            if r.status_code == 200:
                return r.json()['response'].strip()
        except Exception:
            pass
        return f"Design concept for {concept} ({type}): Consider minimalist style with clean lines."

    def write_story(self, prompt, length="short"):
        words = 100 if length == "short" else 300 if length == "medium" else 500
        try:
            r = requests.post("http://127.0.0.1:11434/api/generate", json={
                "model": "mistral",
                "prompt": f"Write a {length} story: {prompt}",
                "stream": False,
                "options": {"num_predict": words}
            }, timeout=30)
            if r.status_code == 200:
                return r.json()['response'].strip()
        except Exception:
            pass
        return "Story generation unavailable"

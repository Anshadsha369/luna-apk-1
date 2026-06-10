"""
Luna Brain - LLM integration with Ollama.
Handles all AI conversation with context awareness.
"""

import json
import requests
import threading
from core.personality import system_prompt, NAME

OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_MODEL = "mistral"
MAX_HISTORY = 50

CONVERSATION = []
USER_PROFILE = {
    "name": None,
    "preferences": {},
    "habits": {},
    "reminders": [],
    "facts": [],
}


def set_host(host):
    global OLLAMA_HOST
    OLLAMA_HOST = host


def status():
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        if r.status_code == 200:
            models = r.json().get('models', [])
            return f"Online ({len(models)} models)" if models else "Online (no models)"
        return "Error"
    except requests.ConnectionError:
        return "Offline"
    except Exception:
        return "Unknown"


def think(user_input, capabilities=None, model=DEFAULT_MODEL):
    caps = capabilities or ["General assistance"]
    messages = [{"role": "system", "content": system_prompt(caps)}]
    for h in CONVERSATION[-MAX_HISTORY:]:
        messages.append(h)
    messages.append({"role": "user", "content": user_input})

    try:
        r = requests.post(f"{OLLAMA_HOST}/api/chat", json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 512}
        }, timeout=15)
        if r.status_code == 200:
            reply = r.json()['message']['content'].strip()
            CONVERSATION.append({"role": "user", "content": user_input})
            CONVERSATION.append({"role": "assistant", "content": reply})
            return reply, None
        return None, f"HTTP {r.status_code}"
    except requests.Timeout:
        return None, "timeout"
    except requests.ConnectionError:
        return None, "offline"
    except Exception as e:
        return None, str(e)


def think_async(user_input, callback, capabilities=None):
    thread = threading.Thread(
        target=lambda: callback(*think(user_input, capabilities)),
        daemon=True
    )
    thread.start()


def reset():
    CONVERSATION.clear()


def learn_fact(fact):
    USER_PROFILE["facts"].append(fact)


def get_summary():
    return {
        "model": DEFAULT_MODEL,
        "host": OLLAMA_HOST,
        "status": status(),
        "conversation_length": len(CONVERSATION),
        "facts": USER_PROFILE["facts"][-5:],
    }

"""
Luna Conversation Engine - Context-aware, natural conversations.
Maintains context across sessions, understands intent, manages state.
"""

import re
import time
import json
from pathlib import Path

MEMORY_DIR = Path.home() / ".luna_memory"
MEMORY_DIR.mkdir(exist_ok=True)

CONTEXT_FILE = MEMORY_DIR / "context.json"
STATE_FILE = MEMORY_DIR / "state.json"


class ConversationEngine:
    def __init__(self):
        self.context = self._load_context()
        self.state = self._load_state()
        self.current_topic = None
        self.last_intent = None
        self.session_start = time.time()

    def _load_context(self):
        if CONTEXT_FILE.exists():
            try:
                return json.loads(CONTEXT_FILE.read_text())
            except Exception:
                return {}
        return {"topics": [], "entities": {}, "preferences": {}, "history": []}

    def _save_context(self):
        CONTEXT_FILE.write_text(json.dumps(self.context, indent=2))

    def _load_state(self):
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text())
            except Exception:
                return {}
        return {"mood": "neutral", "last_interaction": None, "ongoing_tasks": []}

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

    def process(self, user_input):
        intent = self._detect_intent(user_input)
        entities = self._extract_entities(user_input)
        self._update_context(user_input, intent, entities)
        self.last_intent = intent
        return intent, entities

    def _detect_intent(self, text):
        patterns = {
            "greeting": r"^(hello|hi|hey|good morning|good evening|sup|yo)",
            "time": r"(time|what time|current time|clock)",
            "date": r"(date|what date|today'?s date|day)",
            "weather": r"(weather|temperature|how'?s the weather|rain|forecast)",
            "search": r"(search|google|look up|find|research)",
            "news": r"(news|headlines|what'?s happening)",
            "reminder": r"(remind|reminder|remember|don'?t forget)",
            "timer": r"(timer|countdown|set timer)",
            "alarm": r"(alarm|wake me|set alarm)",
            "sms": r"(sms|text|message|send.*message)",
            "call": r"(call|phone|dial|ring)",
            "open_app": r"(open|launch|start)\s+\w+",
            "close_app": r"(close|exit|quit|kill)\s+\w+",
            "screenshot": r"(screenshot|capture screen|screen)",
            "camera": r"(camera|take picture|photo|snap)",
            "flashlight": r"(flashlight|torch|light)",
            "volume": r"(volume|sound|mute|unmute)",
            "battery": r"(battery|charge|power left)",
            "wifi": r"(wifi|internet|network|connect)",
            "bluetooth": r"(bluetooth)",
            "brightness": r"(brightness|screen|display)",
            "translate": r"(translate|interpret|in\s+\w+)",
            "define": r"(define|meaning|what does|dictionary)",
            "calculate": r"(calculate|compute|math|sum|plus|minus|times|divided)",
            "note": r"(note|write down|take a note)",
            "read": r"(read|what did i write|show notes)",
            "remind_me": r"(remind me|set a reminder|remember that)",
            "schedule": r"(schedule|meeting|appointment|calendar|event)",
            "email": r"(email|mail|send.*email)",
            "music": r"(play|music|song|playlist|artist|album)",
            "joke": r"(joke|funny|make me laugh)",
            "help": r"(help|what can you do|features|capabilities)",
            "stop": r"(stop|cancel|abort|never mind)",
            "thanks": r"(thanks|thank you|thx|appreciate)",
            "goodbye": r"(bye|goodbye|see you|later|exit|quit)",
            "create": r"(create|make|generate|design|build)\s+\w+",
            "code": r"(code|program|script|function|debug|fix)",
            "learn": r"(teach|learn|explain|tutorial|lesson)",
            "health": r"(health|fitness|workout|exercise|diet|calories)",
            "finance": r"(finance|money|spend|budget|expense|bill)",
            "smart_home": r"(light|fan|ac|thermostat|plug|switch)",
            "translate_to": r"translate\s+to\s+\w+",
            "vision": r"(see|look|identify|what'?s this|recognize)",
            "automation": r"(automate|task|routine|workflow|sequence)",
            "screen": r"(screen|display|what'?s on|current screen)",
            "object": r"(object|thing|item|what is that)",
            "person": r"(who is|person|someone)",
        }
        for intent, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return intent
        return "general"

    def _extract_entities(self, text):
        entities = {}
        time_m = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', text, re.IGNORECASE)
        if time_m:
            entities["time"] = f"{time_m.group(1)}:{time_m.group(2)} {time_m.group(3) or ''}".strip()
        date_m = re.search(r'(today|tomorrow|next\s+\w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text, re.IGNORECASE)
        if date_m:
            entities["date"] = date_m.group(1)
        number_m = re.search(r'\b(\d+)\b', text)
        if number_m:
            entities["number"] = int(number_m.group(1))
        app_m = re.search(r'(?:open|launch|start|close|exit|kill)\s+(\w[\w\s]*)', text, re.IGNORECASE)
        if app_m:
            entities["app"] = app_m.group(1).strip()
        query_m = re.search(r'(?:search|google|look up|find)\s+(.+?)$', text, re.IGNORECASE)
        if query_m:
            entities["query"] = query_m.group(1).strip()
        message_m = re.search(r'(?:text|message|say)\s+(.+?)(?:\s+to\s+|\s*$)', text, re.IGNORECASE)
        if message_m:
            entities["message"] = message_m.group(1).strip()
        return entities

    def _update_context(self, text, intent, entities):
        ctx = self.context
        ctx["history"].append({
            "text": text,
            "intent": intent,
            "entities": entities,
            "time": time.time()
        })
        ctx["history"] = ctx["history"][-100:]
        if intent not in ("greeting", "thanks", "goodbye", "general"):
            ctx["topics"].append(intent)
            ctx["topics"] = ctx["topics"][-10:]
        self.current_topic = intent
        self._save_context()
        self._save_state()

    def get_context_summary(self):
        recent = self.context["history"][-5:] if self.context["history"] else []
        return {
            "current_topic": self.current_topic,
            "last_intent": self.last_intent,
            "recent_topics": self.context["topics"][-3:],
            "session_duration": int(time.time() - self.session_start),
            "total_interactions": len(self.context["history"]),
        }

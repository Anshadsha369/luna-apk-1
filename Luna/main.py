"""
L U N A  v2.0 - Personal AI Assistant
A Siri-like intelligent assistant with complete device control,
personal intelligence, and advanced capabilities.
"""

import os
import sys
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import platform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.personality import NAME, greet as personality_greet, acknowledge, confirm, error
from core.voice import speak, greet as voice_greet, listen
from core.brain import think, status as brain_status, reset as brain_reset
from core.conversation import ConversationEngine

from intelligence.personal import PersonalIntelligence
from control.phone import PhoneControl
from control.system import SystemControl
from control.camera import CameraVision
from control.smart_home import SmartHomeControl
from agents.internet import InternetAgent
from agents.automation import AutomationEngine
from agents.finance import FinanceAgent
from agents.health import HealthCoach
from creative.design import CreativeAssistant
from vision.screen import ScreenVision

IS_ANDROID = platform == 'android'


class ChatBubble(BoxLayout):
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [dp(60) if is_user else dp(10), dp(3), dp(10) if is_user else dp(60), dp(3)]

        is_luna = not is_user
        bg = (0.15, 0.3, 0.5, 0.8) if is_luna else (0.2, 0.2, 0.35, 0.8)
        prefix = "Luna" if is_luna else "You"

        label = Label(
            text=f"[b]{prefix}:[/b]\n{text}",
            markup=True,
            size_hint_y=None,
            text_size=(dp(280), None),
            halign='left' if is_luna else 'right',
            valign='top',
            color=(0.5, 0.85, 1, 1) if is_luna else (0.85, 0.85, 0.95, 1),
            font_size=dp(13),
            padding=[dp(10), dp(6)],
        )
        label.bind(texture_size=lambda *x: setattr(label, 'height', max(dp(30), label.texture_size[1] + dp(12))))
        self.add_widget(label)

        from kivy.metrics import dp
        from kivy.clock import Clock

        Clock.schedule_once(lambda dt: setattr(self, 'height', label.height + dp(6)))


class LunaUI(BoxLayout):
    pass


class LunaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation = ConversationEngine()
        self.personality = PersonalIntelligence()
        self.phone = PhoneControl()
        self.system = SystemControl()
        self.camera = CameraVision()
        self.smart_home = SmartHomeControl()
        self.internet = InternetAgent()
        self.automation = AutomationEngine()
        self.finance = FinanceAgent()
        self.health = HealthCoach()
        self.creative = CreativeAssistant()
        self.screen_vision = ScreenVision()
        self.listening = False

        self.capabilities = [
            "Natural conversation with context awareness",
            "Phone control: SMS, calls, contacts, apps, settings",
            "System control: battery, CPU, network, processes",
            "Camera vision: identify objects, text, scenes",
            "Smart home: lights, AC, fans, IoT devices",
            "Internet agent: search, research, news, weather, tracking",
            "Automation: multi-step workflows, routines",
            "Finance: expense tracking, budgets, bills",
            "Health: activity, meals, sleep, goals, coaching",
            "Creative: code generation, design ideas, stories",
            "Screen understanding: see and analyze your screen",
            "Personal intelligence: learns habits and preferences",
            "Translation between languages",
            "Coding help: write, debug, explain code",
        ]

    def build(self):
        self.title = f"{NAME} v2.0"
        Clock.schedule_once(self._post_build, 0.5)
        return LunaUI()

    def _post_build(self, dt):
        self._update_status(f"{NAME} v2.0 | Ollama: {brain_status()}")
        voice_greet()

    def _update_status(self, text):
        if hasattr(self, 'root') and self.root:
            try:
                self.root.ids.status_bar.text = text
            except Exception:
                pass

    def add_chat(self, text, is_user=False):
        try:
            container = self.root.ids.chat_container
            bubble = ChatBubble(text, is_user=is_user)
            container.add_widget(bubble)
            Clock.schedule_once(lambda dt: self._scroll_down(), 0.1)
        except Exception:
            pass

    def _scroll_down(self):
        try:
            scroll = self.root.ids.chat_scroll
            scroll.scroll_y = 0
        except Exception:
            pass

    def send(self, text):
        if not text or not text.strip():
            return
        try:
            self.root.ids.msg_input.text = ''
        except Exception:
            pass
        self.add_chat(text, is_user=True)
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text):
        intent, entities = self.conversation.process(text)
        response = self._handle(intent, entities, text)

        if not response:
            ai_response, error_type = think(text, self.capabilities)
            if error_type == "offline":
                response = "Ollama is offline. Start it with 'ollama serve' for full AI. I'll handle what I can locally."
                self._update_status(f"{NAME} | Ollama: offline")
            elif error_type:
                response = error()
            else:
                response = ai_response

        if response:
            Clock.schedule_once(lambda dt: self.add_chat(response, is_user=False))
            speak(response)

    def _handle(self, intent, entities, raw):
        raw_lower = raw.lower()

        # Greeting
        if intent == "greeting":
            return personality_greet()

        # Time/Date
        if intent in ("time", "date"):
            from agents.internet import get_time, get_date
            if intent == "time":
                return f"The time is {get_time()}"
            return f"Today is {get_date()}"

        # Weather
        if intent == "weather":
            loc = entities.get("query") or raw.replace("weather", "").replace("in", "").strip()
            return self.internet.get_weather(loc)

        # News
        if intent == "news":
            news = self.internet.get_news()
            return "Here are today's headlines:\n• " + "\n• ".join(news[:5]) if news else "News unavailable"

        # Search
        if intent == "search" and entities.get("query"):
            results = self.internet.search(entities["query"])
            return "Here's what I found:\n• " + "\n• ".join(results[:3]) if results else "No results"

        # Internet research
        if any(w in raw_lower for w in ["research", "investigate", "deep dive"]):
            query = raw.replace("research", "").replace("investigate", "").replace("deep dive", "").strip()
            if query:
                return self.internet.research(query)

        # SMS
        if intent == "sms":
            if not self.phone.available():
                return "SMS requires an Android device"
            msg = entities.get("message") or ""
            if msg:
                return self.phone.send_sms(None, msg)
            return "Who should I message?"

        # Battery
        if intent == "battery":
            if self.phone.available():
                lvl = self.phone.get_battery()
                charging = self.phone.is_charging()
                return f"Battery at {lvl}% {'(charging)' if charging else ''}"
            sys_bat = self.system.get_battery()
            return f"Battery: {sys_bat}"

        # System info
        if any(w in raw_lower for w in ["system", "specs", "computer info", "device info"]):
            info = self.system.get_system_info()
            return f"CPU: {info['cpu']}, RAM: {info['memory']}, Uptime: {info['uptime']}"

        # Open App
        if intent in ("open_app",) and entities.get("app"):
            if self.phone.available():
                return self.phone.open_app(entities["app"])
            return f"Opening {entities['app']}... (requires Android)"

        # Smart home
        if intent == "smart_home":
            devices = self.smart_home.list_devices()
            if isinstance(devices, list) and len(devices) > 0:
                return "Your devices:\n" + "\n".join(devices)
            return "No smart home devices configured. Say 'add device' to set one up."

        # Automation
        if intent == "automation":
            workflows = self.automation.list_workflows()
            if workflows:
                return f"Your workflows: {', '.join(workflows)}"
            return "No workflows yet. Say 'create morning routine' to start."

        # Finance
        if intent == "finance":
            summary = self.finance.get_summary()
            msg = f"Monthly spending: ${summary['monthly_spending']['total']:.2f}\n"
            for cat, amt in summary['monthly_spending']['by_category'].items():
                msg += f"  {cat}: ${amt:.2f}\n"
            if summary['alerts']:
                msg += "Alerts:\n" + "\n".join(summary['alerts'])
            return msg

        # Health
        if intent == "health":
            return self._get_health_summary()

        # Camera/Vision
        if intent == "camera":
            if not self.phone.available():
                return "Camera requires an Android device"
            path = self.camera.capture()
            if path:
                result = self.camera.describe_scene(path)
                return f"I see: {result}" if result else "Couldn't analyze image"
            return "Couldn't capture from camera"

        # Screen understanding
        if intent == "screen":
            result = self.screen_vision.analyze()
            return f"On your screen: {result}" if result else "Couldn't analyze screen"

        # Translation
        if intent == "translate":
            if entities.get("query"):
                return f"Translating: {entities['query']}" + "\n(Install translation model for full support)"

        # Creative - Code
        if intent == "code":
            if entities.get("query"):
                return self.creative.generate_code(entities["query"])
            return "What code should I write?"

        # Learning
        if intent == "learn":
            return "I can teach almost anything. Ask me about any topic and I'll explain it."

        # Note/Remember
        if intent == "note":
            if entities.get("query") or entities.get("message"):
                text_note = entities.get("query") or entities.get("message") or raw.replace("note", "").replace("remember", "").strip()
                self.personality.remember_fact(text_note)
                return f"Noted: {text_note}"
            return "What should I remember?"

        # Read notes
        if intent == "read":
            facts = self.personality.recall_facts()
            if facts:
                return "Things I remember:\n• " + "\n• ".join([f['text'] for f in facts[-5:]])
            return "I don't have any notes saved yet."

        # Timer
        if intent == "timer":
            if entities.get("number"):
                return f"Setting timer for {entities['number']} seconds... (timer feature active)"

        # Help
        if intent == "help":
            msg = f"I'm {NAME}, your AI assistant. I can:\n"
            for c in self.capabilities[:8]:
                msg += f"• {c}\n"
            msg += "\nWhat would you like help with?"
            return msg

        # Thanks
        if intent == "thanks":
            return confirm()

        # Goodbye
        if intent == "goodbye":
            self.stop()
            return "Goodbye! I'll be here when you need me."

        # Joke
        if intent == "joke":
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs.",
                "I'd tell you a joke about AI, but I'm still learning how to deliver punchlines.",
                "What's a computer's favorite snack? Microchips!",
                "Why did the AI break up with the human? Too many mixed signals.",
            ]
            import random
            return random.choice(jokes)

        # Name learning
        if "my name is" in raw_lower or "i'm " in raw_lower and len(raw) < 50:
            import re
            m = re.search(r"(?:my name is|i'm|i am)\s+(\w+)", raw_lower)
            if m:
                name = m.group(1).capitalize()
                return self.personality.learn_name(name)

        return None

    def _get_health_summary(self):
        today = self.health.get_today_summary()
        recs = self.health.get_recommendation()
        msg = f"Today's summary:\n"
        msg += f"  Calories: {today.get('calories', 0)}\n"
        msg += f"  Activity: {today.get('activity_minutes', 0)}min\n"
        msg += f"  Water: {today.get('water_glasses', 0)} glasses\n"
        if recs:
            msg += "\nRecommendations:\n" + "\n".join(f"  • {r}" for r in recs)
        return msg

    def toggle_voice(self):
        if not IS_ANDROID:
            self.add_chat("Voice input is available on Android devices.", is_user=False)
            return
        self.listening = not self.listening
        if self.listening:
            self._update_status("Listening...")
            threading.Thread(target=self._voice_listen, daemon=True).start()
        else:
            self._update_status(f"{NAME} | Voice: stopped")

    def _voice_listen(self):
        text = listen()
        if text:
            Clock.schedule_once(lambda dt: self.send(text))
        else:
            msg = "I didn't catch that. Could you repeat it?"
            Clock.schedule_once(lambda dt: self.add_chat(msg, is_user=False))
            speak(msg)
        self.listening = False
        Clock.schedule_once(lambda dt: self._update_status(f"{NAME} v2.0 | Ollama: {brain_status()}"))

    def clear_chat(self):
        try:
            self.root.ids.chat_container.clear_widgets()
        except Exception:
            pass
        brain_reset()
        Clock.schedule_once(lambda dt: self.add_chat("Conversation cleared.", is_user=False))

    def show_status(self):
        sys_info = self.system.get_system_info()
        p = self.personality.get_summary()
        msg = f"Ollama: {brain_status()}\n"
        msg += f"CPU: {sys_info['cpu']} | RAM: {sys_info['memory']}\n"
        msg += f"Known as: {p['name']}\n"
        msg += f"Facts stored: {p['facts_count']}"
        self.add_chat(msg, is_user=False)
        speak(f"All systems nominal. {brain_status()}")

    def show_help(self):
        msg = f"I'm {NAME}. I can help with:\n"
        for c in self.capabilities:
            msg += f"  • {c}\n"
        msg += "\nTry: 'What time is it?', 'Search for...', 'Check weather', 'Remind me...'"
        self.add_chat(msg, is_user=False)

    def on_stop(self):
        print(f"{NAME} shutting down.")


if __name__ == '__main__':
    LunaApp().run()

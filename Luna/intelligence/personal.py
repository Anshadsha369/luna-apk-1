"""
Personal Intelligence - learns habits, preferences, and patterns.
Adapts to user's style, predicts needs, remembers everything.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path.home() / ".luna_memory"
MEMORY_DIR.mkdir(exist_ok=True)

PROFILE_FILE = MEMORY_DIR / "profile.json"
HABITS_FILE = MEMORY_DIR / "habits.json"
PREFERENCES_FILE = MEMORY_DIR / "preferences.json"


class PersonalIntelligence:
    def __init__(self):
        self.profile = self._load(PROFILE_FILE, {})
        self.habits = self._load(HABITS_FILE, {})
        self.preferences = self._load(PREFERENCES_FILE, {})

    def _load(self, path, default):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                return default
        return default

    def _save(self, path, data):
        path.write_text(json.dumps(data, indent=2))

    def learn_name(self, name):
        self.profile["name"] = name
        self._save(PROFILE_FILE, self.profile)
        return f"Got it, {name}."

    def learn_preference(self, key, value):
        self.preferences[key] = {"value": value, "timestamp": time.time()}
        self._save(PREFERENCES_FILE, self.preferences)

    def get_preference(self, key, default=None):
        entry = self.preferences.get(key)
        return entry["value"] if entry else default

    def track_habit(self, category, action):
        today = datetime.now().strftime("%Y-%m-%d")
        if category not in self.habits:
            self.habits[category] = {}
        if today not in self.habits[category]:
            self.habits[category][today] = []
        self.habits[category][today].append({
            "action": action,
            "time": datetime.now().strftime("%H:%M")
        })
        self._save(HABITS_FILE, self.habits)

    def get_habit_insight(self, category):
        if category not in self.habits:
            return f"No data for {category} yet."
        days = sorted(self.habits[category].keys(), reverse=True)[:7]
        total = sum(len(self.habits[category][d]) for d in days)
        avg = total / max(len(days), 1)
        return f"Past {len(days)} days: {total} times (~{avg:.1f}/day)"

    def predict_need(self):
        hour = datetime.now().hour
        weekday = datetime.now().weekday()
        predictions = []

        if self.preferences.get("morning_routine"):
            if 6 <= hour <= 9:
                predictions.append("Start morning routine?")

        if self.preferences.get("evening_routine"):
            if 19 <= hour <= 22:
                predictions.append("Begin evening routine?")

        if self.habits.get("work") and weekday < 5:
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in self.habits.get("work", {}):
                if 9 <= hour <= 11:
                    predictions.append("Start work session?")

        return predictions

    def remember_fact(self, fact):
        if "facts" not in self.profile:
            self.profile["facts"] = []
        self.profile["facts"].append({
            "text": fact,
            "timestamp": datetime.now().isoformat()
        })
        self._save(PROFILE_FILE, self.profile)

    def recall_facts(self, query=None):
        facts = self.profile.get("facts", [])
        if query:
            query = query.lower()
            return [f for f in facts if query in f["text"].lower()]
        return facts[-10:]

    def get_summary(self):
        return {
            "name": self.profile.get("name", "Unknown"),
            "facts_count": len(self.profile.get("facts", [])),
            "preferences": list(self.preferences.keys()),
            "habits": list(self.habits.keys()),
        }

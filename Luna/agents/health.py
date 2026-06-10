"""
Health & Fitness Coach - tracks activity, provides recommendations,
monitors goals, and gives insights.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

HEALTH_DIR = Path.home() / ".luna_memory" / "health"
HEALTH_DIR.mkdir(parents=True, exist_ok=True)
ACTIVITY_FILE = HEALTH_DIR / "activity.json"
GOALS_FILE = HEALTH_DIR / "goals.json"


class HealthCoach:
    def __init__(self):
        self.activity = self._load(ACTIVITY_FILE, [])
        self.goals = self._load(GOALS_FILE, {})

    def _load(self, path, default):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return default

    def _save_activity(self):
        ACTIVITY_FILE.write_text(json.dumps(self.activity, indent=2))

    def _save_goals(self):
        GOALS_FILE.write_text(json.dumps(self.goals, indent=2))

    def log_activity(self, activity_type, duration_minutes, calories=None, notes=""):
        entry = {
            "type": activity_type,
            "duration": duration_minutes,
            "calories": calories or 0,
            "notes": notes,
            "date": datetime.now().isoformat(),
        }
        self.activity.append(entry)
        self._save_activity()
        return f"Logged {duration_minutes}min of {activity_type}"

    def log_meal(self, meal_type, calories, description=""):
        entry = {
            "type": "meal",
            "meal_type": meal_type,
            "calories": calories,
            "description": description,
            "date": datetime.now().isoformat(),
        }
        self.activity.append(entry)
        self._save_activity()
        return f"Logged {meal_type}: {calories} cal"

    def log_water(self, glasses):
        entry = {
            "type": "water",
            "glasses": glasses,
            "date": datetime.now().isoformat(),
        }
        self.activity.append(entry)
        self._save_activity()
        return f"Logged {glasses} glasses of water"

    def log_sleep(self, hours, quality="good"):
        entry = {
            "type": "sleep",
            "hours": hours,
            "quality": quality,
            "date": datetime.now().isoformat(),
        }
        self.activity.append(entry)
        self._save_activity()
        return f"Logged {hours}h of sleep ({quality})"

    def get_today_summary(self):
        today = datetime.now().strftime("%Y-%m-%d")
        entries = [e for e in self.activity if e["date"].startswith(today)]
        total_calories = sum(e.get("calories", 0) for e in entries if e["type"] == "meal")
        total_activity = sum(e.get("duration", 0) for e in entries if e["type"] != "meal" and e["type"] != "water")
        total_water = sum(e.get("glasses", 0) for e in entries if e["type"] == "water")
        sleep = [e for e in entries if e["type"] == "sleep"]
        return {
            "calories": total_calories,
            "activity_minutes": total_activity,
            "water_glasses": total_water,
            "sleep": sleep[-1] if sleep else None,
        }

    def get_weekly_summary(self):
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        entries = [e for e in self.activity if e["date"] >= week_ago]
        total_calories = sum(e.get("calories", 0) for e in entries if e["type"] == "meal")
        total_activity = sum(e.get("duration", 0) for e in entries if e["type"] not in ("meal", "water"))
        total_water = sum(e.get("glasses", 0) for e in entries if e["type"] == "water")
        avg_sleep = 0
        sleep_entries = [e for e in entries if e["type"] == "sleep"]
        if sleep_entries:
            avg_sleep = sum(e["hours"] for e in sleep_entries) / len(sleep_entries)
        return {
            "total_calories": total_calories,
            "total_activity_minutes": total_activity,
            "total_water": total_water,
            "avg_sleep_hours": round(avg_sleep, 1),
            "days_tracked": len(set(e["date"][:10] for e in entries)),
        }

    def set_goal(self, goal_type, target, period="daily"):
        self.goals[goal_type] = {"target": target, "period": period}
        self._save_goals()
        return f"Goal set: {target} {goal_type} per {period}"

    def check_goals(self):
        today = self.get_today_summary()
        week = self.get_weekly_summary()
        feedback = []
        for goal_type, goal in self.goals.items():
            target = goal["target"]
            period = goal["period"]
            if period == "daily":
                current = today.get(goal_type, 0)
            else:
                current = week.get(f"total_{goal_type}", 0)
            if current >= target:
                feedback.append(f"✓ {goal_type}: {current}/{target} - achieved!")
            else:
                remaining = target - current
                feedback.append(f"  {goal_type}: {current}/{target} - {remaining} remaining")
        return feedback

    def get_recommendation(self):
        today = self.get_today_summary()
        recs = []
        if today["water_glasses"] < 8:
            recs.append("Drink more water (aim for 8 glasses)")
        if today["activity_minutes"] < 30:
            recs.append("Get moving! 30min exercise recommended")
        if today["calories"] > 2500:
            recs.append("Watch your calorie intake today")
        if today.get("sleep") and today["sleep"]["hours"] < 7:
            recs.append("Try to get more sleep tonight (7-9 hours)")
        return recs or ["You're on track today!"]

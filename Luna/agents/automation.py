"""
Automation Engine - multi-step tasks, routines, workflows.
Executes sequences of actions automatically.
"""

import json
import time
import threading
import re
from pathlib import Path

AUTOMATION_DIR = Path.home() / ".luna_memory" / "automations"
AUTOMATION_DIR.mkdir(parents=True, exist_ok=True)

_running_threads = {}


class AutomationEngine:
    def create_workflow(self, name, steps):
        workflow = {
            "name": name,
            "steps": steps,
            "created": time.time(),
            "enabled": True
        }
        path = AUTOMATION_DIR / f"{name.replace(' ', '_')}.json"
        path.write_text(json.dumps(workflow, indent=2))
        return f"Workflow '{name}' created with {len(steps)} steps"

    def load_workflow(self, name):
        path = AUTOMATION_DIR / f"{name.replace(' ', '_')}.json"
        if path.exists():
            return json.loads(path.read_text())
        return None

    def list_workflows(self):
        return [f.stem for f in AUTOMATION_DIR.glob("*.json")]

    def delete_workflow(self, name):
        path = AUTOMATION_DIR / f"{name.replace(' ', '_')}.json"
        if path.exists():
            path.unlink()
            return f"Deleted '{name}'"
        return f"Workflow '{name}' not found"

    def run_workflow(self, name, context=None):
        workflow = self.load_workflow(name)
        if not workflow:
            return f"Workflow '{name}' not found"

        def _execute():
            for i, step in enumerate(workflow["steps"]):
                action = step.get("action", "")
                params = step.get("params", {})
                delay = step.get("delay", 0)
                if delay:
                    time.sleep(delay)
                print(f"[Automation] Step {i+1}: {action}")
                # Action dispatch would go here
                # Each action maps to a module function
            return f"Workflow '{name}' completed"

        thread = threading.Thread(target=_execute, daemon=True)
        thread.start()
        tid = f"{name}_{int(time.time())}"
        _running_threads[tid] = thread
        return f"Running workflow '{name}' ({len(workflow['steps'])} steps)"

    def create_morning_routine(self):
        steps = [
            {"action": "speak", "params": {"text": "Good morning!"}, "delay": 0},
            {"action": "smart_home", "params": {"device": "lights", "command": "on"}, "delay": 1},
            {"action": "weather", "params": {}, "delay": 0},
            {"action": "news", "params": {"topic": "technology"}, "delay": 0},
            {"action": "schedule", "params": {"day": "today"}, "delay": 0},
        ]
        return self.create_workflow("morning_routine", steps)

    def create_evening_routine(self):
        steps = [
            {"action": "smart_home", "params": {"device": "lights", "command": "off"}, "delay": 0},
            {"action": "speak", "params": {"text": "Good night!"}, "delay": 0},
            {"action": "reminder", "params": {"text": "Set alarm for tomorrow"}, "delay": 0},
        ]
        return self.create_workflow("evening_routine", steps)

    def parse_natural_workflow(self, text):
        steps = []
        actions = re.split(r'\b(then|and|after that|next|finally)\b', text, flags=re.IGNORECASE)
        for action in actions:
            action = action.strip()
            if not action:
                continue
            if re.search(r'(turn|switch|set)\s+(on|off)\s+(light|fan|ac)', action, re.IGNORECASE):
                m = re.search(r'(on|off)', action, re.IGNORECASE)
                device_m = re.search(r'(light|fan|ac|plug)', action, re.IGNORECASE)
                if m and device_m:
                    steps.append({
                        "action": "smart_home",
                        "params": {"device": device_m.group(1), "command": m.group(1)},
                        "delay": 1
                    })
            elif re.search(r'(weather|forecast)', action, re.IGNORECASE):
                steps.append({"action": "weather", "params": {}, "delay": 0})
            elif re.search(r'(news|headlines)', action, re.IGNORECASE):
                steps.append({"action": "news", "params": {}, "delay": 0})
            elif re.search(r'(schedule|calendar|meeting)', action, re.IGNORECASE):
                steps.append({"action": "schedule", "params": {}, "delay": 0})
        return steps if steps else None

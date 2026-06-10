"""Test all Luna modules"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.personality import NAME, greet, acknowledge, confirm, error
from core.voice import speak, listen
from core.brain import think, status as brain_status, reset as brain_reset
from core.conversation import ConversationEngine
from intelligence.personal import PersonalIntelligence
from control.system import SystemControl
from agents.internet import InternetAgent
from agents.finance import FinanceAgent
from agents.health import HealthCoach

print("All modules imported OK")
print("NAME:", NAME)
print("Greet:", greet())
print("Acknowledge:", acknowledge())
print("Confirm:", confirm())
print("Error:", error())
print("Ollama:", brain_status())

# Test conversation engine
conv = ConversationEngine()
intent, entities = conv.process("hello")
print("Intent (hello):", intent)
intent2, entities2 = conv.process("what time is it")
print("Intent (time):", intent2)
intent3, entities3 = conv.process("search for python tutorials")
print("Intent (search):", intent3, "entities:", entities3)
intent4, entities4 = conv.process("open chrome")
print("Intent (open):", intent4, "entities:", entities4)

# Test system
sys_ctl = SystemControl()
info = sys_ctl.get_system_info()
print("System - CPU:", info["cpu"], "RAM:", info["memory"])

# Test finance
fin = FinanceAgent()
print("Finance - monthly total:", fin.get_monthly_spending()["total"])

# Test health
hc = HealthCoach()
print("Health - today calories:", hc.get_today_summary()["calories"])

# Test internet
web = InternetAgent()
loc = web._get_location()
print("Location:", loc)

print("\n=== ALL TESTS PASSED ===")

import os
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from aiagent.services.ai_service import AIService

ai_service = AIService()
profile_data = {
    "name": "Test User",
    "age": 25,
    "gender": "male",
    "goal": "maintenance",
    "conditions": []
}

try:
    print("Sending message to AI...")
    reply = ai_service.chat_response("Hello, how are you?", profile_data)
    print(f"Reply: {reply}")
except Exception as e:
    print(f"Error: {e}")

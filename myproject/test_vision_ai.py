import os
import django
import json
import base64

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from aiagent.services.ai_service import AIService

ai_service = AIService()

# Create a tiny dummy JPEG base64 (1x1 pixel)
# Realistically, we'd use a real image, but let's see if the model even responds to a minimal one.
dummy_jpeg = (
    b'\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f'
    b'\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.344\xff\xc0\x00\x11\x08\x00\x01\x00\x01'
    b'\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x05\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c'
    b'\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xdf\xff\xd9'
)
image_b64 = base64.b64encode(dummy_jpeg).decode('utf-8')

try:
    print("Sending image to Vision AI...")
    result = ai_service.vision_analyze_food(image_b64)
    print(f"Result: {json.dumps(result, indent=2)}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

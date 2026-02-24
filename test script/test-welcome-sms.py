#!/usr/bin/env python3
"""
Test the exact welcome message
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_crm.settings')

import django
django.setup()

from django.conf import settings
import requests

def test_welcome_message():
    """Test the exact welcome message"""
    phone_number = "0241626072"  # The failing number from logs
    
    # The exact welcome message from views.py
    message = (
        f"Welcome to Ahinsan Youth Federation!\n\n"
        f"Dear Test User,\n\n"
        f"Thank you for registering for the 2025 Annual Youth Camp! "
        f"Here are your assigned room and division details:\n\n"
        f"Room: Test Room\n"
        f"Division: Test Division\n\n"
        f"We look forward to seeing you at the camp!\n\n"
        f"Best regards,\n"
        f"Ahinsan Youth Federation Team"
    )
    
    print(f"Testing with message length: {len(message)} characters")
    print(f"Message: {repr(message)}")
    
    # Clean phone number
    phone_number = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Format for Ghana numbers
    if phone_number.startswith('0'):
        phone_number = '233' + phone_number[1:]
    elif not phone_number.startswith('233'):
        phone_number = '233' + phone_number.lstrip('0')
    
    # Clean up sender ID
    sender_id = settings.ARKESEL_SENDER_ID.split('#')[0].strip()
    sender_id = sender_id[:11]
    
    # Arkesel API endpoint
    url = "https://sms.arkesel.com/api/v2/sms/send"
    
    # Request headers
    headers = {
        'api-key': settings.ARKESEL_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Request payload
    payload = {
        'sender': sender_id,
        'message': message,
        'recipients': [phone_number]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {response_data}")
            if response_data.get('status') == 'success':
                print("✅ Welcome SMS sent successfully!")
                return True
            else:
                error_msg = response_data.get('message', 'Unknown error')
                print(f"❌ Failed to send welcome SMS: {error_msg}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_welcome_message()

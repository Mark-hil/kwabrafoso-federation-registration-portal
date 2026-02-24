#!/usr/bin/env python3
"""
Test script to verify Arkesel SMS API key
"""
import os
import sys
import requests
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_crm.settings')

import django
django.setup()

from django.conf import settings

def test_api_key():
    """Test if API key is valid by sending a test SMS"""
    print("Testing Arkesel SMS API...")
    print(f"API Key: {settings.ARKESEL_API_KEY[:10]}...{settings.ARKESEL_API_KEY[-4:] if settings.ARKESEL_API_KEY else 'None'}")
    print(f"Sender ID: {settings.ARKESEL_SENDER_ID}")
    
    # Test by sending a simple SMS
    url = "https://sms.arkesel.com/api/v2/sms/send"
    
    headers = {
        'api-key': settings.ARKESEL_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Test payload
    payload = {
        'sender': settings.ARKESEL_SENDER_ID,
        'message': 'Test message from API validation',
        'recipients': ['233544919953']  # Test number
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if data.get('status') == 'success':
                print("✅ API Key is valid and working!")
                balance = data.get('sms_balance', 'N/A')
                print(f"Balance: {balance}")
                return True
            else:
                error_msg = data.get('message', 'Unknown error')
                print(f"❌ API Error: {error_msg}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key()

# members/utils/sms.py
import logging
import requests
import json
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(phone_number, message):
    """
    Send SMS using Arkesel API
    
    Args:
        phone_number (str): Recipient's phone number (e.g., "0501234567" or "233501234567")
        message (str): The message to send
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        # Validate inputs
        if not phone_number or not message:
            logger.error("Phone number or message is empty")
            return False
            
        # Clean phone number
        phone_number = ''.join(filter(str.isdigit, str(phone_number)))
        
        # Format for Ghana numbers (assuming local numbers start with 0)
        if phone_number.startswith('0'):
            phone_number = '233' + phone_number[1:]
        elif not phone_number.startswith('233'):
            phone_number = '233' + phone_number.lstrip('0')
        
        # Validate phone number length (should be 12 digits for Ghana: 233 + 9 digits)
        if len(phone_number) != 12 or not phone_number.startswith('233'):
            logger.error(f"Invalid phone number format: {phone_number}")
            return False
        
        # Clean up sender ID - ensure it's not too long and has no extra characters
        sender_id = settings.ARKESEL_SENDER_ID.split('#')[0].strip()  # Remove any comments
        sender_id = sender_id[:11]  # Ensure it's not longer than 11 characters
        
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
        
        # Log detailed info about SMS being sent
        logger.info(f"Sending SMS to {phone_number}...")
        logger.debug(f"SMS API KEY loaded: {bool(settings.ARKESEL_API_KEY)}")
        logger.debug(f"Sender ID: {sender_id}")
        logger.debug(f"Message length: {len(message)} characters")
        
        try:
            # Send request
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10  # 10 seconds timeout
            )
            
            # Parse JSON response
            response_data = response.json()
            
            # Check if response indicates success
            if response.status_code == 200 and response_data.get('status') == 'success':
                logger.info(f"SMS sent to {phone_number} (Balance: {response_data.get('sms_balance', 'N/A')})")
                return True
            else:
                error_msg = response_data.get('message', 'Unknown error')
                logger.error(f"Failed to send SMS to {phone_number}: {error_msg}")
                logger.error(f"Full response: {response_data}")
                logger.error(f"Status code: {response.status_code}")
                return False
                
        except json.JSONDecodeError:
            logger.error(f"Invalid response from SMS gateway for {phone_number}")
            logger.error(f"Raw response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as re:
        logger.error(f"Request error sending SMS to {phone_number}: {str(re)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending SMS to {phone_number}: {str(e)}", exc_info=True)
        return False
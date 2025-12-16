"""
Vonage SMS Service for PhishVision
Handles SMS sending for phishing simulation campaigns via Vonage (Nexmo)
"""

import os
from datetime import datetime
from typing import Optional, Dict, List
import uuid

# Try to import Vonage
try:
    import vonage
    VONAGE_AVAILABLE = True
except ImportError:
    VONAGE_AVAILABLE = False
    print("Warning: Vonage library not installed. Run: pip install vonage")


class VonageSMSService:
    """Service for sending SMS via Vonage (Nexmo)"""

    def __init__(self, api_key: str = None, api_secret: str = None, from_number: str = None):
        """
        Initialize Vonage SMS service

        Args:
            api_key: Vonage API Key
            api_secret: Vonage API Secret
            from_number: Default phone number to send from (or alphanumeric sender ID)
        """
        if not VONAGE_AVAILABLE:
            raise ImportError("Vonage library not installed. Run: pip install vonage")

        # Use provided credentials or fall back to environment variables
        self.api_key = api_key or os.environ.get('VONAGE_API_KEY')
        self.api_secret = api_secret or os.environ.get('VONAGE_API_SECRET')
        self.from_number = from_number or os.environ.get('VONAGE_FROM_NUMBER', 'PhishVision')

        if not all([self.api_key, self.api_secret]):
            raise ValueError(
                "Vonage credentials not provided. Set VONAGE_API_KEY and "
                "VONAGE_API_SECRET in environment or settings."
            )

        # Initialize Vonage client
        self.client = vonage.Client(key=self.api_key, secret=self.api_secret)
        self.sms = vonage.Sms(self.client)


    def send_sms(
        self,
        to_number: str,
        message: str,
        tracking_url: Optional[str] = None,
        sender_id: Optional[str] = None
    ) -> Dict:
        """
        Send an SMS message

        Args:
            to_number: Recipient phone number (E.164 format: +1234567890)
            message: SMS message body
            tracking_url: Optional tracking URL to include in message
            sender_id: Optional custom sender ID (company name or phone number)

        Returns:
            dict: {
                'success': bool,
                'message_id': str,
                'status': str,
                'error': str (if failed)
            }
        """
        try:
            # Replace tracking URL placeholder if provided
            if tracking_url:
                print(f"[VONAGE SMS] Original message: {message}")
                print(f"[VONAGE SMS] Tracking URL: {tracking_url}")
                # Support multiple placeholder formats
                message = message.replace('{{url}}', tracking_url)
                message = message.replace('{{link}}', tracking_url)
                message = message.replace('{link}', tracking_url)
                print(f"[VONAGE SMS] Final message: {message}")

            # Use custom sender_id if provided, otherwise use default
            from_identifier = sender_id if sender_id else self.from_number
            print(f"[VONAGE SMS] Sending from: {from_identifier}")
            print(f"[VONAGE SMS] Sending to: {to_number}")

            # Send SMS via Vonage
            response = self.sms.send_message({
                "from": from_identifier,
                "to": to_number,
                "text": message,
            })

            if response["messages"][0]["status"] == "0":
                return {
                    'success': True,
                    'message_id': response["messages"][0]["message-id"],
                    'status': 'sent',
                    'to': to_number,
                    'from': from_identifier,
                    'remaining_balance': response["messages"][0].get("remaining-balance"),
                    'message_price': response["messages"][0].get("message-price"),
                    'network': response["messages"][0].get("network")
                }
            else:
                return {
                    'success': False,
                    'error': response["messages"][0].get("error-text", "Unknown error"),
                    'error_code': response["messages"][0]["status"]
                }

        except Exception as e:
            print(f"[VONAGE SMS] Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


    def send_bulk_sms(
        self,
        recipients: List[Dict],
        message_template: str,
        base_tracking_url: Optional[str] = None,
        sender_id: Optional[str] = None
    ) -> Dict:
        """
        Send SMS to multiple recipients

        Args:
            recipients: List of dicts with 'phone' and optional 'tracking_token'
            message_template: SMS message with {{url}} placeholder
            base_tracking_url: Base URL for tracking (token will be appended)
            sender_id: Optional custom sender ID (company name or phone number)

        Returns:
            dict: {
                'total': int,
                'sent': int,
                'failed': int,
                'results': List[dict]
            }
        """
        results = []
        sent_count = 0
        failed_count = 0

        for recipient in recipients:
            phone = recipient.get('phone')
            tracking_token = recipient.get('tracking_token', str(uuid.uuid4())[:8])

            # Build tracking URL with unique token
            if base_tracking_url:
                tracking_url = f"{base_tracking_url}/{tracking_token}"
            else:
                tracking_url = None

            # Send SMS
            result = self.send_sms(
                to_number=phone,
                message=message_template,
                tracking_url=tracking_url,
                sender_id=sender_id
            )

            # Add recipient info to result
            result['phone'] = phone
            result['tracking_token'] = tracking_token
            results.append(result)

            if result['success']:
                sent_count += 1
            else:
                failed_count += 1

        return {
            'total': len(recipients),
            'sent': sent_count,
            'failed': failed_count,
            'results': results
        }


    @staticmethod
    def format_phone_number(phone: str, country_code: str = '+994') -> str:
        """
        Format phone number to E.164 format

        Args:
            phone: Phone number (any format)
            country_code: Country code (default: +994 for Azerbaijan)

        Returns:
            str: Formatted phone number (+994XX XXX XX XX)
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))

        # Add country code if not present
        if not phone.startswith('+'):
            if len(digits) == 9:  # Azerbaijan number without country code
                return f"{country_code}{digits}"
            elif len(digits) == 12 and digits[:3] == '994':  # With 994 prefix
                return f"+{digits}"

        return phone


    @staticmethod
    def is_vonage_available() -> bool:
        """Check if Vonage library is available"""
        return VONAGE_AVAILABLE


# Convenience function for quick SMS sending
def send_phishing_sms_vonage(
    to_number: str,
    message: str,
    tracking_url: Optional[str] = None,
    api_key: str = None,
    api_secret: str = None,
    sender_id: str = None
) -> Dict:
    """
    Quick function to send a phishing simulation SMS via Vonage

    Args:
        to_number: Recipient phone number
        message: SMS message
        tracking_url: Optional tracking URL
        api_key: Vonage API Key (or from env)
        api_secret: Vonage API Secret (or from env)
        sender_id: Sender ID (company name or phone number)

    Returns:
        dict: Send result
    """
    try:
        service = VonageSMSService(api_key, api_secret, sender_id)
        return service.send_sms(to_number, message, tracking_url, sender_id)
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

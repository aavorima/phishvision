"""
Twilio SMS Service for PhishVision
Handles SMS sending for phishing simulation campaigns
"""

import os
from datetime import datetime
from typing import Optional, Dict, List
import uuid

# Try to import Twilio
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: Twilio library not installed. Run: pip install twilio")


class TwilioSMSService:
    """Service for sending SMS via Twilio"""

    def __init__(self, account_sid: str = None, auth_token: str = None, from_number: str = None):
        """
        Initialize Twilio SMS service

        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_number: Twilio phone number to send from
        """
        if not TWILIO_AVAILABLE:
            raise ImportError("Twilio library not installed. Run: pip install twilio")

        # Use provided credentials or fall back to environment variables
        self.account_sid = account_sid or os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.environ.get('TWILIO_PHONE_NUMBER')

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError(
                "Twilio credentials not provided. Set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in environment or settings."
            )

        # Initialize Twilio client
        self.client = Client(self.account_sid, self.auth_token)


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
                'message_sid': str,
                'status': str,
                'error': str (if failed)
            }
        """
        try:
            # Replace tracking URL placeholder if provided
            if tracking_url:
                print(f"[SMS] Original message: {message}")
                print(f"[SMS] Tracking URL: {tracking_url}")
                # Support multiple placeholder formats
                message = message.replace('{{url}}', tracking_url)
                message = message.replace('{{link}}', tracking_url)
                message = message.replace('{link}', tracking_url)
                print(f"[SMS] Final message: {message}")

            # Use custom sender_id if provided, otherwise use default phone number
            from_identifier = sender_id if sender_id else self.from_number
            print(f"[SMS] Sending from: {from_identifier}")

            # Send SMS via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=from_identifier,
                to=to_number
            )

            return {
                'success': True,
                'message_sid': twilio_message.sid,
                'status': twilio_message.status,
                'to': twilio_message.to,
                'from': twilio_message.from_,
                'error_code': twilio_message.error_code,
                'error_message': twilio_message.error_message
            }

        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code,
                'error_message': e.msg
            }
        except Exception as e:
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


    def get_message_status(self, message_sid: str) -> Dict:
        """
        Get the delivery status of a sent message

        Args:
            message_sid: Twilio message SID

        Returns:
            dict: Message status details
        """
        try:
            message = self.client.messages(message_sid).fetch()

            return {
                'success': True,
                'sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated
            }

        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e)
            }


    def validate_phone_number(self, phone_number: str) -> Dict:
        """
        Validate a phone number using Twilio Lookup API

        Args:
            phone_number: Phone number to validate

        Returns:
            dict: Validation results
        """
        try:
            # Use Twilio Lookup API
            number = self.client.lookups.v1.phone_numbers(phone_number).fetch()

            return {
                'success': True,
                'valid': True,
                'phone_number': number.phone_number,
                'national_format': number.national_format,
                'country_code': number.country_code,
                'carrier': number.carrier.get('name') if number.carrier else None
            }

        except TwilioRestException as e:
            if e.code == 20404:  # Invalid phone number
                return {
                    'success': True,
                    'valid': False,
                    'error': 'Invalid phone number'
                }
            return {
                'success': False,
                'error': str(e)
            }


    @staticmethod
    def format_phone_number(phone: str, country_code: str = '+1') -> str:
        """
        Format phone number to E.164 format

        Args:
            phone: Phone number (any format)
            country_code: Country code (default: +1 for US)

        Returns:
            str: Formatted phone number (+1234567890)
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))

        # Add country code if not present
        if not phone.startswith('+'):
            if len(digits) == 10:  # US number without country code
                return f"{country_code}{digits}"
            elif len(digits) == 11 and digits[0] == '1':  # US number with 1 prefix
                return f"+{digits}"

        return phone


    @staticmethod
    def is_twilio_available() -> bool:
        """Check if Twilio library is available"""
        return TWILIO_AVAILABLE


# Convenience function for quick SMS sending
def send_phishing_sms(
    to_number: str,
    message: str,
    tracking_url: Optional[str] = None,
    account_sid: str = None,
    auth_token: str = None,
    from_number: str = None
) -> Dict:
    """
    Quick function to send a phishing simulation SMS

    Args:
        to_number: Recipient phone number
        message: SMS message
        tracking_url: Optional tracking URL
        account_sid: Twilio Account SID (or from env)
        auth_token: Twilio Auth Token (or from env)
        from_number: Twilio phone number (or from env)

    Returns:
        dict: Send result
    """
    try:
        service = TwilioSMSService(account_sid, auth_token, from_number)
        return service.send_sms(to_number, message, tracking_url)
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

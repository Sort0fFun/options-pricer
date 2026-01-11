"""
M-Pesa Daraja API integration service.
"""
import base64
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from flask import current_app


class MpesaService:
    """Service for M-Pesa Daraja API integration."""
    
    SANDBOX_URL = "https://sandbox.safaricom.co.ke"
    PRODUCTION_URL = "https://api.safaricom.co.ke"
    
    _access_token = None
    _token_expiry = None
    _app = None

    @classmethod
    def init_app(cls, app):
        """Initialize with Flask app."""
        cls._app = app

    @classmethod
    def _get_base_url(cls) -> str:
        """Get base URL based on environment."""
        env = current_app.config.get('MPESA_ENV', 'sandbox')
        return cls.PRODUCTION_URL if env == 'production' else cls.SANDBOX_URL

    @classmethod
    def _get_access_token(cls) -> str:
        """Get OAuth access token from Daraja API."""
        # Check if we have a valid cached token
        if cls._access_token and cls._token_expiry and datetime.now() < cls._token_expiry:
            return cls._access_token

        consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
        consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
        
        if not consumer_key or not consumer_secret:
            raise ValueError("M-Pesa credentials not configured. Set MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET.")

        # Create base64 encoded credentials
        credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
        
        response = requests.get(
            f"{cls._get_base_url()}/oauth/v1/generate?grant_type=client_credentials",
            headers={"Authorization": f"Basic {credentials}"},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get M-Pesa access token: {response.text}")
        
        data = response.json()
        cls._access_token = data['access_token']
        # Token expires in 1 hour, refresh after 50 minutes to be safe
        from datetime import timedelta
        cls._token_expiry = datetime.now() + timedelta(minutes=50)
        
        return cls._access_token

    @classmethod
    def _generate_password(cls, timestamp: str) -> str:
        """Generate password for STK push."""
        shortcode = current_app.config.get('MPESA_SHORTCODE')
        passkey = current_app.config.get('MPESA_PASSKEY')
        
        if not shortcode or not passkey:
            raise ValueError("M-Pesa shortcode or passkey not configured")
        
        data_to_encode = f"{shortcode}{passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode()

    @classmethod
    def initiate_stk_push(
        cls,
        phone_number: str,
        amount: float,
        account_reference: str,
        transaction_desc: str = "Wallet Top-up"
    ) -> Dict[str, Any]:
        """
        Initiate STK Push to customer's phone.
        
        Args:
            phone_number: Phone number in format 2547XXXXXXXX
            amount: Amount in KES
            account_reference: Unique reference for this transaction
            transaction_desc: Description shown to customer
            
        Returns:
            Dictionary with success status and MerchantRequestID, CheckoutRequestID, etc.
        """
        try:
            access_token = cls._get_access_token()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = cls._generate_password(timestamp)
            
            shortcode = current_app.config.get('MPESA_SHORTCODE')
            callback_url = current_app.config.get('MPESA_CALLBACK_URL')
            
            if not callback_url:
                raise ValueError("MPESA_CALLBACK_URL not configured")
            
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),  # M-Pesa expects integer
                "PartyA": phone_number,
                "PartyB": shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": account_reference[:12],  # Max 12 characters
                "TransactionDesc": transaction_desc[:13]     # Max 13 characters
            }
            
            response = requests.post(
                f"{cls._get_base_url()}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            data = response.json()
            
            if response.status_code != 200 or data.get('ResponseCode') != '0':
                error_msg = data.get('errorMessage') or data.get('ResponseDescription') or 'STK push failed'
                return {
                    'success': False,
                    'error': error_msg
                }
            
            return {
                'success': True,
                'merchant_request_id': data['MerchantRequestID'],
                'checkout_request_id': data['CheckoutRequestID'],
                'response_code': data['ResponseCode'],
                'response_description': data['ResponseDescription'],
                'customer_message': data.get('CustomerMessage', 'Please check your phone for the M-Pesa prompt')
            }
        except Exception as e:
            current_app.logger.error(f"M-Pesa STK push exception: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def query_stk_status(cls, checkout_request_id: str) -> Dict[str, Any]:
        """Query the status of an STK push transaction."""
        access_token = cls._get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = cls._generate_password(timestamp)
        shortcode = current_app.config.get('MPESA_SHORTCODE')
        
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        response = requests.post(
            f"{cls._get_base_url()}/mpesa/stkpushquery/v1/query",
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        data = response.json()
        
        return {
            'response_code': data.get('ResponseCode'),
            'response_description': data.get('ResponseDescription'),
            'result_code': data.get('ResultCode'),
            'result_desc': data.get('ResultDesc'),
            'merchant_request_id': data.get('MerchantRequestID'),
            'checkout_request_id': data.get('CheckoutRequestID')
        }

    @classmethod
    def parse_callback(cls, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse M-Pesa callback data.
        
        Returns:
            Dictionary with parsed callback information
        """
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        
        result = {
            'merchant_request_id': stk_callback.get('MerchantRequestID'),
            'checkout_request_id': stk_callback.get('CheckoutRequestID'),
            'result_code': stk_callback.get('ResultCode'),
            'result_desc': stk_callback.get('ResultDesc'),
            'success': stk_callback.get('ResultCode') == 0
        }
        
        # Parse metadata if transaction was successful
        if result['success'] and stk_callback.get('CallbackMetadata'):
            metadata = stk_callback['CallbackMetadata'].get('Item', [])
            for item in metadata:
                name = item.get('Name')
                value = item.get('Value')
                if name == 'Amount':
                    result['amount'] = float(value)
                elif name == 'MpesaReceiptNumber':
                    result['mpesa_receipt'] = value
                elif name == 'TransactionDate':
                    result['transaction_date'] = str(value)
                elif name == 'PhoneNumber':
                    result['phone_number'] = str(value)
        
        return result

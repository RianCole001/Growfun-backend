import requests
import hashlib
import hmac
from django.conf import settings
from decouple import config
import json

class KorapayService:
    """
    Korapay Payment Integration Service
    Supports: Mobile Money, Bank Transfers, Cards
    """
    
    def __init__(self):
        self.base_url = config('KORAPAY_BASE_URL', default='https://api.korapay.com/merchant/api/v1')
        self.secret_key = config('KORAPAY_SECRET_KEY', default='')
        self.public_key = config('KORAPAY_PUBLIC_KEY', default='')
        self.encryption_key = config('KORAPAY_ENCRYPTION_KEY', default='')
    
    def _get_headers(self):
        """Get request headers with authorization"""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
    
    def charge_customer(self, amount, customer_email, customer_name, reference, 
                       payment_method='mobile_money', phone_number=None, currency='NGN'):
        """
        Charge customer (for deposits)
        Payment methods: mobile_money, bank_transfer, card
        """
        url = f"{self.base_url}/charges/initialize"
        
        payload = {
            "amount": float(amount),
            "currency": currency,
            "reference": reference,
            "customer": {
                "name": customer_name,
                "email": customer_email
            },
            "notification_url": config('KORAPAY_WEBHOOK_URL', default=''),
            "redirect_url": config('FRONTEND_URL', default='http://localhost:3000') + '/payment/callback',
        }
        
        # Add payment method specific data
        if payment_method == 'mobile_money' and phone_number:
            payload['mobile_money'] = {
                'phone': phone_number,
                'provider': 'mtn'  # Can be mtn, airtel, vodafone, etc.
            }
        elif payment_method == 'bank_transfer':
            payload['bank_transfer'] = {
                'narration': f'Deposit to GrowFund - {reference}'
            }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'reference': data['data']['reference'],
                    'checkout_url': data['data'].get('checkout_url'),
                    'authorization_url': data['data'].get('authorization_url'),
                    'message': 'Payment initialized successfully'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Payment initialization failed')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Request error: {str(e)}'
            }
    
    def verify_transaction(self, reference):
        """
        Verify transaction status
        """
        url = f"{self.base_url}/charges/{reference}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                transaction_data = data['data']
                return {
                    'success': True,
                    'status': transaction_data.get('status'),
                    'amount': transaction_data.get('amount'),
                    'currency': transaction_data.get('currency'),
                    'reference': transaction_data.get('reference'),
                    'customer': transaction_data.get('customer'),
                    'paid_at': transaction_data.get('paid_at'),
                    'payment_method': transaction_data.get('payment_method')
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Verification failed')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Verification error: {str(e)}'
            }
    
    def disburse_funds(self, amount, account_number, bank_code, account_name, 
                      reference, narration, currency='NGN'):
        """
        Send money to bank account (for withdrawals)
        """
        url = f"{self.base_url}/transactions/disburse"
        
        payload = {
            "reference": reference,
            "destination": {
                "type": "bank_account",
                "amount": float(amount),
                "currency": currency,
                "narration": narration,
                "bank_account": {
                    "bank": bank_code,
                    "account": account_number,
                    "account_name": account_name
                }
            },
            "notification_url": config('KORAPAY_WEBHOOK_URL', default='')
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'reference': data['data']['reference'],
                    'status': data['data'].get('status'),
                    'message': 'Disbursement initiated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Disbursement failed')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Disbursement error: {str(e)}'
            }
    
    def disburse_mobile_money(self, amount, phone_number, provider, reference, 
                             customer_name, currency='NGN'):
        """
        Send money to mobile money account (for withdrawals)
        Providers: mtn, airtel, vodafone, etc.
        """
        url = f"{self.base_url}/transactions/disburse"
        
        payload = {
            "reference": reference,
            "destination": {
                "type": "mobile_money",
                "amount": float(amount),
                "currency": currency,
                "narration": f"Withdrawal from GrowFund",
                "mobile_money": {
                    "operator": provider,
                    "mobile_number": phone_number,
                    "customer": {
                        "name": customer_name
                    }
                }
            },
            "notification_url": config('KORAPAY_WEBHOOK_URL', default='')
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'reference': data['data']['reference'],
                    'status': data['data'].get('status'),
                    'message': 'Mobile money disbursement initiated'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Disbursement failed')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Disbursement error: {str(e)}'
            }
    
    def get_banks(self, country='NG'):
        """
        Get list of supported banks
        Countries: NG (Nigeria), GH (Ghana), KE (Kenya), etc.
        """
        url = f"{self.base_url}/misc/banks"
        params = {'countryCode': country}
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'banks': data['data']
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to fetch banks'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def resolve_bank_account(self, account_number, bank_code):
        """
        Verify bank account details
        """
        url = f"{self.base_url}/misc/banks/resolve"
        
        payload = {
            "bank": bank_code,
            "account": account_number
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'account_name': data['data'].get('account_name'),
                    'account_number': data['data'].get('account_number'),
                    'bank_code': data['data'].get('bank_code')
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Account verification failed')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Verification error: {str(e)}'
            }
    
    def verify_webhook_signature(self, payload, signature):
        """
        Verify webhook signature for security
        """
        computed_signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    
    def get_balance(self):
        """
        Get merchant balance
        """
        url = f"{self.base_url}/balances"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'balances': data['data']
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to fetch balance'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

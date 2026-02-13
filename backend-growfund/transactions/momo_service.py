import requests
import uuid
from django.conf import settings
from decouple import config
import base64
import json

class MoMoAPIService:
    """
    MTN Mobile Money API Integration Service
    Supports Collection (deposits) and Disbursement (withdrawals)
    """
    
    def __init__(self):
        self.base_url = config('MOMO_BASE_URL', default='https://sandbox.momodeveloper.mtn.com')
        self.collection_subscription_key = config('MOMO_COLLECTION_SUBSCRIPTION_KEY', default='')
        self.disbursement_subscription_key = config('MOMO_DISBURSEMENT_SUBSCRIPTION_KEY', default='')
        self.api_user = config('MOMO_API_USER', default='')
        self.api_key = config('MOMO_API_KEY', default='')
        self.callback_url = config('MOMO_CALLBACK_URL', default='')
        self.environment = config('MOMO_ENVIRONMENT', default='sandbox')
    
    def _get_access_token(self, product='collection'):
        """Get OAuth access token"""
        url = f"{self.base_url}/{product}/token/"
        
        # Create basic auth header
        credentials = f"{self.api_user}:{self.api_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Ocp-Apim-Subscription-Key': self.collection_subscription_key if product == 'collection' else self.disbursement_subscription_key,
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def request_to_pay(self, amount, phone_number, reference, description="Deposit"):
        """
        Request payment from user (Collection)
        """
        access_token = self._get_access_token('collection')
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        url = f"{self.base_url}/collection/v1_0/requesttopay"
        
        # Generate unique reference ID
        x_reference_id = str(uuid.uuid4())
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Reference-Id': x_reference_id,
            'X-Target-Environment': self.environment,
            'Ocp-Apim-Subscription-Key': self.collection_subscription_key,
            'Content-Type': 'application/json',
        }
        
        # Format phone number (remove + and spaces)
        formatted_phone = phone_number.replace('+', '').replace(' ', '')
        
        payload = {
            'amount': str(amount),
            'currency': 'EUR',  # Change to your currency (UGX, GHS, etc.)
            'externalId': reference,
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId': formatted_phone
            },
            'payerMessage': description,
            'payeeNote': f'Payment for {description}'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 202:
                return {
                    'success': True,
                    'reference_id': x_reference_id,
                    'message': 'Payment request sent successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f'Payment request failed: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Request error: {str(e)}'}
    
    def check_payment_status(self, reference_id):
        """
        Check status of payment request
        """
        access_token = self._get_access_token('collection')
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        url = f"{self.base_url}/collection/v1_0/requesttopay/{reference_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Target-Environment': self.environment,
            'Ocp-Apim-Subscription-Key': self.collection_subscription_key,
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'status': data.get('status'),
                'amount': data.get('amount'),
                'currency': data.get('currency'),
                'financial_transaction_id': data.get('financialTransactionId'),
                'external_id': data.get('externalId'),
                'reason': data.get('reason')
            }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Status check error: {str(e)}'}
    
    def transfer(self, amount, phone_number, reference, description="Withdrawal"):
        """
        Send money to user (Disbursement)
        """
        access_token = self._get_access_token('disbursement')
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        url = f"{self.base_url}/disbursement/v1_0/transfer"
        
        # Generate unique reference ID
        x_reference_id = str(uuid.uuid4())
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Reference-Id': x_reference_id,
            'X-Target-Environment': self.environment,
            'Ocp-Apim-Subscription-Key': self.disbursement_subscription_key,
            'Content-Type': 'application/json',
        }
        
        # Format phone number
        formatted_phone = phone_number.replace('+', '').replace(' ', '')
        
        payload = {
            'amount': str(amount),
            'currency': 'EUR',  # Change to your currency
            'externalId': reference,
            'payee': {
                'partyIdType': 'MSISDN',
                'partyId': formatted_phone
            },
            'payerMessage': description,
            'payeeNote': f'Withdrawal: {description}'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 202:
                return {
                    'success': True,
                    'reference_id': x_reference_id,
                    'message': 'Transfer initiated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f'Transfer failed: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Transfer error: {str(e)}'}
    
    def check_transfer_status(self, reference_id):
        """
        Check status of transfer (disbursement)
        """
        access_token = self._get_access_token('disbursement')
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        url = f"{self.base_url}/disbursement/v1_0/transfer/{reference_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Target-Environment': self.environment,
            'Ocp-Apim-Subscription-Key': self.disbursement_subscription_key,
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'status': data.get('status'),
                'amount': data.get('amount'),
                'currency': data.get('currency'),
                'financial_transaction_id': data.get('financialTransactionId'),
                'external_id': data.get('externalId'),
                'reason': data.get('reason')
            }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Status check error: {str(e)}'}
    
    def get_account_balance(self, product='collection'):
        """
        Get account balance
        """
        access_token = self._get_access_token(product)
        if not access_token:
            return {'success': False, 'message': 'Failed to get access token'}
        
        url = f"{self.base_url}/{product}/v1_0/account/balance"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Target-Environment': self.environment,
            'Ocp-Apim-Subscription-Key': self.collection_subscription_key if product == 'collection' else self.disbursement_subscription_key,
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'available_balance': data.get('availableBalance'),
                'currency': data.get('currency')
            }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Balance check error: {str(e)}'}

"""
ExpressPay Ghana Payment Integration Service
Docs: https://expresspaygh.com/api/

Flow:
  STEP 1 — POST to submit.php  → get token
  STEP 2 — Redirect user to checkout.php?token=xxx
  STEP 3 — User completes payment, expressPay redirects to redirect-url
  STEP 4a — POST to query.php  → check final status
  STEP 4b — expressPay POSTs to post-url when async payment completes
"""
import requests
import uuid
from decouple import config


SANDBOX_BASE = 'https://sandbox.expresspaygh.com/api'
LIVE_BASE    = 'https://expresspaygh.com/api'


class ExpressPayService:

    def __init__(self):
        self.merchant_id = config('EXPRESSPAY_MERCHANT_ID', default='')
        self.api_key     = config('EXPRESSPAY_API_KEY', default='')
        self.sandbox     = config('EXPRESSPAY_SANDBOX', default='True') == 'True'
        self.base_url    = SANDBOX_BASE if self.sandbox else LIVE_BASE

    # ── STEP 1: Submit ─────────────────────────────────────────────────────────
    def submit(self, amount, order_id, customer, redirect_url, post_url=None,
               currency='GHS', description='GrowFund Deposit', order_img_url=''):
        """
        Initiate a payment and obtain a token.

        customer dict: { firstname, lastname, email, phone, username, account_number }

        Returns:
          { success, token, order_id, checkout_url }   on success
          { success, status_code, message }             on failure
        """
        url = f'{self.base_url}/submit.php'

        payload = {
            'merchant-id':    self.merchant_id,
            'api-key':        self.api_key,
            'firstname':      customer.get('firstname', ''),
            'lastname':       customer.get('lastname', ''),
            'email':          customer.get('email', ''),
            'phonenumber':    customer.get('phone', ''),
            'username':       customer.get('username', customer.get('email', '')),
            'accountnumber':  customer.get('account_number', '36'),
            'currency':       currency,
            'amount':         str(amount),
            'order-id':       order_id,
            'order-desc':     description,
            'order-img-url':  order_img_url,
            'redirect-url':   redirect_url,
        }

        if post_url:
            payload['post-url'] = post_url

        try:
            resp = requests.post(
                url,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=15
            )
            data = resp.json()
        except Exception as e:
            return {'success': False, 'message': f'Network error: {e}'}

        ep_status = data.get('status')

        if ep_status == 1:
            token = data.get('token')
            return {
                'success':      True,
                'token':        token,
                'order_id':     data.get('order-id'),
                'checkout_url': f'{self.base_url}/checkout.php?token={token}',
                'message':      data.get('message', 'Success'),
            }

        # Map ExpressPay status codes to readable messages
        error_map = {
            2: 'Invalid credentials — check EXPRESSPAY_MERCHANT_ID and EXPRESSPAY_API_KEY',
            3: 'Invalid request — check required parameters',
            4: 'Invalid IP — your server IP is not whitelisted on ExpressPay',
        }
        return {
            'success':     False,
            'status_code': ep_status,
            'message':     error_map.get(ep_status, f'ExpressPay error (status {ep_status})'),
        }

    # ── STEP 4a: Query ─────────────────────────────────────────────────────────
    def query(self, token):
        """
        Check the final status of a transaction.

        Returns:
          { success, result, result_text, order_id, token,
            transaction_id, currency, amount, date_processed }

        result codes:
          1 = Approved
          2 = Declined
          3 = Error
          4 = Pending
        """
        url = f'{self.base_url}/query.php'

        payload = {
            'merchant-id': self.merchant_id,
            'api-key':     self.api_key,
            'token':       token,
        }

        try:
            resp = requests.post(
                url,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=15
            )
            data = resp.json()
        except Exception as e:
            return {'success': False, 'message': f'Network error: {e}'}

        return {
            'success':        True,
            'result':         data.get('result'),
            'result_text':    data.get('result-text', ''),
            'order_id':       data.get('order-id', ''),
            'token':          data.get('token', ''),
            'transaction_id': data.get('transaction-id', ''),
            'currency':       data.get('currency', ''),
            'amount':         data.get('amount'),
            'date_processed': data.get('date-processed', ''),
        }

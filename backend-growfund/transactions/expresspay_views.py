"""
ExpressPay Ghana — Views
Endpoints:
  POST /api/transactions/expresspay/deposit/        — STEP 1: initiate payment
  GET  /api/transactions/expresspay/callback/       — STEP 3: browser redirect after payment
  POST /api/transactions/expresspay/verify/         — STEP 4a: manual status check
  POST /api/transactions/expresspay/post-url/       — STEP 4b: async webhook from ExpressPay
"""
import uuid
from decimal import Decimal

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from decouple import config

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer
from .expresspay_service import ExpressPayService

expresspay = ExpressPayService()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def expresspay_deposit(request):
    """
    STEP 1 + 2 — Initiate an ExpressPay deposit.

    Request body:
      { amount: 50.00 }          (GHS, minimum 1.00)

    Response:
      { success, checkout_url, reference, transaction_id }

    The frontend should redirect the user to `checkout_url` to complete payment.
    """
    amount = request.data.get('amount')
    if not amount:
        return Response({'success': False, 'message': 'amount is required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = Decimal(str(amount))
    except Exception:
        return Response({'success': False, 'message': 'Invalid amount'},
                        status=status.HTTP_400_BAD_REQUEST)

    if amount < Decimal('1.00'):
        return Response({'success': False, 'message': 'Minimum deposit is GHS 1.00'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Unique order ID for this transaction
    order_id = f"DEP-{uuid.uuid4().hex[:12].upper()}"

    # URLs ExpressPay will use
    frontend_url  = config('FRONTEND_URL', default='https://dashboard-yfb8.onrender.com')
    backend_url   = config('BACKEND_URL',  default='https://growfun-backend.onrender.com')
    redirect_url  = f"{frontend_url}/payment/callback"
    post_url      = f"{backend_url}/api/transactions/expresspay/post-url/"

    customer = {
        'firstname':      request.user.first_name or 'Customer',
        'lastname':       request.user.last_name  or 'User',
        'email':          request.user.email,
        'phone':          request.user.phone or '',
        'username':       request.user.email,
        'account_number': str(request.user.id)[:3],  # max 3 chars per API spec
    }

    result = expresspay.submit(
        amount=amount,
        order_id=order_id,
        customer=customer,
        redirect_url=redirect_url,
        post_url=post_url,
        currency='GHS',
        description='GrowFund Deposit',
    )

    if not result['success']:
        return Response({'success': False, 'message': result['message']},
                        status=status.HTTP_400_BAD_REQUEST)

    # Persist the pending transaction
    txn = Transaction.objects.create(
        user=request.user,
        transaction_type='deposit',
        payment_method='card',
        amount=amount,
        fee=Decimal('0'),
        net_amount=amount,
        status='pending',
        reference=order_id,
        external_reference=result['token'],
        description=f'ExpressPay deposit of GHS {amount}',
        metadata={
            'token':        result['token'],
            'checkout_url': result['checkout_url'],
            'gateway':      'expresspay',
        }
    )

    return Response({
        'success':        True,
        'message':        'Payment initiated. Redirect user to checkout_url.',
        'checkout_url':   result['checkout_url'],
        'reference':      order_id,
        'transaction_id': txn.id,
        'amount':         str(amount),
        'currency':       'GHS',
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expresspay_callback(request):
    """
    STEP 3 — Browser redirect after payment.
    ExpressPay appends ?order-id=xxx&token=xxx to the redirect-url.
    We immediately query the status and return the result.

    The frontend lands here after the user completes (or cancels) payment.
    """
    order_id = request.query_params.get('order-id')
    token    = request.query_params.get('token')

    if not order_id or not token:
        return Response({'success': False, 'message': 'Missing order-id or token'},
                        status=status.HTTP_400_BAD_REQUEST)

    return _settle_transaction(token=token, order_id=order_id, user=request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def expresspay_verify(request):
    """
    STEP 4a — Manual status check.
    Useful if the user returns to the app and wants to confirm their payment.

    Request body: { token: "..." }  OR  { reference: "DEP-..." }
    """
    token     = request.data.get('token')
    reference = request.data.get('reference')

    if not token and not reference:
        return Response({'success': False, 'message': 'Provide token or reference'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Look up the transaction to get the token if only reference was given
    if not token:
        try:
            txn = Transaction.objects.get(reference=reference, user=request.user)
            token = txn.metadata.get('token') or txn.external_reference
        except Transaction.DoesNotExist:
            return Response({'success': False, 'message': 'Transaction not found'},
                            status=status.HTTP_404_NOT_FOUND)

    return _settle_transaction(token=token, user=request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def expresspay_post_url(request):
    """
    STEP 4b — Async webhook from ExpressPay.
    Called by ExpressPay when a mobile-money payment completes asynchronously.
    Per the docs: query the status, update local state, return HTTP 200 immediately.

    Request body (form-encoded): { order-id, token }
    """
    order_id = request.data.get('order-id')
    token    = request.data.get('token')

    if not token:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the token exists in our DB before querying ExpressPay
    # This prevents arbitrary tokens being submitted to trigger queries
    from .models import Transaction
    token_exists = Transaction.objects.filter(
        external_reference=token
    ).exists() or Transaction.objects.filter(
        metadata__token=token
    ).exists()

    if not token_exists:
        # Return 200 to prevent ExpressPay from retrying, but don't process
        return Response({'success': True}, status=status.HTTP_200_OK)

    # Settle without a user context (webhook is server-to-server)
    _settle_transaction(token=token, order_id=order_id, user=None)

    # ExpressPay requires HTTP 200 immediately
    return Response({'success': True}, status=status.HTTP_200_OK)


# ── Shared settlement logic ────────────────────────────────────────────────────

def _settle_transaction(token, order_id=None, user=None):
    """
    Query ExpressPay for the final status of a transaction and update the DB.
    Returns a DRF Response.
    """
    query_result = expresspay.query(token)

    if not query_result['success']:
        return Response({'success': False, 'message': query_result.get('message', 'Query failed')},
                        status=status.HTTP_502_BAD_GATEWAY)

    ep_result = query_result['result']

    # Find the transaction by token (stored in external_reference or metadata)
    txn = None
    try:
        if order_id:
            txn = Transaction.objects.get(reference=order_id)
        else:
            txn = Transaction.objects.get(external_reference=token)
    except Transaction.DoesNotExist:
        pass

    if txn is None:
        return Response({'success': False, 'message': 'Transaction record not found'},
                        status=status.HTTP_404_NOT_FOUND)

    # Ensure the requesting user owns this transaction (skip check for webhook)
    if user and txn.user != user:
        return Response({'success': False, 'message': 'Unauthorized'},
                        status=status.HTTP_403_FORBIDDEN)

    result_map = {1: 'approved', 2: 'declined', 3: 'error', 4: 'pending'}
    ep_status_text = result_map.get(ep_result, 'unknown')

    if ep_result == 1 and txn.status != 'completed':
        # Payment approved — credit the user
        txn.status = 'completed'
        txn.completed_at = timezone.now()
        txn.metadata['expresspay_transaction_id'] = query_result.get('transaction_id')
        txn.save()

        txn.user.balance += txn.amount
        txn.user.save(update_fields=['balance'])

        # Notification
        try:
            from notifications.models import Notification
            Notification.create_notification(
                user=txn.user,
                title='Deposit Successful',
                message=f'Your deposit of GHS {txn.amount} has been confirmed.',
                notification_type='success'
            )
        except Exception:
            pass

    elif ep_result == 2 and txn.status not in ('failed', 'completed'):
        txn.status = 'failed'
        txn.save()

    elif ep_result == 4 and txn.status == 'pending':
        # Still pending — no change needed
        pass

    return Response({
        'success':        True,
        'status':         ep_status_text,
        'result_code':    ep_result,
        'result_text':    query_result.get('result_text', ''),
        'transaction':    TransactionSerializer(txn).data,
        'amount':         query_result.get('amount'),
        'currency':       query_result.get('currency'),
        'date_processed': query_result.get('date_processed'),
    }, status=status.HTTP_200_OK)

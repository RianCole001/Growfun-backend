from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .usdt_models import USDTDepositRequest


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_usdt_deposit(request):
    base_amount = float(request.data.get('amount', 0))
    if base_amount < 30:
        return Response({'error': 'Minimum deposit is $30'}, status=400)

    deposit = USDTDepositRequest.objects.create(
        user=request.user,
        base_amount=Decimal(str(base_amount)),
        expected_amount=Decimal(str(base_amount)),
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    return Response({
        'deposit_id': str(deposit.id),
        'wallet_address': deposit.wallet_address,
        'amount_to_send': str(deposit.base_amount),
        'expires_at': deposit.expires_at.isoformat(),
        'network': 'TRC20 (Tron)',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_deposit_status(request, deposit_id):
    try:
        deposit = USDTDepositRequest.objects.get(id=deposit_id, user=request.user)
        return Response({
            'status': deposit.status,
            'tx_hash': deposit.tx_hash,
            'amount': str(deposit.base_amount),
            'confirmed_at': deposit.confirmed_at.isoformat() if deposit.confirmed_at else None,
        })
    except USDTDepositRequest.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

import logging
from decimal import Decimal
import requests
from django.utils import timezone
from django.db import transaction as db_transaction
from django.conf import settings

logger = logging.getLogger(__name__)

TRONGRID_URL = 'https://api.trongrid.io/v1/accounts/{address}/transactions/trc20'
USDT_CONTRACT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'
PLATFORM_WALLET = getattr(settings, 'USDT_WALLET_ADDRESS', 'TNGbuN1FPWJDsxd9wtoyoAqeRvCVuPuDXm')
TRONGRID_API_KEY = getattr(settings, 'TRONGRID_API_KEY', '')


def fetch_recent_trc20_transactions(limit=100):
    url = TRONGRID_URL.format(address=PLATFORM_WALLET)
    headers = {}
    if TRONGRID_API_KEY:
        headers['TRON-PRO-API-KEY'] = TRONGRID_API_KEY
    try:
        resp = requests.get(url, params={
            'limit': limit,
            'contract_address': USDT_CONTRACT,
            'only_to': 'true',
        }, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get('data', [])
    except Exception as e:
        logger.error(f'TronGrid fetch failed: {e}')
        return []


def process_usdt_deposits():
    from .usdt_models import USDTDepositRequest
    from .models import Transaction

    # Expire old pending deposits
    USDTDepositRequest.objects.filter(
        status='pending',
        expires_at__lt=timezone.now()
    ).update(status='expired')

    pending = USDTDepositRequest.objects.filter(status='pending').select_related('user')
    if not pending.exists():
        return

    transactions = fetch_recent_trc20_transactions()
    if not transactions:
        return

    for tx in transactions:
        try:
            if tx.get('token_info', {}).get('address') != USDT_CONTRACT:
                continue

            tx_hash = tx.get('transaction_id')
            to_address = tx.get('to')
            raw_value = tx.get('value', '0')
            amount = Decimal(raw_value) / Decimal('1000000')

            if to_address != PLATFORM_WALLET:
                continue

            if USDTDepositRequest.objects.filter(tx_hash=tx_hash).exists():
                continue

            matched = None
            for deposit in pending:
                if abs(deposit.expected_amount - amount) <= Decimal('0.02'):
                    matched = deposit
                    break

            if not matched:
                continue

            with db_transaction.atomic():
                matched.status = 'confirmed'
                matched.tx_hash = tx_hash
                matched.confirmed_at = timezone.now()
                matched.save()

                user = matched.user
                user.balance += matched.base_amount
                user.save(update_fields=['balance'])

                import uuid as _uuid
                Transaction.objects.create(
                    user=user,
                    transaction_type='deposit',
                    payment_method='bank',
                    amount=matched.base_amount,
                    net_amount=matched.base_amount,
                    status='completed',
                    reference=str(_uuid.uuid4()),
                    description=f'USDT TRC20 deposit confirmed (tx: {tx_hash[:16]}...)',
                    completed_at=timezone.now(),
                )

                try:
                    from notifications.models import Notification
                    Notification.objects.create(
                        user=user,
                        title='Deposit Confirmed',
                        message=f'Your USDT deposit of ${matched.base_amount} has been confirmed.',
                        notification_type='success',
                    )
                except Exception:
                    pass

                logger.info(f'USDT deposit confirmed: {user.email} ${matched.base_amount}')

        except Exception as e:
            logger.error(f'Error processing tx: {e}')
            continue

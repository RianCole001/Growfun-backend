import logging
import uuid as _uuid
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
AMOUNT_TOLERANCE = Decimal('5.00')  # ±$5 tolerance


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

    # Get pending deposits ordered oldest first (first-come-first-served)
    pending = list(
        USDTDepositRequest.objects.filter(status='pending')
        .select_related('user')
        .order_by('created_at')
    )
    if not pending:
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
            # USDT has 6 decimals on Tron
            received_amount = Decimal(raw_value) / Decimal('1000000')

            if to_address != PLATFORM_WALLET:
                continue

            # Skip already processed
            if USDTDepositRequest.objects.filter(tx_hash=tx_hash).exists():
                continue

            # Skip if below minimum
            if received_amount < Decimal('30'):
                continue

            # Match: oldest pending deposit within ±$5 tolerance
            matched = None
            for deposit in pending:
                if abs(deposit.expected_amount - received_amount) <= AMOUNT_TOLERANCE:
                    matched = deposit
                    break

            # If no close match, assign to oldest pending deposit
            # that hasn't been matched yet (any amount >= 30)
            if not matched and pending:
                matched = pending[0]

            if not matched:
                continue

            with db_transaction.atomic():
                matched.status = 'confirmed'
                matched.tx_hash = tx_hash
                matched.confirmed_at = timezone.now()
                matched.save()

                # Remove from pending list so it can't be matched again
                pending.remove(matched)

                # Credit actual received amount
                user = matched.user
                user.balance += received_amount
                user.save(update_fields=['balance'])

                Transaction.objects.create(
                    user=user,
                    transaction_type='deposit',
                    payment_method='bank',
                    amount=received_amount,
                    net_amount=received_amount,
                    status='completed',
                    reference=str(_uuid.uuid4()),
                    description=f'USDT TRC20 deposit (tx: {tx_hash[:16]}...)',
                    completed_at=timezone.now(),
                )

                try:
                    from notifications.models import Notification
                    Notification.create_notification(
                        user=user,
                        title='Deposit Confirmed',
                        message=f'Your USDT deposit of ${received_amount} has been confirmed and credited.',
                        notification_type='success',
                    )
                except Exception:
                    pass

                logger.info(f'USDT confirmed: {user.email} ${received_amount} tx:{tx_hash}')

        except Exception as e:
            logger.error(f'Error processing tx: {e}')
            continue

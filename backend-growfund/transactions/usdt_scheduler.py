"""
Lightweight in-process USDT deposit checker.
Runs in a background thread, triggered on app startup.
Checks every 60 seconds without needing Celery or a cron job.
"""
import threading
import time
import logging

logger = logging.getLogger(__name__)

_thread = None
_running = False


def _run_loop():
    global _running
    logger.info('USDT deposit checker started')
    while _running:
        try:
            from .tron_monitor import process_usdt_deposits
            process_usdt_deposits()
        except Exception as e:
            logger.error(f'USDT checker error: {e}')
        time.sleep(60)


def start():
    global _thread, _running
    if _thread and _thread.is_alive():
        return
    _running = True
    _thread = threading.Thread(target=_run_loop, daemon=True, name='usdt-checker')
    _thread.start()


def stop():
    global _running
    _running = False

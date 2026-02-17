# Gunicorn configuration optimized for Render - SIMPLIFIED
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker processes - simplified for stability
workers = 1
worker_class = "sync"
timeout = 120  # Increased timeout
keepalive = 2

# Memory management - less aggressive
max_requests = 0  # Disable worker recycling temporarily
preload_app = False  # Disable preloading to avoid issues

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"  # More verbose logging to debug issues

# Process naming
proc_name = 'growfund_backend'
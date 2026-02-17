# Gunicorn configuration optimized for Render's memory limits
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes - optimized for memory
workers = 1  # Reduced from default to save memory
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Memory management
max_requests = 1000  # Restart workers after 1000 requests to prevent memory leaks
max_requests_jitter = 50
preload_app = True  # Load app before forking workers to save memory

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "warning"  # Reduce log verbosity
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'growfund_backend'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Memory optimization
worker_tmp_dir = '/dev/shm'  # Use memory for temporary files if available
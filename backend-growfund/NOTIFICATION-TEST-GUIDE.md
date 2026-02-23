# Notification System Test Guide

## Issue: Admin notifications not reflecting to users

## Testing Steps:

### 1. Test Admin Notification Creation
```bash
# Test admin notification endpoint
curl -X POST http://localhost:8000/api/notifications/admin/send/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "message": "This is a test notification from admin",
    "type": "info",
    "priority": "normal",
    "target": "all"
  }'
```

### 2. Test User Notification Retrieval
```bash
# Test user notification endpoint
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Check Database
```sql
-- Check if admin notifications are created
SELECT * FROM notifications_adminnotification ORDER BY created_at DESC LIMIT 5;

-- Check if user notifications are created
SELECT * FROM notifications_notification ORDER BY created_at DESC LIMIT 10;
```

### 4. Frontend Test
1. Login as admin
2. Go to Admin Notifications
3. Create a test notification with target "all"
4. Login as regular user
5. Check if notification appears in user dashboard

## Common Issues:

### Issue 1: Admin Token Not Valid
- Check if admin user has `is_staff=True` or `is_superuser=True`
- Verify token is not expired

### Issue 2: User Not Receiving Notifications
- Check if user is `is_active=True`
- Verify notification creation logic in `admin_send_notification`

### Issue 3: Frontend Not Showing Notifications
- Check if user notification API endpoint is called
- Verify notification component is properly connected

## Debug Commands:

```python
# Django shell debug
python manage.py shell

from django.contrib.auth import get_user_model
from notifications.models import Notification, AdminNotification

User = get_user_model()

# Check admin user
admin = User.objects.filter(is_staff=True).first()
print(f"Admin: {admin.email if admin else 'No admin found'}")

# Check regular users
users = User.objects.filter(is_active=True, is_staff=False)[:5]
print(f"Active users: {[u.email for u in users]}")

# Check recent notifications
recent_notifications = Notification.objects.all()[:10]
for n in recent_notifications:
    print(f"{n.user.email}: {n.title}")

# Check admin notifications
admin_notifications = AdminNotification.objects.all()[:5]
for an in admin_notifications:
    print(f"Admin notification: {an.title} - sent to {an.sent_count} users")
```

## Expected Flow:
1. Admin creates notification via `/api/notifications/admin/send/`
2. Backend creates `AdminNotification` record
3. Backend creates individual `Notification` records for each target user
4. Users fetch notifications via `/api/notifications/`
5. Frontend displays notifications in user dashboard
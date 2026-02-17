# 🧪 Admin Testing Guide - Delete & Suspend

## 🎯 **Quick Test Steps**

### **1. Test Admin Delete Function**

**Debug Endpoint (with detailed logging):**
```bash
# Test delete user with ID 11
curl -X POST "https://growfun-backend.onrender.com/api/auth/debug/admin/users/11/delete/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Original Endpoint:**
```bash
# Test delete user with ID 11
curl -X DELETE "https://growfun-backend.onrender.com/api/auth/admin/users/11/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### **2. Test Admin Suspend Function**

**Debug Endpoint (with detailed logging):**
```bash
# Test suspend user with ID 11
curl -X POST "https://growfun-backend.onrender.com/api/auth/debug/admin/users/11/suspend/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "suspend"}'

# Test unsuspend user with ID 11
curl -X POST "https://growfun-backend.onrender.com/api/auth/debug/admin/users/11/suspend/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "unsuspend"}'
```

**Original Endpoint:**
```bash
# Test suspend user with ID 11
curl -X POST "https://growfun-backend.onrender.com/api/auth/admin/users/11/suspend/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "suspend"}'
```

### **3. Get Your Admin Token**

**Login as admin:**
```bash
curl -X POST "https://growfun-backend.onrender.com/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@growfund.com",
    "password": "Admin123!"
  }'
```

Copy the `access` token from the response.

### **4. List Suspended Users**

```bash
curl -X GET "https://growfun-backend.onrender.com/api/auth/admin/users/suspended/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 🔍 **What to Look For**

### **Successful Delete Response:**
```json
{
  "success": true,
  "message": "User user@example.com deleted successfully",
  "debug": {
    "user_id": 11,
    "original_email": "user@example.com",
    "new_email": "deleted_11_user@example.com",
    "is_active": false
  }
}
```

### **Successful Suspend Response:**
```json
{
  "success": true,
  "message": "User user@example.com suspended successfully",
  "debug": {
    "user_id": 11,
    "email": "user@example.com",
    "action": "suspend",
    "original_status": true,
    "new_status": false
  }
}
```

### **Error Responses:**
```json
{
  "error": "Admin access required"
}
```
```json
{
  "error": "User not found"
}
```
```json
{
  "error": "Cannot delete your own account"
}
```

## 🐛 **Debugging Steps**

### **1. Check Server Logs**
If using the debug endpoints, check your server console for detailed logs:
- `🔧 DEBUG: Admin delete called for user 11`
- `✅ DEBUG: Found user user@example.com`
- `✅ DEBUG: User soft deleted successfully`

### **2. Verify Admin Permissions**
Make sure your admin user has the right permissions:
```bash
# Check admin user status
curl -X GET "https://growfun-backend.onrender.com/api/auth/me/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Should return:
```json
{
  "is_staff": true,
  "is_superuser": true
}
```

### **3. Test with Different User IDs**
Try with different user IDs to see if it's user-specific:
```bash
# List all users first
curl -X GET "https://growfun-backend.onrender.com/api/auth/admin/users/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### **4. Check Database State**
After operations, verify the changes:
```bash
# Check if user is in suspended list
curl -X GET "https://growfun-backend.onrender.com/api/auth/admin/users/suspended/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 🔧 **Common Issues & Solutions**

### **Issue: "Admin access required"**
**Solution:** 
- Verify your token is valid
- Check if admin user has `is_staff=True` or `is_superuser=True`

### **Issue: "User not found"**
**Solution:**
- Check if the user ID exists
- User might already be deleted (soft deleted)

### **Issue: "Cannot delete your own account"**
**Solution:**
- This is a safety feature
- Use a different user ID, not your own admin account

### **Issue: 500 Internal Server Error**
**Solution:**
- Check server logs for detailed error
- Use debug endpoints to see exact error message

## 🎯 **Expected Behavior**

### **Delete Function:**
- ✅ Sets `is_active = False` (soft delete)
- ✅ Changes email to `deleted_{id}_{original_email}`
- ✅ Preserves all user data and relationships
- ✅ Creates notification for admin

### **Suspend Function:**
- ✅ Sets `is_active = False` for suspend
- ✅ Sets `is_active = True` for unsuspend
- ✅ Keeps original email unchanged
- ✅ Creates notifications for admin and user

### **List Suspended:**
- ✅ Shows all users with `is_active = False`
- ✅ Includes both suspended and deleted users
- ✅ Ordered by registration date

## 📞 **If Still Not Working**

### **1. Try Debug Endpoints First**
The debug endpoints provide detailed logging and error information.

### **2. Check Frontend Code**
Make sure your frontend is:
- Sending correct HTTP method (DELETE for delete, POST for suspend)
- Including proper Authorization header
- Sending correct JSON data for suspend

### **3. Test Locally**
Run the server locally and test:
```bash
py manage.py runserver --settings=growfund.minimal_settings
```

Then test with `http://localhost:8000` instead of the Render URL.

---

**The admin functions should work now. Use the debug endpoints to get detailed information about any issues!** 🚀
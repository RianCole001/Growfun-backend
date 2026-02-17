// FRONTEND NOTIFICATION INTEGRATION
// Replace the TODO comments in your AdminNotifications.js with these API calls

// 1. FETCH NOTIFICATIONS - Replace fetchNotifications function
const fetchNotifications = async () => {
  try {
    setLoading(true);
    
    // Get admin token from localStorage or your auth context
    const token = localStorage.getItem('adminToken') || localStorage.getItem('token');
    
    const response = await fetch('https://growfun-backend.onrender.com/api/notifications/admin/notifications/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const result = await response.json();
    
    if (result.success) {
      setNotifications(result.data);
    } else {
      throw new Error(result.error || 'Failed to fetch notifications');
    }
  } catch (error) {
    console.error('Error fetching notifications:', error);
    toast.error('Failed to load notifications');
  } finally {
    setLoading(false);
  }
};

// 2. CREATE NOTIFICATION - Replace handleCreateNotification function
const handleCreateNotification = async () => {
  if (!newNotification.title.trim() || !newNotification.message.trim()) {
    toast.error('Title and message are required');
    return;
  }

  try {
    setLoading(true);
    
    // Get admin token
    const token = localStorage.getItem('adminToken') || localStorage.getItem('token');
    
    // Prepare request body to match backend format
    const requestBody = {
      title: newNotification.title,
      message: newNotification.message,
      type: newNotification.type,
      priority: newNotification.priority,
      target: newNotification.target,
      target_users: newNotification.target === 'specific_users' ? newNotification.targetUsers : ''
    };

    const response = await fetch('https://growfun-backend.onrender.com/api/notifications/admin/send/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    const result = await response.json();
    
    if (result.success) {
      // Add new notification to the list
      setNotifications([result.data, ...notifications]);
      setShowCreateModal(false);
      setNewNotification({
        title: '',
        message: '',
        type: 'info',
        target: 'all',
        targetUsers: '',
        priority: 'normal'
      });
      toast.success(`Notification sent to ${result.data.sent_count} users!`);
    } else {
      throw new Error(result.error || 'Failed to send notification');
    }
  } catch (error) {
    console.error('Error creating notification:', error);
    toast.error('Failed to send notification');
  } finally {
    setLoading(false);
  }
};

// 3. DELETE NOTIFICATION - Replace handleDeleteNotification function
const handleDeleteNotification = async (id) => {
  if (!window.confirm('Are you sure you want to delete this notification?')) return;

  try {
    // Get admin token
    const token = localStorage.getItem('adminToken') || localStorage.getItem('token');
    
    const response = await fetch(`https://growfun-backend.onrender.com/api/notifications/admin/notifications/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const result = await response.json();
    
    if (result.success) {
      setNotifications(notifications.filter(n => n.id !== id));
      toast.success('Notification deleted');
    } else {
      throw new Error(result.error || 'Failed to delete notification');
    }
  } catch (error) {
    console.error('Error deleting notification:', error);
    toast.error('Failed to delete notification');
  }
};

// 4. AXIOS VERSION (if you prefer using axios)
import axios from 'axios';

// Create axios instance with base URL
const adminAPI = axios.create({
  baseURL: 'https://growfun-backend.onrender.com/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
adminAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken') || localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// AXIOS FUNCTIONS
const fetchNotificationsAxios = async () => {
  try {
    setLoading(true);
    const response = await adminAPI.get('/notifications/admin/notifications/');
    setNotifications(response.data.data);
  } catch (error) {
    console.error('Error fetching notifications:', error);
    toast.error('Failed to load notifications');
  } finally {
    setLoading(false);
  }
};

const handleCreateNotificationAxios = async () => {
  if (!newNotification.title.trim() || !newNotification.message.trim()) {
    toast.error('Title and message are required');
    return;
  }

  try {
    setLoading(true);
    
    const requestBody = {
      title: newNotification.title,
      message: newNotification.message,
      type: newNotification.type,
      priority: newNotification.priority,
      target: newNotification.target,
      target_users: newNotification.target === 'specific_users' ? newNotification.targetUsers : ''
    };

    const response = await adminAPI.post('/notifications/admin/send/', requestBody);
    
    setNotifications([response.data.data, ...notifications]);
    setShowCreateModal(false);
    setNewNotification({
      title: '',
      message: '',
      type: 'info',
      target: 'all',
      targetUsers: '',
      priority: 'normal'
    });
    toast.success(`Notification sent to ${response.data.data.sent_count} users!`);
  } catch (error) {
    console.error('Error creating notification:', error);
    toast.error('Failed to send notification');
  } finally {
    setLoading(false);
  }
};

const handleDeleteNotificationAxios = async (id) => {
  if (!window.confirm('Are you sure you want to delete this notification?')) return;

  try {
    await adminAPI.delete(`/notifications/admin/notifications/${id}/`);
    setNotifications(notifications.filter(n => n.id !== id));
    toast.success('Notification deleted');
  } catch (error) {
    console.error('Error deleting notification:', error);
    toast.error('Failed to delete notification');
  }
};

// 5. TESTING THE ENDPOINTS
// You can test these endpoints directly in browser console or Postman:

/*
// Test 1: Get notifications (GET)
fetch('https://growfun-backend.onrender.com/api/notifications/admin/notifications/', {
  headers: { 'Authorization': 'Bearer YOUR_ADMIN_TOKEN' }
})
.then(r => r.json())
.then(console.log);

// Test 2: Send notification (POST)
fetch('https://growfun-backend.onrender.com/api/notifications/admin/send/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_ADMIN_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Test Notification',
    message: 'This is a test notification from admin',
    type: 'info',
    priority: 'normal',
    target: 'all'
  })
})
.then(r => r.json())
.then(console.log);

// Test 3: Delete notification (DELETE)
fetch('https://growfun-backend.onrender.com/api/notifications/admin/notifications/1/', {
  method: 'DELETE',
  headers: { 'Authorization': 'Bearer YOUR_ADMIN_TOKEN' }
})
.then(r => r.json())
.then(console.log);
*/

// 6. BACKEND RESPONSE FORMATS
/*
GET /api/notifications/admin/notifications/ Response:
{
  "data": [
    {
      "id": 1,
      "title": "Welcome to GrowFund",
      "message": "Thank you for joining...",
      "type": "success",
      "priority": "normal",
      "target": "all",
      "sent_count": 156,
      "created_at": "2026-02-17T10:30:00Z",
      "status": "sent"
    }
  ],
  "success": true
}

POST /api/notifications/admin/send/ Response:
{
  "data": {
    "id": 1,
    "title": "Welcome to GrowFund",
    "message": "Thank you for joining...",
    "type": "success",
    "priority": "normal",
    "target": "all",
    "sent_count": 156,
    "created_at": "2026-02-17T10:30:00Z",
    "status": "sent"
  },
  "success": true
}

DELETE /api/notifications/admin/notifications/{id}/ Response:
{
  "data": {
    "message": "Notification deleted"
  },
  "success": true
}
*/
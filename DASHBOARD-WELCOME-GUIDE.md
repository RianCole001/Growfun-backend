# Dashboard Welcome Message Guide

## What You'll See

When you log in to your GrowFund account, the dashboard will now greet you by name:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Welcome Back, John Doe!                               │
│  Here's an overview of your portfolio journey          │
│                                                         │
│  [Investments] [Balance] [Profile]                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## How Your Name Gets There

### Step 1: Registration
You enter your name when registering:
- First Name: John
- Last Name: Doe

### Step 2: Login
When you login, the backend sends your name back

### Step 3: Dashboard
The dashboard displays: "Welcome Back, John Doe!"

## Name Display Rules

| Scenario | Display |
|----------|---------|
| Full name available | "Welcome Back, John Doe!" |
| Only email available | "Welcome Back, john@example.com!" |
| No name data | "Welcome Back, User!" |

## Testing Your Welcome Message

### Test 1: Register with Full Name
1. Go to `http://localhost:3000/register`
2. Enter:
   - First Name: `John`
   - Last Name: `Doe`
   - Email: `john@example.com`
   - Password: `Test123!`
3. Complete registration
4. Verify email
5. Login
6. Check dashboard - should show "Welcome Back, John Doe!"

### Test 2: Update Your Name
1. Login to dashboard
2. Go to Profile page
3. Edit your name
4. Save changes
5. Go back to Dashboard
6. Name should update in welcome message

### Test 3: Logout and Login Again
1. Click logout
2. Login again
3. Dashboard should still show your name

## Customizing Your Name

To change your name:

1. Click on **Profile** in the navigation
2. Click **Edit** button
3. Update your name fields
4. Click **Save Changes**
5. Go back to Dashboard
6. Welcome message will show your new name

## Technical Details

### Data Flow
```
User Registration
    ↓
Backend stores: first_name, last_name
    ↓
User Login
    ↓
Backend returns: first_name, last_name
    ↓
Frontend stores in profile state
    ↓
Dashboard displays: "Welcome Back, {first_name} {last_name}!"
```

### API Response
When you login, the backend returns:
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe"
  }
}
```

## Troubleshooting

### Issue: Welcome message shows "User" instead of name

**Cause**: Name wasn't captured during registration

**Solution**:
1. Go to Profile page
2. Click Edit
3. Enter your first and last name
4. Click Save
5. Go back to Dashboard
6. Name should now display

### Issue: Name doesn't update after editing profile

**Cause**: Page needs to refresh

**Solution**:
1. After saving profile changes
2. Refresh the page (F5)
3. Or navigate away and back to Dashboard
4. Name should update

### Issue: Name shows email instead of full name

**Cause**: First/last name not set

**Solution**:
1. Go to Profile
2. Click Edit
3. Fill in First Name and Last Name
4. Save changes
5. Dashboard will show full name

## Features

✅ Personalized greeting with your name
✅ Name updates when you edit profile
✅ Persists across sessions
✅ Fallback to email if name not available
✅ Mobile responsive

## Next Steps

- Update your profile with complete information
- Add a profile picture
- Set your preferences
- Start investing!

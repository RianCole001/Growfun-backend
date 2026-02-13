# Admin User Actions - Quick Reference

## Action Buttons (in order)

| Icon | Color | Action | What It Does |
|------|-------|--------|-------------|
| 👁️ | Blue | View | Opens modal with user details |
| ✓/✗ | Green/Yellow | Verify | Toggle email verification status |
| 🔒 | Orange | Suspend | Lock user account (prevents login) |
| ⚠️ | Purple | Reset Password | Set new password for user |
| 🗑️ | Red | Delete | Permanently delete user account |

## How to Use Each Action

### 1. View User Details
```
Click: Eye icon (Blue)
Result: Modal shows name, email, status, balance, join date
```

### 2. Verify/Unverify User
```
Click: Check/X icon (Green/Yellow)
Result: Toggles verification status
- Green ✓ = Verified (click to unverify)
- Yellow ✗ = Unverified (click to verify)
```

### 3. Suspend User
```
Click: Lock icon (Orange)
Confirm: Click OK in confirmation dialog
Result: User account is locked (cannot login)
```

### 4. Reset Password
```
Click: Alert icon (Purple)
Enter: New password (minimum 8 characters)
Click: Reset button
Result: User password is changed
```

### 5. Delete User
```
Click: Trash icon (Red)
Confirm: Click OK in confirmation dialog (warns: cannot undo)
Result: User account is permanently deleted
```

## Search & Filter

**Search**: Type user name or email in search box
**Filter**: Click status buttons (All, Active, Pending, Suspended)

## Stats at Bottom

- **Total Users**: Count of all users
- **Active Users**: Users with verified email
- **Pending Verification**: Users without verified email

## Keyboard Shortcuts

- **Refresh**: Click "↻ Refresh" button to reload user list
- **Add User**: Click "+ Add User" button (coming soon)

## Common Tasks

### Task: Verify a New User
1. Find user in list (search if needed)
2. Click yellow ✗ icon
3. Status changes to green ✓
4. User can now access platform

### Task: Unlock a Suspended User
1. Find user in list
2. Click lock icon again
3. User account is unsuspended
4. User can login again

### Task: Help User Who Forgot Password
1. Find user in list
2. Click alert icon (⚠️)
3. Enter temporary password
4. Click Reset
5. Tell user new password

### Task: Remove Problematic User
1. Find user in list
2. Click trash icon (🗑️)
3. Confirm deletion
4. User account is removed

## Tips

✅ **Always confirm** before suspending or deleting
✅ **Use search** to find users quickly
✅ **Check status** before taking action
✅ **Refresh** if list seems outdated
✅ **Use strong passwords** when resetting

## Troubleshooting

**Action not working?**
- Check if you're logged in as admin
- Try refreshing the page
- Check browser console for errors

**User not updating?**
- Click Refresh button
- Wait a moment and try again
- Check if user exists

**Password reset failed?**
- Password must be at least 8 characters
- Try a different password
- Check if user still exists

---

**Quick Start**: Login as admin → Go to Users tab → Click action buttons

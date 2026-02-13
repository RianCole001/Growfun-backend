# User Profile - Quick Reference Guide

## Profile Fields & Database Mapping

### What Gets Saved to Database

| What You Edit | Saved As | Where |
|---------------|----------|-------|
| Full Name | first_name + last_name | User table |
| Email | email | User table |
| Phone | phone | User table |
| Location | location | User table |
| Occupation | occupation | User table |
| Company | company | User table |
| Website | website | User table |
| Bio | bio | User table |
| Profile Picture | avatar | avatars/ folder |

## How to Update Profile

### Step 1: Open Profile
- Click "Profile" in navigation menu
- See all your current information

### Step 2: Click Edit
- Click blue "Edit" button
- Form fields become editable

### Step 3: Make Changes
- Edit any field you want to change
- All fields are optional except Name and Email

### Step 4: Upload Picture (Optional)
- Click file input under avatar
- Select an image (JPG, PNG, GIF, WebP)
- Max size: 5MB
- See preview in circle

### Step 5: Save
- Click "Save Changes" button
- Wait for success message
- Profile updates immediately

### Step 6: Verify
- Refresh page
- See all changes persisted
- Avatar displays in profile

## Profile Fields Explained

### Name
- **What it is**: Your full name
- **Required**: Yes
- **Saved as**: first_name + last_name
- **Example**: "John Doe"

### Email
- **What it is**: Your email address
- **Required**: Yes
- **Must be unique**: Yes
- **Example**: "john@example.com"

### Phone
- **What it is**: Your phone number
- **Required**: No
- **Format**: Any format accepted
- **Example**: "+1 (555) 123-4567"

### Location
- **What it is**: Your city/country
- **Required**: No
- **Example**: "New York, USA"

### Occupation
- **What it is**: Your job title
- **Required**: No
- **Example**: "Software Engineer"

### Company
- **What it is**: Your employer
- **Required**: No
- **Example**: "Tech Corp Inc"

### Website
- **What it is**: Your personal/business website
- **Required**: No
- **Format**: Must start with http:// or https://
- **Example**: "https://johndoe.com"

### Bio
- **What it is**: Short professional summary
- **Required**: No
- **Max length**: 500 characters
- **Example**: "Passionate about technology and innovation"

### Profile Picture
- **What it is**: Your avatar/profile photo
- **Required**: No
- **Formats**: JPG, PNG, GIF, WebP
- **Max size**: 5MB
- **Fallback**: Shows initials if no picture

## Validation Rules

### Required Fields
- ❌ Cannot save without Name
- ❌ Cannot save without Email

### File Upload
- ❌ Only image files allowed
- ❌ Max 5MB file size
- ✅ JPG, PNG, GIF, WebP supported

### Email
- ❌ Must be unique (no duplicates)
- ❌ Must be valid email format

### Website
- ❌ Must start with http:// or https://
- ✅ Optional field

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Name is required" | Name field empty | Enter your full name |
| "Email is required" | Email field empty | Enter your email |
| "Please select an image file" | Wrong file type | Select JPG, PNG, GIF, or WebP |
| "File size must be less than 5MB" | File too large | Choose smaller image |
| "Failed to update profile" | Server error | Try again or contact support |

## Tips & Tricks

✅ **Save Often** - Click Save after each change
✅ **Use Good Photo** - Professional photo looks better
✅ **Complete Profile** - More info = better profile
✅ **Update Website** - Link to your portfolio
✅ **Write Bio** - Tell people about yourself
✅ **Keep Email Updated** - Important for notifications

## What Happens When You Save

1. **Frontend**: Validates all fields
2. **Frontend**: Converts avatar to file
3. **Frontend**: Creates FormData with all info
4. **Network**: Sends to backend
5. **Backend**: Validates data
6. **Backend**: Saves avatar to server
7. **Backend**: Updates database
8. **Backend**: Returns updated profile
9. **Frontend**: Updates your profile display
10. **Frontend**: Shows success message

## Data Persistence

✅ **Saved to Database** - All changes persist
✅ **Synced Across Devices** - See changes on any device
✅ **Backed Up** - Data is secure
✅ **Real-time** - Changes immediate
✅ **Timestamped** - Tracks when updated

## Privacy & Security

🔒 **Your Data is Private** - Only you can edit
🔒 **Encrypted** - Sent securely to server
🔒 **Authenticated** - Requires login
🔒 **Validated** - Server checks all data
🔒 **Backed Up** - Regular database backups

## Troubleshooting

### Profile Won't Save
1. Check all required fields filled
2. Check file size if uploading image
3. Try refreshing page
4. Try again

### Avatar Not Showing
1. Check file format (JPG, PNG, GIF, WebP)
2. Check file size (< 5MB)
3. Try different image
4. Refresh page

### Changes Not Persisting
1. Check success message appeared
2. Refresh page to verify
3. Check internet connection
4. Try again

### Can't Upload Image
1. Check file is image (not PDF, doc, etc)
2. Check file size < 5MB
3. Try different image
4. Try different browser

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Move between fields |
| Enter | Submit form (when focused on button) |
| Escape | Cancel edit (if implemented) |

## Mobile Tips

- **Tap Edit** - Opens edit mode
- **Tap File Input** - Opens camera or gallery
- **Scroll Down** - See all fields
- **Tap Save** - Saves all changes
- **Tap Cancel** - Discards changes

## Account Information (Read-Only)

These fields are managed by system:
- **Balance** - Your account balance
- **Verified** - Email verification status
- **Created** - Account creation date
- **Last Updated** - Last profile update
- **Last Login** - Last login time

---

**Quick Start**: Login → Click Profile → Click Edit → Make Changes → Click Save

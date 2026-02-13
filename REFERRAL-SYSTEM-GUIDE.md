# 🎁 Real Referral System - Complete Guide

## Overview

A complete, production-ready referral system where users can earn $5 for each successful referral. The system is fully integrated with registration and the Earn component.

---

## ✅ What's Implemented

### Backend
- ✅ Referral Model - Tracks referrals with reward status
- ✅ Referral Serializers - Data validation and transformation
- ✅ Referral Views - API endpoints for referral management
- ✅ Automatic Reward Claiming - $5 credited instantly on registration
- ✅ Database Migration - Schema for referral tracking
- ✅ Admin Interface - Manage referrals in Django admin

### Frontend
- ✅ RegisterPage with Referral Code - Accept referral code on signup
- ✅ Earn Component - Display real referral data and earnings
- ✅ Referral Link Display - Copy-to-clipboard functionality
- ✅ Real-time Stats - Total referrals, earnings, pending rewards
- ✅ Referral List - Show all referrals with status
- ✅ Reward Tiers - Unlock bonuses at referral milestones

### Features
- ✅ Unique referral codes per user
- ✅ Referral link generation
- ✅ $5 reward per successful referral
- ✅ Automatic reward claiming on registration
- ✅ Real-time earnings tracking
- ✅ Referral status monitoring
- ✅ Reward tier system
- ✅ Complete audit trail

---

## 🚀 Setup Instructions

### Step 1: Apply Migrations

```bash
cd backend-growfund
venv\Scripts\activate
py manage.py migrate accounts
```

### Step 2: Verify Installation

```bash
py manage.py showmigrations accounts
# Should show:
# [X] 0001_initial
# [X] 0002_referral
```

### Step 3: Start Servers

**Backend:**
```bash
py manage.py runserver
```

**Frontend:**
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

---

## 📖 How It Works

### User Flow

```
1. User A generates referral code (automatic on registration)
   ↓
2. User A shares referral link: http://localhost:3000/register?ref=ABC12345
   ↓
3. User B clicks link and sees referral bonus banner
   ↓
4. User B registers with referral code
   ↓
5. Backend creates Referral record
   ↓
6. $5 automatically credited to User A's balance
   ↓
7. User A sees referral in Earn component
   ↓
8. User A can track earnings and referral status
```

### Technical Flow

```
Registration Request
    ↓
Validate referral code
    ↓
Create User
    ↓
Create Referral record
    ↓
Claim reward ($5)
    ↓
Update referrer balance
    ↓
Return success response
```

---

## 🔌 API Endpoints

### Get Referral Stats
```
GET /api/auth/referral-stats/
Authorization: Bearer {token}

Response:
{
  "referral_code": "ABC12345",
  "referral_link": "http://localhost:3000/register?ref=ABC12345",
  "total_referrals": 5,
  "active_referrals": 4,
  "pending_referrals": 1,
  "total_earned": 25.00,
  "pending_earnings": 5.00,
  "this_month_earnings": 15.00
}
```

### Get Referrals List
```
GET /api/auth/referrals/
Authorization: Bearer {token}

Response:
{
  "referral_code": "ABC12345",
  "total_referrals": 5,
  "active_referrals": 4,
  "total_earned": 25.00,
  "pending_earnings": 5.00,
  "referrals": [
    {
      "id": "uuid",
      "referrer_email": "user@example.com",
      "referred_user_email": "friend@example.com",
      "referred_user_name": "John Doe",
      "reward_amount": 5.00,
      "reward_claimed": true,
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Register with Referral Code
```
POST /api/auth/register/
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "referral_code": "ABC12345"
}

Response:
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "john@example.com",
  "verification_token": "uuid"
}
```

---

## 💾 Database Schema

### Referral Table
```
id (UUID) - Primary key
referrer_id (FK) - User who referred
referred_user_id (FK) - User who was referred
reward_amount (decimal) - $5.00
reward_claimed (boolean) - True if reward given
status (string) - pending/active/inactive
created_at (datetime) - When referral created
updated_at (datetime) - Last update
```

### Unique Constraint
- (referrer_id, referred_user_id) - One referral per pair

---

## 🎯 User Experience

### For Referrer (User A)

1. **Get Referral Code**
   - Automatic on registration
   - Displayed in Earn component
   - Copy-to-clipboard button

2. **Share Link**
   - Full referral link provided
   - Easy sharing options
   - Track all referrals

3. **Earn Rewards**
   - $5 per successful referral
   - Instant credit to balance
   - Real-time tracking

4. **Monitor Progress**
   - Total referrals count
   - Active referrals count
   - Total earnings
   - Pending earnings
   - This month earnings
   - Reward tier progress

### For Referred User (User B)

1. **See Bonus Banner**
   - Green banner on registration page
   - Shows $5 bonus
   - Displays referrer code

2. **Register Normally**
   - All standard validation applies
   - Referral code auto-filled
   - No extra steps

3. **Instant Bonus**
   - $5 added to referrer's balance
   - Referral marked as active
   - Confirmation in Earn component

---

## 📊 Reward Tiers

| Referrals | Bonus | Status |
|-----------|-------|--------|
| 5 | $25 | Unlock at 5 referrals |
| 10 | $75 | Unlock at 10 referrals |
| 25 | $250 | Unlock at 25 referrals |
| 50 | $750 | Unlock at 50 referrals |

---

## 🧪 Testing

### Test Referral Registration

1. **Get Referral Code**
   - Login as User A
   - Go to Earn component
   - Copy referral code (e.g., ABC12345)

2. **Register with Code**
   - Open new browser/incognito
   - Go to: http://localhost:3000/register?ref=ABC12345
   - See green bonus banner
   - Fill registration form
   - Submit

3. **Verify Reward**
   - Login as User A
   - Check balance increased by $5
   - Go to Earn component
   - See new referral in list
   - Status: "Claimed"

### Test API

```bash
# Get referral stats
curl -X GET http://localhost:8000/api/auth/referral-stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get referrals list
curl -X GET http://localhost:8000/api/auth/referrals/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Register with referral code
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "referral_code": "ABC12345"
  }'
```

---

## 🔐 Security Features

- ✅ Referral code validation
- ✅ Duplicate referral prevention (unique constraint)
- ✅ User isolation (can only see own referrals)
- ✅ Automatic reward claiming (no manual intervention)
- ✅ Audit trail (created_at, updated_at)
- ✅ Status tracking (pending/active/inactive)

---

## 📈 Earnings Calculation

### Real-time Stats
- **Total Referrals**: Count of all referrals
- **Active Referrals**: Count of active referrals
- **Total Earned**: Sum of all claimed rewards
- **Pending Earnings**: Sum of unclaimed rewards
- **This Month Earnings**: Sum of rewards claimed this month

### Example
```
User A has:
- 5 total referrals
- 4 active referrals
- 1 pending referral
- Total earned: $20 (4 × $5)
- Pending earnings: $5 (1 × $5)
- This month: $15 (3 referrals this month)
```

---

## 🎨 UI Components

### RegisterPage
- Referral code input (auto-filled from URL)
- Green bonus banner
- Shows referrer code
- Standard registration form

### Earn Component
- Referral code display
- Copy-to-clipboard button
- Referral link display
- Real-time stats cards
- Referral list with status
- Reward tier progress
- How-to guide

---

## 🐛 Troubleshooting

### Referral Code Not Working
- Verify code is valid (8 characters)
- Check user exists with that code
- Ensure code is passed in URL: `?ref=CODE`

### Reward Not Credited
- Check referral record created
- Verify reward_claimed = true
- Check referrer balance updated
- Review Django admin

### Stats Not Updating
- Refresh page
- Check API response
- Verify authentication token
- Check browser console for errors

### Referral Not Appearing
- Verify registration completed
- Check email verification
- Ensure referral code was valid
- Check database for referral record

---

## 📝 Files Modified/Created

### Backend
- `accounts/models.py` - Added Referral model
- `accounts/serializers.py` - Added referral serializers
- `accounts/views.py` - Added referral views
- `accounts/urls.py` - Added referral endpoints
- `accounts/admin.py` - Added referral admin
- `accounts/migrations/0002_referral.py` - Migration

### Frontend
- `pages/RegisterPage.js` - Added referral code support
- `components/Earn.js` - Updated with real data
- `services/api.js` - Added referral endpoints

---

## 🚀 Deployment Checklist

- [ ] Migrations applied
- [ ] Backend running
- [ ] Frontend running
- [ ] Can register with referral code
- [ ] Reward credited instantly
- [ ] Earn component shows real data
- [ ] Referral link works
- [ ] Copy-to-clipboard works
- [ ] Stats update in real-time
- [ ] Admin can manage referrals

---

## 📞 Support

### Common Issues

**Q: Referral code not recognized**
A: Ensure the code is exactly 8 characters and belongs to an existing user

**Q: Reward not showing**
A: Refresh page, check API response, verify authentication

**Q: Can't see referrals in Earn**
A: Ensure you're logged in, check browser console for errors

**Q: Registration fails with referral code**
A: Verify code is valid, check backend logs for errors

---

## ✨ Summary

You now have a **complete, real referral system** with:
- ✅ Automatic referral code generation
- ✅ Referral link sharing
- ✅ $5 instant rewards
- ✅ Real-time earnings tracking
- ✅ Referral status monitoring
- ✅ Reward tier system
- ✅ Complete audit trail
- ✅ Admin management

**Ready to use immediately!** 🎉

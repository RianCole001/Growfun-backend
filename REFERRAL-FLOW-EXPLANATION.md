# Referral System - Complete Flow Explanation

## System Overview

The referral system allows users to earn $5 for each successful referral. Here's how it works end-to-end.

---

## User Journey

### Step 1: User A Gets Referral Code
1. User A logs in to dashboard
2. Navigates to Earn tab
3. Sees their unique referral code (e.g., "ABC12345")
4. Copies referral link: `http://localhost:3000/register?ref=ABC12345`
5. Shares link with friends

### Step 2: User B Registers with Referral Code
1. User B clicks referral link
2. Lands on registration page with referral code pre-filled
3. Sees green "Referral Bonus!" banner showing $5 bonus
4. Completes registration form
5. Submits registration

### Step 3: Backend Processes Referral
1. Backend validates referral code
2. Creates new User B account
3. Creates Referral record:
   - `referrer`: User A
   - `referred_user`: User B
   - `reward_amount`: 5.00
   - `status`: 'pending'
4. Automatically claims reward (adds $5 to User A's balance)
5. Returns success response

### Step 4: User A Sees Referral
1. User A refreshes Earn component
2. Sees updated stats:
   - Total Referrals: 1
   - Total Earned: $5.00
   - Pending Earnings: $0.00
3. Sees User B in referrals list with status "Active"

---

## Data Flow Diagram

```
Frontend (React)                Backend (Django)              Database (SQLite)
─────────────────              ────────────────              ─────────────────

User A logs in
    │
    ├─→ GET /api/auth/me/
    │       └─→ Returns User A data with referral_code
    │
    └─→ Earn component loads
        │
        ├─→ GET /api/auth/referral-stats/
        │       └─→ Returns stats (0 referrals, $0 earned)
        │
        └─→ GET /api/auth/referrals/
                └─→ Returns referrals list (empty)

User B clicks referral link
    │
    └─→ RegisterPage loads with ?ref=ABC12345
        │
        └─→ Shows referral bonus banner

User B submits registration
    │
    └─→ POST /api/auth/register/
            {
              "email": "userb@example.com",
              "password": "...",
              "referral_code": "ABC12345"
            }
            │
            ├─→ Backend validates referral code
            │       └─→ Finds User A by referral_code
            │
            ├─→ Creates User B
            │       └─→ Saves to User table
            │
            ├─→ Creates Referral record
            │       ├─→ referrer: User A
            │       ├─→ referred_user: User B
            │       ├─→ reward_amount: 5.00
            │       ├─→ status: 'pending'
            │       └─→ Saves to Referral table
            │
            ├─→ Claims reward
            │       └─→ Updates User A balance: +5.00
            │
            └─→ Returns success response

User A refreshes Earn component
    │
    ├─→ GET /api/auth/referral-stats/
    │       └─→ Returns updated stats:
    │           {
    │             "total_referrals": 1,
    │             "total_earned": 5.00,
    │             "pending_earnings": 0.00,
    │             ...
    │           }
    │
    └─→ GET /api/auth/referrals/
            └─→ Returns referrals list:
                {
                  "referrals": [
                    {
                      "referred_user_name": "User B",
                      "referred_user_email": "userb@example.com",
                      "reward_amount": 5.00,
                      "reward_claimed": true,
                      "status": "active"
                    }
                  ]
                }
```

---

## API Endpoints

### 1. Get Referral Statistics
```
GET /api/auth/referral-stats/
Authorization: Bearer <access_token>

Response:
{
  "referral_code": "ABC12345",
  "referral_link": "http://localhost:3000/register?ref=ABC12345",
  "total_referrals": 1,
  "active_referrals": 1,
  "pending_referrals": 0,
  "total_earned": 5.00,
  "pending_earnings": 0.00,
  "this_month_earnings": 5.00
}
```

### 2. Get Referrals List
```
GET /api/auth/referrals/
Authorization: Bearer <access_token>

Response:
{
  "referrals": [
    {
      "id": "uuid-here",
      "referrer_email": "usera@example.com",
      "referred_user_email": "userb@example.com",
      "referred_user_name": "User B",
      "reward_amount": 5.00,
      "reward_claimed": true,
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Register with Referral Code
```
POST /api/auth/register/
Content-Type: application/json

Request:
{
  "email": "userb@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "User",
  "last_name": "B",
  "referral_code": "ABC12345"
}

Response:
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "userb@example.com",
  "verification_token": "uuid-here"
}
```

---

## Database Schema

### User Model
```
id (PK)
email (unique)
first_name
last_name
password
referral_code (unique, auto-generated)
referred_by (FK to User, nullable)
balance (decimal)
is_verified
created_at
updated_at
...
```

### Referral Model
```
id (PK, UUID)
referrer (FK to User) - The user who owns the referral code
referred_user (FK to User) - The user who registered with the code
reward_amount (decimal, default 5.00)
reward_claimed (boolean, default False)
status (choices: pending, active, inactive)
created_at
updated_at

Unique constraint: (referrer, referred_user)
```

---

## Referral Status Meanings

| Status | Meaning | When Set |
|--------|---------|----------|
| pending | Referral created, reward not yet claimed | On registration |
| active | Referral is active, reward claimed | When reward is claimed |
| inactive | Referral is no longer active | Manual deactivation |

---

## Reward Claiming Process

### Current Implementation
- Reward is automatically claimed when user registers with referral code
- Referrer's balance is immediately updated (+$5.00)
- Referral status changes to 'active'

### Future Enhancement (Optional)
- Could implement manual reward claiming
- Could add approval workflow
- Could add reward expiration

---

## Frontend Components

### Earn.js
- Displays referral code and link
- Shows referral statistics
- Lists all referrals made by user
- Allows copying code/link to clipboard
- Shows reward tiers and unlock progress

### RegisterPage.js
- Accepts referral code from URL parameter (?ref=CODE)
- Displays referral bonus banner if code provided
- Passes referral code to registration API
- Shows success message with bonus info

---

## Backend Components

### UserRegistrationSerializer
- Validates referral code if provided
- Finds referrer by referral code
- Creates Referral record on successful registration
- Automatically claims reward

### ReferralStatsView
- Returns user's referral statistics
- Calculates total earned, pending earnings, this month earnings
- Generates referral link

### UserReferralsView
- Returns list of referrals made by user
- Includes referral details and status

---

## Error Handling

### Frontend
- Catches API errors and shows toast notification
- Handles missing or invalid referral data
- Provides fallback values for stats

### Backend
- Validates referral code exists
- Validates referral code belongs to active user
- Handles duplicate referrals (unique constraint)
- Returns appropriate HTTP status codes

---

## Security Considerations

1. **Referral Code Validation**
   - Code must exist in database
   - Code must belong to active user
   - Prevents invalid referrals

2. **Reward Claiming**
   - Automatic claiming prevents fraud
   - Referrer balance updated atomically
   - Referral record created with status

3. **Authentication**
   - All endpoints require JWT token
   - User can only see their own referrals
   - Admin can view all referrals

---

## Testing Scenarios

### Scenario 1: Happy Path
1. User A gets referral code
2. User B registers with code
3. User A sees referral in stats
4. Reward is claimed and balance updated

### Scenario 2: Invalid Code
1. User B tries to register with invalid code
2. Backend returns error
3. Registration fails
4. No referral record created

### Scenario 3: Multiple Referrals
1. User A refers User B, C, D
2. User A sees 3 referrals in list
3. Total earned: $15.00
4. Each referral shows individual status

### Scenario 4: Referral Link Sharing
1. User A copies referral link
2. Shares via email/social media
3. User B clicks link
4. Registration page pre-fills referral code
5. User B completes registration
6. Referral is recorded

---

## Troubleshooting

### Referral Code Not Generated
- Check if user was created successfully
- Verify migration was applied
- Check database for user record

### Referral Not Appearing
- Verify referral code is correct
- Check if referred user was created
- Check Referral table for record

### Balance Not Updated
- Verify reward_claimed is true
- Check if referral status is 'active'
- Verify user balance field

### API Returning Empty Data
- Check if user has any referrals
- Verify authentication token is valid
- Check if user is logged in

---

## Performance Considerations

- Referral queries are filtered by referrer (indexed)
- Stats calculation iterates through referrals (acceptable for small numbers)
- Could optimize with database aggregation for large datasets
- Consider caching stats for frequently accessed data

---

## Future Enhancements

1. **Reward Tiers**
   - Unlock bonuses at 5, 10, 25, 50 referrals
   - Increase reward amount for higher tiers

2. **Referral Tracking**
   - Track referral source (email, social, etc.)
   - Track conversion metrics

3. **Notifications**
   - Notify user when referral registers
   - Notify user when reward is claimed

4. **Referral Analytics**
   - Dashboard showing referral performance
   - Charts and graphs for referral trends

5. **Referral Expiration**
   - Set expiration date for referral codes
   - Automatic cleanup of old referrals

6. **Referral Levels**
   - Multi-level referral system
   - Earn from referrals of referrals

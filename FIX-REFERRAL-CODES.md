# Fix: Generate Referral Codes for Existing Users

## Problem
Existing users don't have referral codes because they were created before the referral system was implemented.

## Solution
Run the management command to generate referral codes for all users.

---

## Step 1: Run the Management Command

```bash
cd backend-growfund
py manage.py generate_referral_codes
```

Expected output:
```
Generated code for admin001@gmail.com: ABC12345
Generated code for admin@growfund.com: XYZ98765
...
Successfully generated X referral codes
```

---

## Step 2: Verify Codes Were Generated

```bash
cd backend-growfund
py manage.py shell

from accounts.models import User

# Check all users have codes
for user in User.objects.all():
    print(f"{user.email}: {user.referral_code}")

# Exit
exit()
```

---

## Step 3: Refresh Earn Component

1. Go to browser
2. Refresh page (F5)
3. Navigate to Earn component
4. Should now see referral code and link

---

## If Still Not Working

1. Check browser console (F12 → Console)
2. Check Network tab for API response
3. Verify referral_code is not empty in database
4. Restart Django server

---

## What This Does

- Generates unique 8-character referral codes for all users
- Ensures no duplicate codes
- Saves codes to database
- Allows users to start earning referrals immediately

---

## Next Steps

After running this command:
1. Refresh Earn component
2. Should see referral code and link
3. Test registration with referral code
4. Verify referral system works end-to-end

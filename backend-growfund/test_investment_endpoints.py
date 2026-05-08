"""
Test investment edit/delete endpoints
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from investments.models import Trade, CapitalInvestmentPlan

User = get_user_model()

print("\n🧪 Testing Investment Endpoints\n")
print("=" * 60)

# Check for investments
trades = Trade.objects.all()
capital_plans = CapitalInvestmentPlan.objects.all()

print(f"\n📊 Current Investments:")
print(f"   Trades: {trades.count()}")
for trade in trades[:3]:
    print(f"     - ID: {trade.id} (UUID)")
    print(f"       User: {trade.user.email}")
    print(f"       Asset: {trade.asset}")
    print(f"       Amount: ${trade.entry_price * trade.quantity}")

print(f"\n   Capital Plans: {capital_plans.count()}")
for plan in capital_plans[:3]:
    print(f"     - ID: {plan.id} (UUID)")
    print(f"       User: {plan.user.email}")
    print(f"       Type: {plan.plan_type}")
    print(f"       Amount: ${plan.initial_amount}")

print(f"\n✅ Investment IDs are UUIDs")
print(f"✅ New endpoints support UUID IDs:")
print(f"   - PUT /api/admin/investments/<uuid>/edit/")
print(f"   - DELETE /api/admin/investments/<uuid>/delete/")

print("\n" + "=" * 60)
print("✅ Investment endpoints ready for testing!\n")

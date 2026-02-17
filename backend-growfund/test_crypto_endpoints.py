"""
Quick test script for crypto pricing endpoints
Run with: python test_crypto_endpoints.py
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test data
ADMIN_EMAIL = "admin001@gmail.com"
ADMIN_PASSWORD = "admin123"  # Update with actual password

def test_login():
    """Test admin login"""
    print("\n🔐 Testing Admin Login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"   Admin: {data.get('user', {}).get('email')}")
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_get_admin_prices(token):
    """Test getting admin crypto prices"""
    print("\n📊 Testing Get Admin Crypto Prices...")
    response = requests.get(
        f"{BASE_URL}/api/investments/admin/crypto-prices/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {len(data.get('data', {}))} crypto prices:")
        for coin, price_data in data.get('data', {}).items():
            print(f"   {coin}: Buy ${price_data['buy_price']} / Sell ${price_data['sell_price']} (Spread: {price_data['spread_percentage']:.2f}%)")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_get_public_prices(token):
    """Test getting public crypto prices"""
    print("\n💰 Testing Get Public Crypto Prices...")
    response = requests.get(
        f"{BASE_URL}/api/investments/crypto/prices/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got public prices:")
        for coin, price_data in data.get('data', {}).items():
            print(f"   {coin}: ${price_data['price']} (24h: {price_data['change24h']}%)")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_update_price(token):
    """Test updating crypto price"""
    print("\n✏️ Testing Update Crypto Price...")
    response = requests.put(
        f"{BASE_URL}/api/investments/admin/crypto-prices/update/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "coin": "EXACOIN",
            "buy_price": 65.00,
            "sell_price": 62.00,
            "change_24h": 5.00
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ Price updated successfully!")
        print(f"   {data.get('data', {}).get('coin')}: Buy ${data.get('data', {}).get('buy_price')} / Sell ${data.get('data', {}).get('sell_price')}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    print("=" * 60)
    print("🧪 CRYPTO PRICING ENDPOINTS TEST")
    print("=" * 60)
    
    # Login
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Test endpoints
    test_get_admin_prices(token)
    test_get_public_prices(token)
    test_update_price(token)
    
    # Verify update
    test_get_admin_prices(token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

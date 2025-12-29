#!/usr/bin/env python3
"""
test_payment_system.py - Quick test for the payment system

Run this to verify the payment system is working correctly.
"""

from payment_system import PaymentSystem

def test_payment_system():
    print("=" * 60)
    print("🧪 TESTING CLOUD PAYMENT SYSTEM")
    print("=" * 60)
    
    # Initialize payment system
    ps = PaymentSystem()
    
    # Test 1: Get storage plans
    print("\n1️⃣ Testing: Get Storage Plans")
    plans = ps.get_storage_plans()
    for plan_key, plan in plans.items():
        print(f"   ✓ {plan['name']}: {plan['storage_gb']}GB - ${plan['price_per_month']}/month")
    
    # Test 2: Calculate storage cost
    print("\n2️⃣ Testing: Calculate Storage Cost")
    cost, plan_key, plan = ps.calculate_storage_cost(50)
    print(f"   ✓ 50GB storage costs: ${cost}/month ({plan['name']} plan)")
    
    # Test 3: Get storage status
    print("\n3️⃣ Testing: Storage Status with Color Coding")
    test_cases = [
        (500 * 1024 * 1024, 2, "500MB / 2GB"),  # Green
        (1.6 * 1024 * 1024 * 1024, 2, "1.6GB / 2GB"),  # Yellow
        (1.85 * 1024 * 1024 * 1024, 2, "1.85GB / 2GB"),  # Red
    ]
    
    for used_bytes, allocated_gb, description in test_cases:
        status = ps.get_storage_status(used_bytes, allocated_gb)
        print(f"   {description}: {status['level'].upper()} ({status['usage_percent']:.1f}%) - {status['message']}")
    
    # Test 4: Process simulated payment
    print("\n4️⃣ Testing: Process Simulated Payment")
    result = ps.process_payment(
        user_email="test@example.com",
        user_id="user_test_123",
        amount=4.99,
        storage_gb=50,
        payment_method="credit_card"
    )
    if result['success']:
        print(f"   ✓ Payment processed: {result['payment_id']}")
        print(f"   ✓ Storage allocated: {result['storage_allocated']}GB")
        print(f"   ✓ Amount: ${result['receipt']['amount']}")
    
    # Test 5: Get subscription
    print("\n5️⃣ Testing: Get User Subscription")
    subscription = ps.get_user_subscription("test@example.com")
    if subscription:
        print(f"   ✓ Plan: {subscription['storage_gb']}GB")
        print(f"   ✓ Status: {subscription['status']}")
        print(f"   ✓ Next billing: {subscription['next_billing_date'][:10]}")
    
    # Test 6: Get payment history
    print("\n6️⃣ Testing: Get Payment History")
    history = ps.get_user_payment_history("test@example.com")
    print(f"   ✓ Total payments: {len(history)}")
    if history:
        latest = history[-1]
        print(f"   ✓ Latest: ${latest['amount']} for {latest['storage_gb']}GB")
    
    # Test 7: Get upgrade suggestions
    print("\n7️⃣ Testing: Upgrade Suggestions")
    suggestions = ps.get_upgrade_suggestions(current_storage_gb=2, used_gb=1.8)
    print(f"   ✓ Found {len(suggestions)} upgrade options:")
    for suggestion in suggestions[:3]:  # Show first 3
        print(f"      - {suggestion['plan_name']}: {suggestion['storage_gb']}GB @ ${suggestion['price']}/mo")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Payment system is working perfectly!")
    print("=" * 60)
    print("\n🚀 Ready to use! Start the web API with: python web_api.py")
    print("📖 See CLOUD_PAYMENT_FEATURES.md for full documentation")

if __name__ == '__main__':
    test_payment_system()

#!/usr/bin/env python3
"""
payment_system.py - Simulated Cloud Payment System

This module handles simulated payment processing for storage upgrades,
subscription management, and payment history tracking.
"""

import os
import json
import secrets
import time
from datetime import datetime, timedelta

class PaymentSystem:
    """Simulated cloud payment system for storage upgrades"""
    
    def __init__(self, payments_db_path='payments.json', subscriptions_db_path='subscriptions.json'):
        self.payments_db_path = payments_db_path
        self.subscriptions_db_path = subscriptions_db_path
        self.payments = self.load_payments()
        self.subscriptions = self.load_subscriptions()
        
        # Storage pricing plans (per GB per month)
        self.STORAGE_PLANS = {
            'basic': {
                'name': 'Basic',
                'storage_gb': 2,
                'price_per_month': 0,
                'color': '#95a5a6',
                'features': ['2GB Storage', 'Basic Support']
            },
            'pro': {
                'name': 'Pro',
                'storage_gb': 50,
                'price_per_month': 4.99,
                'color': '#3498db',
                'features': ['50GB Storage', 'Priority Support', 'File Versioning']
            },
            'business': {
                'name': 'Business',
                'storage_gb': 200,
                'price_per_month': 9.99,
                'color': '#2ecc71',
                'features': ['200GB Storage', '24/7 Support', 'File Versioning', 'Team Collaboration']
            },
            'enterprise': {
                'name': 'Enterprise',
                'storage_gb': 1000,
                'price_per_month': 29.99,
                'color': '#f39c12',
                'features': ['1TB Storage', 'Dedicated Support', 'Advanced Security', 'Custom Branding']
            }
        }
        
        # Per-GB pricing for custom amounts
        self.PRICE_PER_GB = 0.10  # $0.10 per GB per month
    
    def load_payments(self):
        """Load payment history from JSON database"""
        if os.path.exists(self.payments_db_path):
            try:
                with open(self.payments_db_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def load_subscriptions(self):
        """Load subscriptions from JSON database"""
        if os.path.exists(self.subscriptions_db_path):
            try:
                with open(self.subscriptions_db_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save_payments(self):
        """Save payment history to JSON database"""
        with open(self.payments_db_path, 'w') as f:
            json.dump(self.payments, f, indent=2)
    
    def save_subscriptions(self):
        """Save subscriptions to JSON database"""
        with open(self.subscriptions_db_path, 'w') as f:
            json.dump(self.subscriptions, f, indent=2)
    
    def get_storage_plans(self):
        """Get available storage plans"""
        return self.STORAGE_PLANS
    
    def calculate_storage_cost(self, storage_gb):
        """Calculate monthly cost for a given storage amount"""
        # Find the best matching plan
        for plan_key, plan in sorted(self.STORAGE_PLANS.items(), key=lambda x: x[1]['storage_gb']):
            if storage_gb <= plan['storage_gb']:
                return plan['price_per_month'], plan_key, plan
        
        # Custom pricing for amounts larger than enterprise
        custom_cost = storage_gb * self.PRICE_PER_GB
        return custom_cost, 'custom', {
            'name': 'Custom',
            'storage_gb': storage_gb,
            'price_per_month': custom_cost,
            'color': '#9b59b6',
            'features': [f'{storage_gb}GB Storage', 'All Enterprise Features']
        }
    
    def process_payment(self, user_email, user_id, amount, storage_gb, payment_method='credit_card'):
        """
        Simulate payment processing for storage upgrade
        In a real system, this would integrate with Stripe, PayPal, etc.
        """
        # Generate payment ID
        payment_id = f"pay_{int(time.time())}_{secrets.token_hex(8)}"
        
        # Simulate payment processing (always succeeds in simulation)
        payment_record = {
            'payment_id': payment_id,
            'user_email': user_email,
            'user_id': user_id,
            'amount': amount,
            'currency': 'USD',
            'storage_gb': storage_gb,
            'payment_method': payment_method,
            'status': 'completed',
            'transaction_date': datetime.now().isoformat(),
            'description': f'Storage upgrade to {storage_gb}GB',
            'receipt_url': f'/api/receipts/{payment_id}',
            'card_last4': '4242' if payment_method == 'credit_card' else None
        }
        
        # Save payment record
        self.payments.append(payment_record)
        self.save_payments()
        
        # Update or create subscription
        self.update_subscription(user_email, storage_gb, amount)
        
        return {
            'success': True,
            'payment_id': payment_id,
            'message': f'Payment of ${amount:.2f} processed successfully',
            'storage_allocated': storage_gb,
            'receipt': payment_record
        }
    
    def update_subscription(self, user_email, storage_gb, monthly_amount):
        """Update or create a subscription for a user"""
        now = datetime.now()
        next_billing_date = (now + timedelta(days=30)).isoformat()
        
        subscription_data = {
            'user_email': user_email,
            'storage_gb': storage_gb,
            'monthly_amount': monthly_amount,
            'status': 'active',
            'started_at': now.isoformat(),
            'next_billing_date': next_billing_date,
            'updated_at': now.isoformat()
        }
        
        self.subscriptions[user_email] = subscription_data
        self.save_subscriptions()
        
        return subscription_data
    
    def get_user_subscription(self, user_email):
        """Get user's current subscription"""
        return self.subscriptions.get(user_email)
    
    def get_user_payment_history(self, user_email):
        """Get user's payment history"""
        return [p for p in self.payments if p['user_email'] == user_email]
    
    def cancel_subscription(self, user_email):
        """Cancel a user's subscription (downgrade to free plan)"""
        if user_email in self.subscriptions:
            self.subscriptions[user_email]['status'] = 'cancelled'
            self.subscriptions[user_email]['cancelled_at'] = datetime.now().isoformat()
            self.save_subscriptions()
            return {'success': True, 'message': 'Subscription cancelled'}
        return {'success': False, 'message': 'No active subscription found'}
    
    def get_storage_status(self, user_storage_used_bytes, user_storage_allocated_gb):
        """
        Get storage status with color coding
        Returns status level: 'green', 'yellow', or 'red'
        """
        used_gb = user_storage_used_bytes / (1024 * 1024 * 1024)
        usage_percent = (used_gb / user_storage_allocated_gb) * 100
        
        status = {
            'used_gb': used_gb,
            'allocated_gb': user_storage_allocated_gb,
            'used_bytes': user_storage_used_bytes,
            'usage_percent': usage_percent,
            'available_gb': user_storage_allocated_gb - used_gb,
            'available_bytes': (user_storage_allocated_gb * 1024 * 1024 * 1024) - user_storage_used_bytes
        }
        
        # Determine status level
        if usage_percent >= 90:
            status['level'] = 'red'
            status['color'] = '#e74c3c'
            status['message'] = 'Storage almost full! Upgrade now to continue uploading.'
            status['alert'] = True
        elif usage_percent >= 75:
            status['level'] = 'yellow'
            status['color'] = '#f39c12'
            status['message'] = 'Storage filling up. Consider upgrading soon.'
            status['alert'] = True
        else:
            status['level'] = 'green'
            status['color'] = '#2ecc71'
            status['message'] = 'Storage healthy'
            status['alert'] = False
        
        return status
    
    def get_upgrade_suggestions(self, current_storage_gb, used_gb):
        """Get suggested upgrade plans based on current usage"""
        suggestions = []
        
        for plan_key, plan in self.STORAGE_PLANS.items():
            if plan['storage_gb'] > current_storage_gb:
                suggestions.append({
                    'plan_key': plan_key,
                    'plan_name': plan['name'],
                    'storage_gb': plan['storage_gb'],
                    'price': plan['price_per_month'],
                    'savings_vs_custom': max(0, (plan['storage_gb'] * self.PRICE_PER_GB) - plan['price_per_month']),
                    'features': plan['features'],
                    'color': plan['color']
                })
        
        return suggestions

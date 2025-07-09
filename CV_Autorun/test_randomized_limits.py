#!/usr/bin/env python3
"""
Test script to demonstrate randomized daily limits (400-450 range)
"""

import sys
import os
sys.path.append('src')

from account_manager import AccountManager
from account_utils import AccountUtilities

def main():
    print("=" * 80)
    print("RANDOMIZED DAILY LIMITS TEST (400-450 range)")
    print("=" * 80)
    
    try:
        # Initialize utilities
        utils = AccountUtilities()
        
        # Show configuration
        print("\n1. CONFIGURATION:")
        print("-" * 40)
        
        for account in utils.account_manager.accounts:
            limit_range = account.get('daily_limit_range', [400, 450])
            print(f"Account {account['id']}: {account['sender_email']}")
            print(f"  Daily Limit Range: {limit_range[0]}-{limit_range[1]} emails")
        
        # Show current daily limits
        print("\n2. TODAY'S RANDOMIZED LIMITS:")
        print("-" * 40)
        
        stats = utils.account_manager.get_account_stats()
        total_capacity = 0
        
        for account in stats['accounts']:
            limit_display = account.get('daily_limit_display', f"{account['daily_limit']}")
            total_capacity += account['daily_limit']
            print(f"✓ {account['id']}: {account['daily_limit']} emails (range: {limit_display})")
        
        print(f"\nTotal Daily Capacity: {total_capacity} emails")
        print(f"Expected Range: 1200-1350 emails (3 accounts × 400-450)")
        
        # Show account statistics
        print("\n3. DETAILED ACCOUNT STATISTICS:")
        print("-" * 40)
        utils.show_account_stats()
        
        # Test connections
        print("\n4. CONNECTION TEST:")
        print("-" * 40)
        success = utils.test_account_connection()
        
        if success:
            print(f"\n✅ ALL ACCOUNTS WORKING!")
            print(f"📊 Today's Capacity: {total_capacity} emails")
            print(f"🎯 Optimal Daily Limit: {total_capacity}")
            print(f"\n🚀 Run campaign with:")
            print(f"python src/main.py --resume data/Ayush.pdf --batch-size 50 --daily-limit {total_capacity}")
        else:
            print("\n❌ Some accounts have issues")
        
        # Show safety benefits
        print("\n5. SAFETY BENEFITS:")
        print("-" * 40)
        print("✅ Randomized limits (400-450) avoid detection patterns")
        print("✅ Each account gets different daily limit")
        print("✅ More natural sending behavior")
        print("✅ Reduced risk of being flagged as spam")
        print("✅ Better long-term account health")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

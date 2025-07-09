#!/usr/bin/env python3
"""
Quick test script for 3-account setup
Tests all 3 accounts and shows comprehensive statistics
"""

import sys
import os
sys.path.append('src')

from account_manager import AccountManager
from account_utils import AccountUtilities

def main():
    print("=" * 60)
    print("3-ACCOUNT SETUP TEST")
    print("=" * 60)
    
    try:
        # Initialize utilities
        utils = AccountUtilities()
        
        # Show current configuration
        print("\n1. CURRENT CONFIGURATION:")
        print("-" * 30)
        config = utils.account_manager.config
        total_accounts = len(config.get('email_accounts', []))
        enabled_accounts = len(utils.account_manager.accounts)
        print(f"Total configured accounts: {total_accounts}")
        print(f"Enabled accounts: {enabled_accounts}")
        
        if enabled_accounts == 3:
            print("✅ Perfect! You have 3 accounts enabled")
        else:
            print(f"⚠️  Expected 3 accounts, found {enabled_accounts}")
        
        # Show account details
        print("\n2. ACCOUNT DETAILS:")
        print("-" * 30)
        stats = utils.account_manager.get_account_stats()
        for i, account_stat in enumerate(stats['accounts'], 1):
            print(f"Account {i}: {account_stat['id']} ({account_stat['email']})")
            print(f"  Daily Limit: {account_stat['daily_limit_display']}")
            print(f"  Status: {'✅ Enabled' if account_stat['status'] == 'active' else '❌ Disabled'}")
            print(f"  Emails sent today: {account_stat['emails_sent_today']}")
            print(f"  Remaining today: {account_stat['remaining_today']}")
        
        # Calculate total capacity
        total_capacity = utils.account_manager.get_total_daily_capacity()
        print(f"\nTotal Daily Capacity: {total_capacity} emails")
        
        # Show account statistics
        print("\n3. ACCOUNT STATISTICS:")
        print("-" * 30)
        utils.show_account_stats()
        
        # Test all accounts
        print("\n4. TESTING ACCOUNT CONNECTIONS:")
        print("-" * 30)
        success = utils.test_account_connection()
        
        if success:
            print("\n✅ ALL ACCOUNTS WORKING PERFECTLY!")
            print("\n🚀 You can now run campaigns with --daily-limit 1500")
            print("\nExample command:")
            print("python src/main.py --resume data/Ayush.pdf --batch-size 50 --daily-limit 1500")
        else:
            print("\n❌ Some accounts have connection issues")
            print("Please check the failed accounts and their credentials")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

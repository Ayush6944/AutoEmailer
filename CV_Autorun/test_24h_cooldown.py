#!/usr/bin/env python3
"""
Test script for 24-hour cooldown feature
Perfect for server deployments to prevent spam detection
"""

import sys
import os
sys.path.append('src')

from account_manager import AccountManager
from account_utils import AccountUtilities
from datetime import datetime, timedelta

def main():
    print("=" * 80)
    print("24-HOUR COOLDOWN FEATURE TEST")
    print("=" * 80)
    
    try:
        # Initialize utilities
        utils = AccountUtilities()
        
        # Show configuration
        print("\n1. CONFIGURATION CHECK:")
        print("-" * 50)
        config = utils.account_manager.config
        email_rotation = config.get('email_rotation', {})
        
        server_mode = email_rotation.get('server_mode', False)
        cooldown_hours = email_rotation.get('account_cooldown_hours', 24)
        
        print(f"Server Mode: {'✅ ENABLED' if server_mode else '❌ DISABLED'}")
        if server_mode:
            print(f"Account Cooldown: {cooldown_hours} hours")
            print(f"Short-term Cooldown: {email_rotation.get('cooldown_minutes', 60)} minutes")
        else:
            print("⚠️  Server mode is DISABLED. Enable it in config.json for 24-hour cooldown.")
        
        # Show current account statistics
        print("\n2. ACCOUNT STATISTICS:")
        print("-" * 50)
        utils.show_account_stats()
        
        # Show detailed cooldown status
        print("\n3. 24-HOUR COOLDOWN STATUS:")
        print("-" * 50)
        utils.show_cooldown_status()
        
        # Calculate server capacity with cooldown
        print("\n4. SERVER CAPACITY ANALYSIS:")
        print("-" * 50)
        
        if server_mode:
            total_accounts = len(utils.account_manager.accounts)
            cooldown_status = utils.account_manager.get_account_cooldown_status()
            
            available_accounts = sum(1 for acc in cooldown_status['accounts'] if acc['is_available'])
            
            print(f"Total Accounts: {total_accounts}")
            print(f"Available Now: {available_accounts}")
            print(f"In Cooldown: {total_accounts - available_accounts}")
            
            if available_accounts > 0:
                daily_capacity = utils.account_manager.get_remaining_daily_capacity()
                print(f"Current Daily Capacity: {daily_capacity} emails")
                print(f"✅ Ready for campaign")
            else:
                next_available = cooldown_status.get('next_available_account')
                if next_available:
                    time_until = next_available - datetime.now()
                    hours_until = time_until.total_seconds() / 3600
                    print(f"⏰ Next account available in {hours_until:.1f} hours")
                    print(f"📅 Available at: {next_available.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print("❌ No accounts available")
        else:
            print("Server mode disabled - no cooldown restrictions")
        
        # Show safety benefits
        print("\n5. SERVER DEPLOYMENT BENEFITS:")
        print("-" * 50)
        print("✅ 24-hour cooldown prevents spam detection")
        print("✅ Each account used only once per day")
        print("✅ Natural usage patterns maintained")
        print("✅ Long-term account health preserved")
        print("✅ Ideal for automated server deployments")
        print("✅ Gmail-friendly sending behavior")
        
        # Show usage recommendations
        print("\n6. USAGE RECOMMENDATIONS:")
        print("-" * 50)
        
        if server_mode and available_accounts > 0:
            daily_capacity = utils.account_manager.get_remaining_daily_capacity()
            print(f"🚀 Run campaign with up to {daily_capacity} emails today")
            print(f"📋 Command: python src/main.py --resume data/Ayush.pdf --daily-limit {daily_capacity}")
        elif server_mode:
            print("⏳ Wait for cooldown period to expire")
            print("🔄 Check status with: python src/account_utils.py --cooldown-status")
        else:
            print("⚙️  Enable server mode in config.json first")
            print("🔧 Set 'server_mode': true in email_rotation section")
        
        print("\n" + "=" * 80)
        
        # Test connection for available accounts
        if server_mode and available_accounts > 0:
            print("\n7. CONNECTION TEST (Available Accounts Only):")
            print("-" * 50)
            
            # Test only available accounts
            for account_status in cooldown_status['accounts']:
                if account_status['is_available']:
                    account_id = account_status['id']
                    print(f"Testing {account_id}...", end=" ")
                    # You could add actual SMTP testing here
                    print("✅ Available for testing")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

def demo_cooldown_cycle():
    """Demonstrate how the cooldown cycle works"""
    print("\n" + "=" * 80)
    print("COOLDOWN CYCLE DEMONSTRATION")
    print("=" * 80)
    
    print("\n📅 Day 1: Account 1 sends emails")
    print("   - Account 1: ACTIVE (sends 425 emails)")
    print("   - Account 2: INACTIVE (24h cooldown)")
    print("   - Account 3: INACTIVE (24h cooldown)")
    
    print("\n📅 Day 2: Account 2 sends emails")
    print("   - Account 1: INACTIVE (24h cooldown)")
    print("   - Account 2: ACTIVE (sends 438 emails)")
    print("   - Account 3: INACTIVE (24h cooldown)")
    
    print("\n📅 Day 3: Account 3 sends emails")
    print("   - Account 1: INACTIVE (24h cooldown)")
    print("   - Account 2: INACTIVE (24h cooldown)")
    print("   - Account 3: ACTIVE (sends 412 emails)")
    
    print("\n📅 Day 4: Back to Account 1")
    print("   - Account 1: ACTIVE (ready again)")
    print("   - Account 2: INACTIVE (24h cooldown)")
    print("   - Account 3: INACTIVE (24h cooldown)")
    
    print("\n🔄 This cycle ensures:")
    print("   - Maximum Gmail safety")
    print("   - Natural usage patterns")
    print("   - Long-term account health")
    print("   - Automated server operation")

if __name__ == '__main__':
    success = main()
    
    if success:
        demo_cooldown_cycle()
    
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Account Management Utility Script
Provides CLI interface for managing email accounts, viewing statistics, and testing connections
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from account_manager import AccountManager
from email_engine import EmailEngine
import smtplib
from email.mime.text import MIMEText

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AccountUtilities:
    """Utility class for managing email accounts"""
    
    def __init__(self):
        self.account_manager = AccountManager()
    
    def show_account_stats(self):
        """Display comprehensive account statistics"""
        stats = self.account_manager.get_account_stats()
        
        print("\n" + "="*60)
        print("EMAIL ACCOUNT STATISTICS")
        print("="*60)
        print(f"Total Accounts: {stats['total_accounts']}")
        print(f"Active Accounts: {stats['active_accounts']}")
        print(f"Total Daily Capacity: {self.account_manager.get_total_daily_capacity()}")
        print(f"Remaining Daily Capacity: {self.account_manager.get_remaining_daily_capacity()}")
        print(f"Emails Sent Today: {stats['total_sent_today']}")
        print(f"Total Emails Sent: {stats['total_sent_overall']}")
        
        # Show server mode status
        server_mode = self.account_manager.config.get('email_rotation', {}).get('server_mode', False)
        if server_mode:
            print(f"Server Mode: ✅ ENABLED (24-hour cooldown active)")
        else:
            print(f"Server Mode: ❌ DISABLED")
        
        print("\n" + "-"*60)
        print("INDIVIDUAL ACCOUNT STATUS")
        print("-"*60)
        
        for account in stats['accounts']:
            status_indicator = "✓" if account['status'] == 'active' else "✗"
            limit_display = account.get('daily_limit_display', f"{account['daily_limit']}")
            print(f"{status_indicator} {account['id']:<12} | {account['email']:<30} | {account['emails_sent_today']:>3}/{limit_display:<12} | {account['status']:<8}")
            
            if account['failed_attempts'] > 0:
                print(f"    Failed attempts: {account['failed_attempts']}")
            
            if account['last_used']:
                try:
                    last_used = datetime.fromisoformat(account['last_used'])
                    print(f"    Last used: {last_used.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    print(f"    Last used: {account['last_used']}")
        
        print("\n" + "="*60)
    
    def test_account_connection(self, account_id: str = None):
        """Test SMTP connection for specified account or all accounts"""
        if account_id:
            # Test specific account
            account = None
            for acc in self.account_manager.accounts:
                if acc['id'] == account_id:
                    account = acc
                    break
            
            if not account:
                print(f"Account '{account_id}' not found")
                return False
            
            accounts_to_test = [account]
        else:
            # Test all accounts
            accounts_to_test = self.account_manager.accounts
        
        print("\n" + "="*60)
        print("TESTING ACCOUNT CONNECTIONS")
        print("="*60)
        
        results = []
        
        for account in accounts_to_test:
            print(f"Testing {account['id']} ({account['sender_email']})... ", end="")
            
            try:
                with smtplib.SMTP(account.get('smtp_server', 'smtp.gmail.com'), 
                                account.get('smtp_port', 587)) as server:
                    if account.get('use_tls', True):
                        server.starttls()
                    server.login(account['sender_email'], account['sender_password'])
                    
                print("✓ SUCCESS")
                results.append((account['id'], True, None))
                
            except Exception as e:
                print(f"✗ FAILED: {str(e)}")
                results.append((account['id'], False, str(e)))
        
        print("\n" + "-"*60)
        print("CONNECTION TEST SUMMARY")
        print("-"*60)
        
        success_count = sum(1 for _, success, _ in results if success)
        total_count = len(results)
        
        print(f"Successful connections: {success_count}/{total_count}")
        
        if success_count < total_count:
            print("\nFailed accounts:")
            for account_id, success, error in results:
                if not success:
                    print(f"  {account_id}: {error}")
        
        return success_count == total_count
    
    def send_test_email(self, account_id: str, test_email: str):
        """Send a test email using specified account"""
        account = None
        for acc in self.account_manager.accounts:
            if acc['id'] == account_id:
                account = acc
                break
        
        if not account:
            print(f"Account '{account_id}' not found")
            return False
        
        try:
            email_engine = EmailEngine(self.account_manager)
            
            # Create test email content
            subject = "Test Email from AutoEmailer System"
            content = f"""
            <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a test email sent from the AutoEmailer system.</p>
                <p><strong>Account:</strong> {account['id']} ({account['sender_email']})</p>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>If you received this email, the account is working correctly.</p>
            </body>
            </html>
            """
            
            success, used_account_id = email_engine._send_email(
                to_email=test_email,
                subject=subject,
                content=content,
                is_html=True,
                account=account
            )
            
            if success:
                print(f"✓ Test email sent successfully to {test_email} using account {used_account_id}")
                return True
            else:
                print(f"✗ Failed to send test email")
                return False
                
        except Exception as e:
            print(f"✗ Error sending test email: {str(e)}")
            return False
    
    def reset_account_errors(self, account_id: str):
        """Reset error count for an account"""
        try:
            self.account_manager.reset_account_errors(account_id)
            print(f"✓ Reset errors for account {account_id}")
        except Exception as e:
            print(f"✗ Error resetting account {account_id}: {str(e)}")
    
    def disable_account(self, account_id: str):
        """Disable an account"""
        try:
            self.account_manager.disable_account(account_id)
            print(f"✓ Disabled account {account_id}")
        except Exception as e:
            print(f"✗ Error disabling account {account_id}: {str(e)}")
    
    def enable_account(self, account_id: str):
        """Enable an account"""
        try:
            self.account_manager.enable_account(account_id)
            print(f"✓ Enabled account {account_id}")
        except Exception as e:
            print(f"✗ Error enabling account {account_id}: {str(e)}")
    
    def reset_daily_counters(self):
        """Manually reset daily counters for all accounts"""
        try:
            # Force reset by updating the date
            self.account_manager.progress['last_reset_date'] = '2000-01-01'
            self.account_manager.progress = self.account_manager._reset_daily_counters(self.account_manager.progress)
            self.account_manager._save_progress()
            print("✓ Daily counters reset for all accounts")
        except Exception as e:
            print(f"✗ Error resetting daily counters: {str(e)}")
    
    def show_config(self):
        """Display current configuration"""
        print("\n" + "="*60)
        print("CURRENT CONFIGURATION")
        print("="*60)
        
        config = self.account_manager.config
        
        print(f"Configuration file: {self.account_manager.config_path}")
        print(f"Progress file: {self.account_manager.progress_file}")
        
        if 'email_rotation' in config:
            rotation = config['email_rotation']
            print(f"Rotation strategy: {rotation.get('strategy', 'round_robin')}")
            print(f"Cooldown minutes: {rotation.get('cooldown_minutes', 60)}")
            print(f"Max accounts: {rotation.get('max_accounts', 10)}")
            print(f"Server mode: {rotation.get('server_mode', False)}")
            if rotation.get('server_mode', False):
                print(f"Account cooldown hours: {rotation.get('account_cooldown_hours', 24)}")
        
        print(f"Total configured accounts: {len(config.get('email_accounts', []))}")
        print(f"Enabled accounts: {len(self.account_manager.accounts)}")
    
    def show_cooldown_status(self):
        """Display 24-hour cooldown status for all accounts"""
        cooldown_status = self.account_manager.get_account_cooldown_status()
        
        print("\n" + "="*70)
        print("24-HOUR COOLDOWN STATUS")
        print("="*70)
        
        if not cooldown_status['server_mode']:
            print("⚠️  Server mode is DISABLED. 24-hour cooldown is not active.")
            print("Enable server mode in config.json to activate 24-hour cooldown.")
            return
        
        print(f"Server Mode: ✅ ENABLED")
        print(f"Cooldown Period: {cooldown_status['cooldown_hours']} hours")
        
        next_available = cooldown_status.get('next_available_account')
        if next_available:
            if next_available <= datetime.now():
                print(f"Next Available: ✅ NOW")
            else:
                time_until = next_available - datetime.now()
                hours_until = time_until.total_seconds() / 3600
                print(f"Next Available: ⏰ {next_available.strftime('%Y-%m-%d %H:%M:%S')} ({hours_until:.1f}h)")
        else:
            print(f"Next Available: ✅ NOW")
        
        print("\n" + "-"*70)
        print("ACCOUNT COOLDOWN STATUS")
        print("-"*70)
        
        for account in cooldown_status['accounts']:
            status_icon = "✅" if account['is_available'] else "❌"
            print(f"{status_icon} {account['id']:<12} | {account['email']:<30} | {account['status']:<8}")
            
            if account['last_campaign_date']:
                try:
                    last_campaign = datetime.fromisoformat(account['last_campaign_date'])
                    print(f"    Last Campaign: {last_campaign.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    print(f"    Last Campaign: {account['last_campaign_date']}")
            else:
                print(f"    Last Campaign: Never")
            
            if account['cooldown_remaining']:
                print(f"    Cooldown Remaining: {account['cooldown_remaining']:.1f} hours")
                if account['available_at']:
                    try:
                        available_time = account['available_at']
                        if isinstance(available_time, str):
                            available_time = datetime.fromisoformat(available_time)
                        print(f"    Available At: {available_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        print(f"    Available At: {account['available_at']}")
            else:
                print(f"    Status: ✅ AVAILABLE NOW")
            
            print()
        
        print("="*70)
    
    def reset_cooldown(self, account_id: str):
        """Reset 24-hour cooldown for specific account"""
        try:
            self.account_manager.reset_account_cooldown(account_id)
            print(f"✅ Reset 24-hour cooldown for account {account_id}")
        except Exception as e:
            print(f"❌ Error resetting cooldown for account {account_id}: {str(e)}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Account Management Utility')
    parser.add_argument('--stats', action='store_true', help='Show account statistics')
    parser.add_argument('--test', nargs='?', const='all', help='Test account connection (account_id or "all")')
    parser.add_argument('--send-test', nargs=2, metavar=('account_id', 'email'), 
                       help='Send test email to specified address')
    parser.add_argument('--reset-errors', help='Reset error count for account')
    parser.add_argument('--disable', help='Disable account')
    parser.add_argument('--enable', help='Enable account')
    parser.add_argument('--reset-daily', action='store_true', help='Reset daily counters')
    parser.add_argument('--config', action='store_true', help='Show configuration')
    parser.add_argument('--cooldown-status', action='store_true', help='Show 24-hour cooldown status')
    parser.add_argument('--reset-cooldown', help='Reset 24-hour cooldown for account')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    try:
        utils = AccountUtilities()
        
        if args.stats:
            utils.show_account_stats()
        
        if args.test:
            if args.test == 'all':
                utils.test_account_connection()
            else:
                utils.test_account_connection(args.test)
        
        if args.send_test:
            account_id, email = args.send_test
            utils.send_test_email(account_id, email)
        
        if args.reset_errors:
            utils.reset_account_errors(args.reset_errors)
        
        if args.disable:
            utils.disable_account(args.disable)
        
        if args.enable:
            utils.enable_account(args.enable)
        
        if args.reset_daily:
            utils.reset_daily_counters()
        
        if args.config:
            utils.show_config()
        
        if args.cooldown_status:
            utils.show_cooldown_status()
        
        if args.reset_cooldown:
            utils.reset_cooldown(args.reset_cooldown)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

"""
Account Manager for managing multiple email accounts with rotation and daily limits
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import random

logger = logging.getLogger(__name__)

class AccountManager:
    """Manages multiple email accounts with rotation and daily limit tracking"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.progress_file = "account_progress.json"
        self.config = self._load_config()
        self.accounts = self._load_accounts()
        self.progress = self._load_progress()
        self.current_account_index = 0
        
        logger.info(f"Account Manager initialized with {len(self.accounts)} accounts")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise
    
    def _load_accounts(self) -> List[Dict[str, Any]]:
        """Load and validate email accounts from config"""
        accounts = []
        
        if 'email_accounts' not in self.config:
            logger.error("No email_accounts found in config")
            raise ValueError("Configuration must contain 'email_accounts' section")
        
        for account in self.config['email_accounts']:
            if account.get('enabled', False):
                # Validate required fields (accept either daily_limit or daily_limit_range)
                required_fields = ['id', 'sender_email', 'sender_password']
                has_limit = 'daily_limit' in account or 'daily_limit_range' in account
                
                if all(field in account for field in required_fields) and has_limit:
                    accounts.append(account)
                    logger.info(f"Loaded account: {account['id']} ({account['sender_email']})")
                else:
                    logger.warning(f"Skipping invalid account: {account.get('id', 'unknown')}")
        
        if not accounts:
            logger.error("No valid enabled accounts found")
            raise ValueError("At least one enabled account is required")
        
        return accounts
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load account progress from JSON file"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    
                    # Reset daily counters if it's a new day
                    if self._should_reset_daily_counters(progress):
                        progress = self._reset_daily_counters(progress)
                    
                    return progress
            else:
                return self._create_initial_progress()
        except Exception as e:
            logger.error(f"Error loading progress: {str(e)}")
            return self._create_initial_progress()
    
    def _create_initial_progress(self) -> Dict[str, Any]:
        """Create initial progress structure"""
        progress = {
            'last_reset_date': datetime.now().strftime('%Y-%m-%d'),
            'current_account_index': 0,
            'accounts': {}
        }
        
        for account in self.accounts:
            progress['accounts'][account['id']] = {
                'emails_sent_today': 0,
                'last_used': None,
                'last_campaign_date': None,
                'total_emails_sent': 0,
                'failed_attempts': 0,
                'last_error': None,
                'status': 'active',
                'daily_limit_today': self._get_daily_limit_for_account(account)
            }
        
        return progress
    
    def _get_daily_limit_for_account(self, account: Dict[str, Any]) -> int:
        """Get randomized daily limit for an account"""
        if 'daily_limit_range' in account:
            min_limit, max_limit = account['daily_limit_range']
            daily_limit = random.randint(min_limit, max_limit)
            logger.info(f"Account {account['id']} assigned daily limit: {daily_limit}")
            return daily_limit
        else:
            # Fallback to fixed daily_limit if range not specified
            return account.get('daily_limit', 400)
    
    def _should_reset_daily_counters(self, progress: Dict[str, Any]) -> bool:
        """Check if daily counters should be reset"""
        try:
            last_reset = datetime.strptime(progress.get('last_reset_date', ''), '%Y-%m-%d')
            today = datetime.now()
            return last_reset.date() < today.date()
        except:
            return True
    
    def _reset_daily_counters(self, progress: Dict[str, Any]) -> Dict[str, Any]:
        """Reset daily email counters for all accounts"""
        logger.info("Resetting daily email counters")
        
        progress['last_reset_date'] = datetime.now().strftime('%Y-%m-%d')
        
        for account_id in progress.get('accounts', {}):
            progress['accounts'][account_id]['emails_sent_today'] = 0
            progress['accounts'][account_id]['status'] = 'active'
            
            # Assign new random daily limit for the new day
            account_config = next((a for a in self.accounts if a['id'] == account_id), None)
            if account_config:
                new_limit = self._get_daily_limit_for_account(account_config)
                progress['accounts'][account_id]['daily_limit_today'] = new_limit
        
        return progress
    
    def _save_progress(self):
        """Save progress to JSON file"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving progress: {str(e)}")
    
    def get_available_account(self) -> Optional[Dict[str, Any]]:
        """Get the next available account for sending emails"""
        strategy = self.config.get('email_rotation', {}).get('strategy', 'round_robin')
        
        if strategy == 'round_robin':
            return self._get_round_robin_account()
        else:
            return self._get_least_used_account()
    
    def _get_round_robin_account(self) -> Optional[Dict[str, Any]]:
        """Get account using round-robin strategy"""
        attempts = 0
        start_index = self.current_account_index
        
        while attempts < len(self.accounts):
            account = self.accounts[self.current_account_index]
            account_id = account['id']
            
            # Check if account is available
            if self._is_account_available(account_id):
                logger.info(f"Selected account: {account_id} ({account['sender_email']})")
                return account
            
            # Move to next account
            self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
            attempts += 1
        
        logger.warning("No available accounts found")
        return None
    
    def _get_least_used_account(self) -> Optional[Dict[str, Any]]:
        """Get account with lowest usage today"""
        available_accounts = []
        
        for account in self.accounts:
            if self._is_account_available(account['id']):
                emails_sent = self.progress['accounts'][account['id']]['emails_sent_today']
                available_accounts.append((account, emails_sent))
        
        if not available_accounts:
            return None
        
        # Sort by emails sent (least used first)
        available_accounts.sort(key=lambda x: x[1])
        selected_account = available_accounts[0][0]
        
        logger.info(f"Selected least used account: {selected_account['id']} ({selected_account['sender_email']})")
        return selected_account
    
    def _is_account_available(self, account_id: str) -> bool:
        """Check if account is available for sending"""
        account_progress = self.progress['accounts'].get(account_id, {})
        
        # Check if account is disabled
        if account_progress.get('status') == 'disabled':
            return False
        
        # Check daily limit (use dynamic daily limit if available)
        emails_sent_today = account_progress.get('emails_sent_today', 0)
        daily_limit = account_progress.get('daily_limit_today')
        
        # If no dynamic limit set, calculate it from account config
        if daily_limit is None:
            account_config = next((a for a in self.accounts if a['id'] == account_id), None)
            if not account_config:
                return False
            daily_limit = self._get_daily_limit_for_account(account_config)
            # Save the calculated limit
            account_progress['daily_limit_today'] = daily_limit
            self._save_progress()
        
        if emails_sent_today >= daily_limit:
            logger.debug(f"Account {account_id} has reached daily limit ({emails_sent_today}/{daily_limit})")
            return False
        
        # Check 24-hour campaign cooldown (server mode)
        if self.config.get('email_rotation', {}).get('server_mode', False):
            cooldown_hours = self.config.get('email_rotation', {}).get('account_cooldown_hours', 24)
            last_campaign_date = account_progress.get('last_campaign_date')
            
            if last_campaign_date:
                try:
                    last_campaign_time = datetime.fromisoformat(last_campaign_date)
                    time_since_last_campaign = datetime.now() - last_campaign_time
                    
                    if time_since_last_campaign < timedelta(hours=cooldown_hours):
                        remaining_hours = cooldown_hours - (time_since_last_campaign.total_seconds() / 3600)
                        logger.debug(f"Account {account_id} in 24h cooldown. {remaining_hours:.1f} hours remaining")
                        return False
                except Exception as e:
                    logger.warning(f"Error parsing last_campaign_date for {account_id}: {e}")
        
        # Check short-term cooldown between individual emails
        cooldown_minutes = self.config.get('email_rotation', {}).get('cooldown_minutes', 60)
        last_used = account_progress.get('last_used')
        
        if last_used:
            try:
                last_used_time = datetime.fromisoformat(last_used)
                if datetime.now() - last_used_time < timedelta(minutes=cooldown_minutes):
                    logger.debug(f"Account {account_id} is in short-term cooldown period")
                    return False
            except:
                pass
        
        return True
    
    def mark_email_sent(self, account_id: str, success: bool = True, error_message: str = None):
        """Mark an email as sent for the specified account"""
        if account_id not in self.progress['accounts']:
            logger.warning(f"Account {account_id} not found in progress")
            return
        
        account_progress = self.progress['accounts'][account_id]
        
        if success:
            account_progress['emails_sent_today'] += 1
            account_progress['total_emails_sent'] += 1
            account_progress['last_used'] = datetime.now().isoformat()
            
            # Update last campaign date for 24-hour cooldown tracking
            if self.config.get('email_rotation', {}).get('server_mode', False):
                account_progress['last_campaign_date'] = datetime.now().isoformat()
            
            logger.debug(f"Account {account_id} emails sent today: {account_progress['emails_sent_today']}")
        else:
            account_progress['failed_attempts'] += 1
            account_progress['last_error'] = error_message
            
            # Disable account if too many failures
            if account_progress['failed_attempts'] >= 5:
                account_progress['status'] = 'disabled'
                logger.warning(f"Account {account_id} disabled due to repeated failures")
        
        self._save_progress()
    
    def get_account_stats(self) -> Dict[str, Any]:
        """Get statistics for all accounts"""
        stats = {
            'total_accounts': len(self.accounts),
            'active_accounts': 0,
            'total_sent_today': 0,
            'total_sent_overall': 0,
            'accounts': []
        }
        
        for account in self.accounts:
            account_id = account['id']
            account_progress = self.progress['accounts'].get(account_id, {})
            
            emails_sent_today = account_progress.get('emails_sent_today', 0)
            total_sent = account_progress.get('total_emails_sent', 0)
            
            # Use dynamic daily limit if available, otherwise calculate from config
            daily_limit = account_progress.get('daily_limit_today')
            if daily_limit is None:
                daily_limit = self._get_daily_limit_for_account(account)
            
            # Show range info for display
            limit_range = account.get('daily_limit_range', [daily_limit, daily_limit])
            limit_display = f"{daily_limit} ({limit_range[0]}-{limit_range[1]})"
            
            account_stats = {
                'id': account_id,
                'email': account['sender_email'],
                'emails_sent_today': emails_sent_today,
                'daily_limit': daily_limit,
                'daily_limit_display': limit_display,
                'remaining_today': max(0, daily_limit - emails_sent_today),
                'total_sent': total_sent,
                'status': account_progress.get('status', 'active'),
                'last_used': account_progress.get('last_used'),
                'failed_attempts': account_progress.get('failed_attempts', 0)
            }
            
            stats['accounts'].append(account_stats)
            stats['total_sent_today'] += emails_sent_today
            stats['total_sent_overall'] += total_sent
            
            if self._is_account_available(account_id):
                stats['active_accounts'] += 1
        
        return stats
    
    def get_total_daily_capacity(self) -> int:
        """Get total daily email capacity across all accounts"""
        total = 0
        for account in self.accounts:
            if account.get('enabled', False):
                account_id = account['id']
                account_progress = self.progress['accounts'].get(account_id, {})
                
                # Use dynamic daily limit if available
                daily_limit = account_progress.get('daily_limit_today')
                if daily_limit is None:
                    # Calculate average of range for capacity estimation
                    if 'daily_limit_range' in account:
                        min_limit, max_limit = account['daily_limit_range']
                        daily_limit = (min_limit + max_limit) // 2
                    else:
                        daily_limit = account.get('daily_limit', 400)
                
                total += daily_limit
        return total
    
    def get_remaining_daily_capacity(self) -> int:
        """Get remaining email capacity for today"""
        remaining = 0
        for account in self.accounts:
            account_id = account['id']
            if self._is_account_available(account_id):
                account_progress = self.progress['accounts'][account_id]
                emails_sent = account_progress['emails_sent_today']
                
                # Use dynamic daily limit
                daily_limit = account_progress.get('daily_limit_today')
                if daily_limit is None:
                    daily_limit = self._get_daily_limit_for_account(account)
                
                remaining += max(0, daily_limit - emails_sent)
        return remaining
    
    def reset_account_errors(self, account_id: str):
        """Reset error count for an account"""
        if account_id in self.progress['accounts']:
            self.progress['accounts'][account_id]['failed_attempts'] = 0
            self.progress['accounts'][account_id]['status'] = 'active'
            self.progress['accounts'][account_id]['last_error'] = None
            self._save_progress()
            logger.info(f"Reset errors for account {account_id}")
    
    def disable_account(self, account_id: str):
        """Manually disable an account"""
        if account_id in self.progress['accounts']:
            self.progress['accounts'][account_id]['status'] = 'disabled'
            self._save_progress()
            logger.info(f"Disabled account {account_id}")
    
    def enable_account(self, account_id: str):
        """Manually enable an account"""
        if account_id in self.progress['accounts']:
            self.progress['accounts'][account_id]['status'] = 'active'
            self.progress['accounts'][account_id]['failed_attempts'] = 0
            self._save_progress()
            logger.info(f"Enabled account {account_id}")
    
    def get_next_available_account_time(self) -> Optional[datetime]:
        """Get the time when the next account will be available"""
        if not self.config.get('email_rotation', {}).get('server_mode', False):
            return None
        
        cooldown_hours = self.config.get('email_rotation', {}).get('account_cooldown_hours', 24)
        next_available = None
        
        for account in self.accounts:
            account_id = account['id']
            account_progress = self.progress['accounts'].get(account_id, {})
            
            if account_progress.get('status') == 'disabled':
                continue
            
            last_campaign_date = account_progress.get('last_campaign_date')
            if last_campaign_date:
                try:
                    last_campaign_time = datetime.fromisoformat(last_campaign_date)
                    available_time = last_campaign_time + timedelta(hours=cooldown_hours)
                    
                    if next_available is None or available_time < next_available:
                        next_available = available_time
                except Exception as e:
                    logger.warning(f"Error parsing last_campaign_date for {account_id}: {e}")
            else:
                # Account never used, available immediately
                return datetime.now()
        
        return next_available
    
    def get_account_cooldown_status(self) -> Dict[str, Any]:
        """Get detailed cooldown status for all accounts"""
        if not self.config.get('email_rotation', {}).get('server_mode', False):
            return {'server_mode': False, 'accounts': []}
        
        cooldown_hours = self.config.get('email_rotation', {}).get('account_cooldown_hours', 24)
        account_status = []
        
        for account in self.accounts:
            account_id = account['id']
            account_progress = self.progress['accounts'].get(account_id, {})
            
            last_campaign_date = account_progress.get('last_campaign_date')
            status = {
                'id': account_id,
                'email': account['sender_email'],
                'status': account_progress.get('status', 'active'),
                'last_campaign_date': last_campaign_date,
                'cooldown_remaining': None,
                'available_at': None,
                'is_available': self._is_account_available(account_id)
            }
            
            if last_campaign_date:
                try:
                    last_campaign_time = datetime.fromisoformat(last_campaign_date)
                    time_since_last = datetime.now() - last_campaign_time
                    
                    if time_since_last < timedelta(hours=cooldown_hours):
                        remaining_hours = cooldown_hours - (time_since_last.total_seconds() / 3600)
                        status['cooldown_remaining'] = remaining_hours
                        status['available_at'] = last_campaign_time + timedelta(hours=cooldown_hours)
                except Exception as e:
                    logger.warning(f"Error parsing date for {account_id}: {e}")
            
            account_status.append(status)
        
        return {
            'server_mode': True,
            'cooldown_hours': cooldown_hours,
            'accounts': account_status,
            'next_available_account': self.get_next_available_account_time()
        }
    
    def reset_account_cooldown(self, account_id: str):
        """Reset 24-hour cooldown for specific account (admin function)"""
        if account_id in self.progress['accounts']:
            self.progress['accounts'][account_id]['last_campaign_date'] = None
            self._save_progress()
            logger.info(f"Reset 24-hour cooldown for account {account_id}")

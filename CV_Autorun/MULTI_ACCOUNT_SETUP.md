# Multi-Account Setup Guide

## 🚀 Quick Start for Multiple Gmail Accounts

Your AutoEmailer system has been upgraded to support multiple Gmail accounts with automatic rotation, allowing you to send up to **2500+ emails per day** (5 accounts × 500 emails each).

## 📋 Prerequisites

1. **Multiple Gmail Accounts**: Create 2-5 Gmail accounts
2. **App Passwords**: Generate App Passwords for each Gmail account
3. **Updated Configuration**: Update your `config.json` with multiple accounts

## 🔧 Step-by-Step Setup

### Step 1: Create Gmail Accounts

Create additional Gmail accounts:
- `your_email_1@gmail.com`
- `your_email_2@gmail.com`
- `your_email_3@gmail.com`
- `your_email_4@gmail.com`
- `your_email_5@gmail.com`

### Step 2: Generate App Passwords

For each Gmail account:
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to Security → 2-Step Verification
3. Generate an App Password for "Mail"
4. Save each 16-character password

### Step 3: Update config.json

Replace your current `config.json` with the multi-account configuration:

```json
{
    "campaigns": {
        "default": {
            "name": "default",
            "template": "default",
            "batch_size": 50,
            "delay": 20,
            "test_mode": false
        }
    },
    "email_accounts": [
        {
            "id": "account_1",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "faltuwali01@gmail.com",
            "sender_password": "slbwpcxcgsnlhucq",
            "use_tls": true,
            "daily_limit": 500,
            "batch_delay": 20,
            "max_retries": 2,
            "enabled": true
        },
        {
            "id": "account_2",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "YOUR_SECOND_EMAIL@gmail.com",
            "sender_password": "YOUR_APP_PASSWORD_2",
            "use_tls": true,
            "daily_limit": 500,
            "batch_delay": 20,
            "max_retries": 2,
            "enabled": true
        },
        {
            "id": "account_3",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "YOUR_THIRD_EMAIL@gmail.com",
            "sender_password": "YOUR_APP_PASSWORD_3",
            "use_tls": true,
            "daily_limit": 500,
            "batch_delay": 20,
            "max_retries": 2,
            "enabled": true
        },
        {
            "id": "account_4",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "YOUR_FOURTH_EMAIL@gmail.com",
            "sender_password": "YOUR_APP_PASSWORD_4",
            "use_tls": true,
            "daily_limit": 500,
            "batch_delay": 20,
            "max_retries": 2,
            "enabled": true
        },
        {
            "id": "account_5",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "YOUR_FIFTH_EMAIL@gmail.com",
            "sender_password": "YOUR_APP_PASSWORD_5",
            "use_tls": true,
            "daily_limit": 500,
            "batch_delay": 20,
            "max_retries": 2,
            "enabled": true
        }
    ],
    "email_rotation": {
        "strategy": "round_robin",
        "cooldown_minutes": 60,
        "max_accounts": 10,
        "reset_daily_counters_at": "00:00"
    },
    "attachments": {
        "resume": "data/Ayush.pdf"
    }
}
```

### Step 4: Test Account Connections

Before running your campaign, test all accounts:

```bash
# Test all accounts
python src/account_utils.py --test

# View account statistics
python src/account_utils.py --stats

# Send test email
python src/account_utils.py --send-test account_1 your_test_email@gmail.com
```

### Step 5: Run Your Campaign

Now you can run campaigns with higher daily limits:

```bash
# Send up to 2500 emails per day with 5 accounts
python src/main.py --resume data/Ayush.pdf --batch-size 50 --daily-limit 2500
```

## 📊 New Features

### Account Statistics Dashboard
```bash
python src/account_utils.py --stats
```

Output:
```
============================================================
EMAIL ACCOUNT STATISTICS
============================================================
Total Accounts: 5
Active Accounts: 5
Total Daily Capacity: 2500
Remaining Daily Capacity: 2500
Emails Sent Today: 0
Total Emails Sent: 0

------------------------------------------------------------
INDIVIDUAL ACCOUNT STATUS
------------------------------------------------------------
✓ account_1    | faltuwali01@gmail.com        |   0/500 | active  
✓ account_2    | your_second@gmail.com        |   0/500 | active  
✓ account_3    | your_third@gmail.com         |   0/500 | active  
✓ account_4    | your_fourth@gmail.com        |   0/500 | active  
✓ account_5    | your_fifth@gmail.com         |   0/500 | active  
```

### Account Management Commands
```bash
# Reset error count for an account
python src/account_utils.py --reset-errors account_1

# Disable an account temporarily
python src/account_utils.py --disable account_2

# Enable an account
python src/account_utils.py --enable account_2

# Reset daily counters (useful for testing)
python src/account_utils.py --reset-daily
```

## 🔄 How Account Rotation Works

1. **Round Robin**: Cycles through accounts in order
2. **Daily Limits**: Each account respects Gmail's 500 email/day limit
3. **Cooldown**: 60-minute cooldown between account switches
4. **Error Handling**: Automatically disables accounts with 5+ failures
5. **Progress Tracking**: Separate tracking for each account

## 📈 Performance Benefits

- **5x Capacity**: Send 2500 emails/day instead of 500
- **Risk Distribution**: Spread emails across multiple accounts
- **Automatic Failover**: System continues if one account fails
- **Smart Rotation**: Prevents any single account from being overused

## 🛠️ Progress Files

The system now maintains two progress files:

1. **`campaign_progress.json`**: Overall campaign progress (company IDs)
2. **`account_progress.json`**: Per-account usage and statistics

## 🚨 Important Notes

- **Keep your existing first account**: Your current account is already configured
- **Test thoroughly**: Always test new accounts before running campaigns
- **Monitor logs**: Watch for account-specific errors or failures
- **Backup progress**: Both progress files are automatically backed up

## 🔧 Troubleshooting

### Account Not Working?
```bash
python src/account_utils.py --test account_1
```

### View Current Status?
```bash
python src/account_utils.py --stats
```

### Reset Everything?
```bash
python src/account_utils.py --reset-daily
```

## 🎯 Next Steps

1. **Set up 4 additional Gmail accounts**
2. **Generate App Passwords for each**
3. **Update your `config.json`**
4. **Test all accounts**
5. **Run campaign with `--daily-limit 2500`**

Your system is now ready for enterprise-scale email campaigns! 🚀

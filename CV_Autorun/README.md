# Cold Email Automation System

Automate personalized cold email campaigns at scale, track delivery, and synchronize campaign data with robust database management.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Loading Companies from Excel](#loading-companies-from-excel)
- [Sending Emails](#sending-emails)
- [Synchronizing Databases](#synchronizing-databases)
- [Other Utilities](#other-utilities)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Multi-Account Support**: Use up to 10 Gmail accounts with automatic rotation
- **Smart Rate Limiting**: Respects Gmail's 500 emails/day limit per account
- **Account Management**: Comprehensive CLI tools for account monitoring and management
- **Progress Tracking**: Separate progress tracking for campaigns and individual accounts
- **Error Handling**: Automatic account disabling on repeated failures
- **Scalable Architecture**: Easily add more accounts to increase daily capacity
- Load company and HR data from Excel into a database
- Send personalized emails in batches with rate limiting and error handling
- Track sent emails and campaign performance
- Synchronize and analyze campaign databases
- CLI-based workflow for automation and scripting

---

## Requirements

- Python 3.7+
- See `requirements.txt` for Python dependencies:
  - pandas, openpyxl, numpy, tqdm, pathlib2

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Edit `config.json` to set up your email credentials, campaign settings, and attachments. The system now supports multiple Gmail accounts with automatic rotation:

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
            "sender_email": "your_first_email@gmail.com",
            "sender_password": "your_app_password_1",
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
            "sender_email": "your_second_email@gmail.com",
            "sender_password": "your_app_password_2",
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
        "resume": "data/resume.pdf"
    }
}
```

### Multi-Account Features:

- **Account Rotation**: Automatically switches between accounts using round-robin or least-used strategy
- **Daily Limits**: Each account has its own daily email limit (default: 500 for Gmail)
- **Cooldown Periods**: Prevents overuse of individual accounts
- **Error Handling**: Automatically disables accounts with repeated failures
- **Scalable**: Supports up to 10 accounts (configurable)
- **Progress Tracking**: Separate progress tracking for each account

**Important:**  
- Use an [App Password](https://support.google.com/accounts/answer/185833) for Gmail or your provider's equivalent.
- Place your resume or other attachments in the specified path.

---

## Database Setup

### 1. Initialize the Email Tracking Database

Run the following command to create the `email_tracking.db` with required tables:

```bash
python src/init_email_tracking.py
```

### 2. (Optional) Manually Create/Verify Companies Database

The companies database (`companies.db`) is automatically created/updated when you load your Excel file (see next section).

---

## Loading Companies from Excel

Prepare your Excel file with at least the following columns:

- `company_name`
- `hr_email`

Other optional columns: `website`, `location`, `industry`, `company_size`, `founded_year`, `position`

**To load your Excel file into the database:**

```bash
python src/load_companies.py data/companies.xlsx
```

This will clear previous data and import the new list.

---

## Sending Emails

The main campaign script is `src/main.py`. It sends emails in batches, tracks progress, and updates both databases.

**Basic usage:**

```bash
python src/main.py --resume data/resume.pdf --batch-size 50 --daily-limit 2500
```

- `--resume`: Path to your resume or attachment (required)
- `--batch-size`: Number of emails to send in each batch (default: 50)
- `--daily-limit`: Maximum emails to send per day (can now exceed 500 with multiple accounts)
- `--background`: (Optional) Run in background mode

**Example with multiple accounts:**

```bash
python src/main.py --resume data/resume.pdf --batch-size 25 --daily-limit 2500
```

**Note:** With 5 Gmail accounts, you can now send up to 2500 emails per day (5 × 500).

## Account Management

The system includes a comprehensive account management utility:

### View Account Statistics

```bash
python src/account_utils.py --stats
```

Shows:
- Total accounts and active accounts
- Daily capacity and remaining capacity
- Individual account status and usage
- Failed attempts and last used timestamps

### Test Account Connections

```bash
# Test all accounts
python src/account_utils.py --test

# Test specific account
python src/account_utils.py --test account_1
```

### Send Test Email

```bash
python src/account_utils.py --send-test account_1 your_email@gmail.com
```

### Manage Accounts

```bash
# Reset error count for an account
python src/account_utils.py --reset-errors account_1

# Disable an account
python src/account_utils.py --disable account_2

# Enable an account
python src/account_utils.py --enable account_2

# Reset daily counters manually
python src/account_utils.py --reset-daily

# Show configuration
python src/account_utils.py --config
```

You can safely interrupt and resume the campaign; progress is saved.

---

## Synchronizing Databases

If you need to synchronize or fix inconsistencies between `companies.db` and `email_tracking.db`, use the following scripts:

### 1. Sync Databases

```bash
python src/sync_databases.py
```

This matches sent companies and updates records across both databases.

### 2. Verify Synchronization

```bash
python src/verify_sync.py
```

Prints a report of discrepancies and recent activity.

### 3. Fix Databases

```bash
python src/fix_databases.py
```

Attempts to fix common issues and align both databases.

---

## Other Utilities

- **Analyze Databases:**  
  ```bash
  python src/analyze_databases.py
  ```
  Prints stats, structure, and recent activity.

- **Check Remaining Companies:**  
  ```bash
  python src/check_remaining.py
  ```
  Shows how many companies are left to email.

- **Add Position Column:**  
  ```bash
  python src/add_position_column.py
  ```
  Adds a `position` column to the companies table if missing.

- **Sync Email Tracking Table:**  
  ```bash
  python src/sync_email_tracking.py
  ```
  Ensures all sent companies are reflected in the tracking table.

---

## Troubleshooting

- **Email not sending?**  
  - Check your SMTP credentials in `config.json`.
  - Make sure less secure app access is enabled or use an App Password.
  - Use `python src/account_utils.py --test` to test all account connections.
  - Check if accounts have reached their daily limits with `python src/account_utils.py --stats`.

- **Database errors?**  
  - Use the sync/fix scripts above.
  - Ensure your Excel file has the required columns.
  - Check `account_progress.json` for account-specific issues.

- **Progress not saving?**  
  - The campaign saves progress after each email. If interrupted, just rerun the command.
  - Both `campaign_progress.json` and `account_progress.json` are updated automatically.
  - Use `python src/account_utils.py --stats` to verify account progress.

## Multi-Account Progress Tracking

The system now maintains separate progress files:

- `campaign_progress.json`: Overall campaign progress
- `account_progress.json`: Per-account usage and statistics

### Account Progress Features:

- **Daily Reset**: Automatically resets daily counters at midnight
- **Account Status**: Tracks active/disabled status for each account
- **Error Tracking**: Monitors failed attempts and automatically disables problematic accounts
- **Usage Statistics**: Tracks total emails sent per account
- **Cooldown Management**: Prevents rapid switching between accounts

---

## Manually Updating Sent Status in companies.db

If you need to manually change the status of companies from `pending` to `sent` in the `companies` table (for example, if some emails were sent outside the system or you want to mark a batch as sent):

Use the following script:

```bash
python src/update_sent_emails.py
```

By default, this will mark all companies with IDs up to `0` as `sent` (see the script for the exact ID or modify it as needed). You can edit the script to change the target ID or adapt the logic for your needs.

This is useful if you want to update the status of a batch from `pending` to `sent` manually in the database.

**After updating statuses, you can synchronize the databases:**

```bash
python src/add_missing_companies.py
```

This will add any companies marked as sent in `companies.db` but missing in `email_tracking.db`, ensuring both databases are synchronized. Useful after manual status updates.

---

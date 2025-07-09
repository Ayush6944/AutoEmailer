# 🎯 Randomized Daily Limits Feature

## Overview

Your AutoEmailer system now uses **randomized daily limits** to make email sending more natural and reduce the risk of spam detection. Instead of all accounts using exactly 500 emails per day, each account gets a random limit between 400-450 emails daily.

## 🔧 Configuration

### Updated `config.json`:
```json
{
    "email_accounts": [
        {
            "id": "account_1",
            "sender_email": "faltuwali01@gmail.com",
            "sender_password": "your_app_password",
            "daily_limit_range": [400, 450],
            "enabled": true
        },
        {
            "id": "account_2", 
            "sender_email": "ayushsrivastava.sde@gmail.com",
            "sender_password": "your_app_password",
            "daily_limit_range": [400, 450],
            "enabled": true
        },
        {
            "id": "account_3",
            "sender_email": "ayushsrivastava.dev402@gmail.com", 
            "sender_password": "your_app_password",
            "daily_limit_range": [400, 450],
            "enabled": true
        }
    ]
}
```

## 🎲 How It Works

### Daily Limit Assignment
- Each morning at midnight, the system assigns a random daily limit to each account
- Range: 400-450 emails per account
- Each account gets a different random limit within this range

### Example Daily Limits:
- **Account 1**: 440 emails
- **Account 2**: 431 emails  
- **Account 3**: 449 emails
- **Total**: 1,320 emails/day

## 🛡️ Safety Benefits

### 1. **Avoids Detection Patterns**
- Gmail's spam detection looks for consistent patterns
- Random limits make sending behavior less predictable
- Each account appears to have different usage patterns

### 2. **More Natural Behavior**
- Real users don't send exactly the same number of emails daily
- Randomization mimics natural email usage patterns
- Reduces algorithmic fingerprinting risk

### 3. **Better Long-term Health**
- Accounts last longer with varied usage
- Reduces risk of mass account suspension
- Safer for high-volume campaigns

### 4. **Compliance Buffer**
- Staying under 450 emails provides safety margin
- Gmail's actual limit is 500, giving 50+ email buffer
- Reduces risk of hitting hard limits

## 📊 Statistics Display

The system now shows both the current daily limit and the configured range:

```
✓ account_1    | faltuwali01@gmail.com          |   0/440 (400-450) | active  
✓ account_2    | ayushsrivastava.sde@gmail.com  |   0/431 (400-450) | active  
✓ account_3    | ayushsrivastava.dev402@gmail.com |   0/449 (400-450) | active  
```

## 🚀 Usage

### Run Campaign with Dynamic Limits:
```bash
# The system will automatically use the randomized limits
python src/main.py --resume data/Ayush.pdf --batch-size 50 --daily-limit 1350
```

### Check Today's Limits:
```bash
python src/account_utils.py --stats
```

### Test Randomized Limits:
```bash
python test_randomized_limits.py
```

## 🔄 Daily Reset Process

1. **Midnight Reset**: System detects new day
2. **Random Assignment**: Each account gets new random limit (400-450)
3. **Logging**: New limits are logged for transparency
4. **Capacity Update**: Total daily capacity recalculated

## 📈 Expected Capacity

- **Minimum**: 1,200 emails/day (3 × 400)
- **Maximum**: 1,350 emails/day (3 × 450)
- **Average**: 1,275 emails/day (3 × 425)

## 🎯 Recommended Usage

### Conservative Approach:
```bash
python src/main.py --resume data/Ayush.pdf --daily-limit 1200
```

### Optimal Approach:
```bash
python src/main.py --resume data/Ayush.pdf --daily-limit 1300
```

### Maximum Approach:
```bash
python src/main.py --resume data/Ayush.pdf --daily-limit 1350
```

## 🔧 Customization

### Change the Range:
```json
"daily_limit_range": [350, 400]  // More conservative
"daily_limit_range": [450, 500]  // More aggressive
```

### Per-Account Ranges:
```json
{
    "id": "account_1",
    "daily_limit_range": [400, 450]
},
{
    "id": "account_2", 
    "daily_limit_range": [350, 400]  // More conservative account
}
```

## 📝 Log Examples

```
2025-07-10 01:37:44,284 - account_manager - INFO - Account account_1 assigned daily limit: 440
2025-07-10 01:37:44,284 - account_manager - INFO - Account account_2 assigned daily limit: 431
2025-07-10 01:37:44,284 - account_manager - INFO - Account account_3 assigned daily limit: 449
```

## 🎉 Benefits Summary

- ✅ **Safer**: Randomized limits avoid detection patterns
- ✅ **Smarter**: Each account gets appropriate daily limit
- ✅ **Scalable**: Easy to adjust ranges for different risk levels
- ✅ **Transparent**: Clear logging of daily limit assignments
- ✅ **Automatic**: No manual intervention required

Your AutoEmailer system is now significantly safer and more sophisticated! 🚀

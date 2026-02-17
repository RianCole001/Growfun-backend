# 🔧 Admin Settings API - Complete Documentation

## 🎯 Overview

The Admin Settings system allows platform administrators to control all platform-wide settings including transaction limits, fees, automation rules, and more.

---

## 📊 Database Model

### PlatformSettings
```python
{
    "platformName": "GrowFund",
    "platformEmail": "support@growfund.com",
    "maintenanceMode": false,
    
    # Transaction Limits
    "minDeposit": 100.00,
    "maxDeposit": 100000.00,
    "minWithdrawal": 50.00,
    "maxWithdrawal": 50000.00,
    
    # Fees (Percentage)
    "depositFee": 0.00,
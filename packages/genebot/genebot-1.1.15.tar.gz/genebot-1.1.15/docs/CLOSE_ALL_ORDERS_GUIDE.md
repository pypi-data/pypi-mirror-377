# GeneBot Close All Orders Guide

## 🛑 **Safe Order Closure System**

The `close-all-orders` command provides a safe and controlled way to close all open orders across your trading accounts. This feature is designed with multiple safety mechanisms to protect your trading positions and ensure proper trade completion.

---

## 🎯 **Command Overview**

```bash
genebot close-all-orders [OPTIONS]
```

### **Available Options**

| Option | Description | Default |
|--------|-------------|---------|
| `--force` | Force close without waiting for strategy completion | `False` |
| `--timeout SECONDS` | Maximum time to wait for strategies (seconds) | `300` |
| `--account NAME` | Close orders for specific account only | `All accounts` |

---

## 🔒 **Safety Mechanisms**

### **1. Pre-Closure Validation**
- ✅ Validates all trading accounts before proceeding
- ✅ Checks account connectivity and permissions
- ✅ Verifies open orders exist before attempting closure
- ✅ Ensures trading bot is in a stable state

### **2. Strategy Completion Wait**
- ⏳ Waits for active strategies to complete current trades
- 📊 Ensures proper P&L calculation and trade logging
- ⏰ Respects timeout settings to prevent indefinite waiting
- 🚫 Prevents new orders from being placed during closure

### **3. Sequential Order Closure**
- 🔄 Closes orders one by one (not in parallel)
- ✅ Validates each closure before proceeding to next
- 🔄 Implements retry logic for failed closures
- 📋 Maintains detailed closure log

### **4. User Confirmation**
- 🤔 Requires explicit user confirmation (`CLOSE ALL`)
- ⚠️ Shows detailed impact assessment before proceeding
- 🏦 Lists all affected accounts and order counts
- 🛡️ Prevents accidental execution

---

## 📋 **Usage Examples**

### **Basic Usage**
```bash
# Close all orders with strategy completion wait
genebot close-all-orders
```

**What happens:**
1. Validates all active accounts
2. Waits for strategies to complete (up to 5 minutes)
3. Closes all open orders sequentially
4. Generates comprehensive closure report

### **Force Mode**
```bash
# Immediate closure without waiting
genebot close-all-orders --force
```

**What happens:**
1. Immediately stops all strategies
2. Closes all open orders without waiting
3. Faster execution but may interrupt active trades

### **Account-Specific Closure**
```bash
# Close orders for specific account only
genebot close-all-orders --account binance-demo
```

**What happens:**
1. Validates the specified account exists and is active
2. Closes orders only for that account
3. Other accounts remain unaffected

### **Custom Timeout**
```bash
# Wait up to 10 minutes for strategy completion
genebot close-all-orders --timeout 600
```

**What happens:**
1. Extends the strategy completion wait time
2. Useful for complex strategies that need more time
3. Proceeds with closure after timeout regardless

### **Combined Options**
```bash
# Force close specific account with custom timeout
genebot close-all-orders --account oanda-demo --timeout 120 --force
```

---

## 🔄 **Process Flow**

### **Step 1: Validation Phase**
```
🔍 Pre-closure validation...
🏦 Trading Account Validation:
========================================
🔍 Testing account connectivity...

✅ binance-demo (crypto) - Ready
✅ oanda-demo (forex) - Ready
✅ coinbase-demo (crypto) - Ready

📊 Account Validation Summary:
  Total Accounts: 3
  Valid & Ready: 3
```

### **Step 2: Impact Assessment**
```
⚠️  CRITICAL OPERATION WARNING
This will close ALL open orders across ALL active accounts.

🏦 Affected Accounts:
  • binance-demo - crypto (Demo)
  • oanda-demo - forex (Demo)
  • coinbase-demo - crypto (Demo)

⏱️  Process Configuration:
  • Force Mode: No (Wait for strategy completion)
  • Timeout: 300 seconds
  • Accounts: 3
```

### **Step 3: User Confirmation**
```
🤔 This operation will:
  1. Wait for active strategies to complete current trades
  2. Prevent new orders from being placed
  3. Close all remaining open orders sequentially
  4. Generate a closure report

Are you sure you want to proceed? (type 'CLOSE ALL' to confirm):
```

### **Step 4: Strategy Completion Wait**
```
🚀 Starting order closure process...

⏳ Waiting for active strategies to complete...
   This ensures trades are properly closed and P&L is calculated
   Still waiting for 2 strategies...
✅ All strategies completed successfully
```

### **Step 5: Sequential Order Closure**
```
🔄 Processing binance-demo (crypto)...
  📋 Found 3 open orders
  🛑 Closing ORD_1001 (BTC/USDT BUY 0.1)...
    ✅ Closed successfully
  🛑 Closing ORD_1002 (ETH/USDT SELL 2.5)...
    ✅ Closed successfully
  🛑 Closing ORD_1003 (ADA/USDT BUY 1000)...
    ✅ Closed successfully
  📊 Account Summary: 3/3 orders closed

🔄 Processing oanda-demo (forex)...
  📋 Found 2 open orders
  🛑 Closing ORD_2001 (EUR/USD BUY 10000)...
    ✅ Closed successfully
  🛑 Closing ORD_2002 (GBP/USD SELL 5000)...
    ✅ Closed successfully
  📊 Account Summary: 2/2 orders closed
```

### **Step 6: Closure Report**
```
📊 Order Closure Complete!
========================================
✅ Total Orders Closed: 5
🏦 Accounts Processed: 2
⏱️  Total Time: 45 seconds

📋 Detailed Closure Report:
✅ Successfully Closed (5):
  • binance-demo: ORD_1001 (BTC/USDT BUY)
  • binance-demo: ORD_1002 (ETH/USDT SELL)
  • binance-demo: ORD_1003 (ADA/USDT BUY)
  • oanda-demo: ORD_2001 (EUR/USD BUY)
  • oanda-demo: ORD_2002 (GBP/USD SELL)

🔒 Post-Closure Actions:
  • All strategies have been paused
  • No new orders will be placed
  • Account balances preserved
  • Trading can be resumed with 'genebot start'
```

---

## ⚠️ **Important Considerations**

### **When to Use Close All Orders**

✅ **Recommended Scenarios:**
- End of trading session
- System maintenance
- Strategy reconfiguration
- Risk management (market volatility)
- Account rebalancing
- Emergency situations

❌ **Not Recommended:**
- During active market opportunities
- When strategies are performing well
- For routine position adjustments
- When unsure about market conditions

### **Force Mode Considerations**

⚡ **Use Force Mode When:**
- Strategies are stuck or unresponsive
- Emergency market conditions
- System errors preventing normal closure
- Time-critical situations

⚠️ **Force Mode Risks:**
- May interrupt profitable trades
- Could result in suboptimal exit prices
- Bypasses normal risk management
- May cause incomplete trade logging

### **Account-Specific Closure**

🎯 **Use Account-Specific When:**
- Issues with specific exchange/broker
- Maintenance on particular platform
- Testing closure process
- Selective risk management

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"No active accounts found"**
```bash
❌ No active accounts found!
Cannot close orders without active trading accounts.
```

**Solution:**
1. Check account configuration: `genebot list-accounts`
2. Validate accounts: `genebot validate-accounts`
3. Enable disabled accounts: `genebot enable-account <name>`

#### **"Account not found"**
```bash
❌ Account 'invalid-account' not found or not active!
Available accounts:
  • binance-demo (crypto)
  • oanda-demo (forex)
```

**Solution:**
1. Check available accounts: `genebot list-accounts`
2. Use correct account name
3. Ensure account is enabled and validated

#### **"Strategy completion timeout"**
```bash
⏰ Timeout reached (300s) - proceeding with closure
```

**Solution:**
1. Use longer timeout: `--timeout 600`
2. Use force mode if strategies are stuck: `--force`
3. Check strategy status: `genebot status`

#### **"Failed to close some orders"**
```bash
❌ Failed to Close (2):
  • binance-demo: ORD_1001 (BTC/USDT BUY)
  • oanda-demo: ORD_2001 (EUR/USD SELL)

💡 Retry failed closures with:
   genebot close-all-orders --force
```

**Solution:**
1. Retry with force mode: `genebot close-all-orders --force`
2. Check account connectivity: `genebot validate-accounts`
3. Manual closure via exchange/broker interface
4. Contact support if issues persist

---

## 📊 **Best Practices**

### **Pre-Closure Checklist**

1. **📋 Review Open Positions**
   ```bash
   genebot trades
   genebot status
   ```

2. **🔍 Validate System State**
   ```bash
   genebot validate
   ```

3. **💾 Backup Configuration**
   ```bash
   genebot backup-config
   ```

4. **📊 Generate Pre-Closure Report**
   ```bash
   genebot report detailed
   ```

### **Post-Closure Actions**

1. **✅ Verify All Orders Closed**
   - Check exchange/broker interfaces
   - Review closure report
   - Confirm account balances

2. **📊 Generate Final Report**
   ```bash
   genebot report performance
   ```

3. **💾 Save Closure Log**
   - Document closure reason
   - Save closure report
   - Note any issues encountered

4. **🔄 Plan Resumption**
   - Review strategy performance
   - Adjust configurations if needed
   - Plan restart timing

---

## 🚨 **Emergency Procedures**

### **Emergency Closure**
```bash
# Immediate closure of all orders
genebot close-all-orders --force --timeout 60
```

### **Partial Emergency Closure**
```bash
# Close orders for problematic account only
genebot close-all-orders --account problematic-account --force
```

### **If Command Fails**
1. **Manual Closure**: Use exchange/broker web interfaces
2. **Contact Support**: Reach out to exchange/broker support
3. **System Restart**: `genebot restart` and retry
4. **Force Stop**: `genebot stop` to halt all trading

---

## 📞 **Support**

If you encounter issues with the close-all-orders command:

- 📖 **Documentation**: This guide and `genebot config-help`
- 🐛 **Bug Reports**: GitHub Issues
- 💬 **Community**: GitHub Discussions
- 📧 **Email**: support@genebot.ai

---

**Remember: The close-all-orders command is a powerful tool designed for your safety. Always use it thoughtfully and understand the implications before proceeding.** 🛡️
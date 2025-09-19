#!/usr/bin/env python3
"""
GeneBot Close All Orders Example
===============================

This example demonstrates how to use the close-all-orders command
and shows the safety mechanisms in place.

Usage Examples:
    # Basic usage - close all orders with strategy completion wait
    genebot close-all-orders
    
    # Force mode - immediate closure without waiting
    genebot close-all-orders --force
    
    # Close orders for specific account only
    genebot close-all-orders --account binance-demo
    
    # Custom timeout (default is 300 seconds)
    genebot close-all-orders --timeout 600
    
    # Combination of options
    genebot close-all-orders --account oanda-demo --timeout 120 --force
"""

import sys
import os
import time
from typing import List, Dict, Any, Tuple

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class OrderClosureManager:
    """
    Manages the safe closure of all open orders across trading accounts.
    
    This class implements the core logic for the close-all-orders command,
    including strategy completion waiting, sequential order closure, and
    comprehensive reporting.
    """
    
    def __init__(self, timeout: int = 300, force_mode: bool = False):
        """
        Initialize the order closure manager.
        
        Args:
            timeout: Maximum time to wait for strategy completion (seconds)
            force_mode: If True, close orders immediately without waiting
        """
        self.timeout = timeout
        self.force_mode = force_mode
        self.closure_report = []
        
    def validate_accounts(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Validate all configured trading accounts.
        
        Returns:
            Tuple of (valid_accounts, invalid_accounts, disabled_accounts)
        """
        # Mock implementation - in real system, this would:
        # 1. Read account configuration
        # 2. Test connectivity to each exchange/broker
        # 3. Verify API permissions
        # 4. Check account status
        
        mock_accounts = [
            {
                'name': 'binance-demo',
                'type': 'crypto',
                'exchange': 'binance',
                'enabled': True,
                'sandbox': True,
                'has_open_orders': True
            },
            {
                'name': 'oanda-demo',
                'type': 'forex',
                'broker': 'oanda',
                'enabled': True,
                'sandbox': True,
                'has_open_orders': True
            },
            {
                'name': 'coinbase-demo',
                'type': 'crypto',
                'exchange': 'coinbase',
                'enabled': True,
                'sandbox': True,
                'has_open_orders': False
            }
        ]
        
        valid_accounts = [acc for acc in mock_accounts if acc['enabled']]
        invalid_accounts = []
        disabled_accounts = [acc for acc in mock_accounts if not acc['enabled']]
        
        return valid_accounts, invalid_accounts, disabled_accounts
    
    def wait_for_strategy_completion(self, accounts: List[Dict]) -> bool:
        """
        Wait for active strategies to complete their current trades.
        
        Args:
            accounts: List of accounts to check
            
        Returns:
            True if all strategies completed, False if timeout occurred
        """
        if self.force_mode:
            print("⚡ Force mode enabled - skipping strategy completion wait")
            return True
        
        print("⏳ Waiting for active strategies to complete...")
        print("   This ensures trades are properly closed and P&L is calculated")
        
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            # Mock strategy checking - in real system, this would:
            # 1. Query each strategy's current state
            # 2. Check for pending trades
            # 3. Verify no critical operations in progress
            
            active_strategies = self._check_active_strategies(accounts)
            
            if not active_strategies:
                print("✅ All strategies completed successfully")
                return True
            
            print(f"   Still waiting for {len(active_strategies)} strategies...")
            time.sleep(5)  # Check every 5 seconds
        
        print(f"⏰ Timeout reached ({self.timeout}s) - proceeding with closure")
        return False
    
    def _check_active_strategies(self, accounts: List[Dict]) -> List[str]:
        """
        Check which strategies are still active.
        
        Args:
            accounts: List of accounts to check
            
        Returns:
            List of active strategy names
        """
        # Mock implementation - randomly simulate strategies completing
        import random
        
        # Simulate strategies gradually completing
        if random.random() < 0.3:  # 30% chance of completion each check
            return []  # All strategies completed
        else:
            return ['RSI_Strategy', 'MA_Crossover']  # Some still active
    
    def get_open_orders(self, account: Dict) -> List[Dict]:
        """
        Get all open orders for a specific account.
        
        Args:
            account: Account configuration
            
        Returns:
            List of open orders
        """
        # Mock implementation - in real system, this would:
        # 1. Connect to the exchange/broker API
        # 2. Fetch all open orders
        # 3. Filter by order status
        
        if not account.get('has_open_orders', False):
            return []
        
        import random
        
        mock_orders = [
            {
                'id': f'ORD_{random.randint(1000, 9999)}',
                'pair': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.1,
                'price': 45000.0,
                'type': 'LIMIT'
            },
            {
                'id': f'ORD_{random.randint(1000, 9999)}',
                'pair': 'ETH/USDT',
                'side': 'SELL',
                'amount': 2.5,
                'price': 3000.0,
                'type': 'LIMIT'
            }
        ]
        
        # Return 0-3 random orders
        return random.sample(mock_orders, random.randint(0, len(mock_orders)))
    
    def close_order(self, account: Dict, order: Dict) -> bool:
        """
        Close a specific order.
        
        Args:
            account: Account configuration
            order: Order to close
            
        Returns:
            True if successful, False otherwise
        """
        # Mock implementation - in real system, this would:
        # 1. Connect to the exchange/broker API
        # 2. Send cancel order request
        # 3. Verify cancellation
        # 4. Handle any errors
        
        print(f"    🛑 Closing {order['id']} ({order['pair']} {order['side']} {order['amount']})...")
        
        # Simulate API call delay
        time.sleep(0.5)
        
        # Simulate 95% success rate
        import random
        success = random.random() < 0.95
        
        if success:
            print(f"      ✅ Closed successfully")
            self.closure_report.append({
                'account': account['name'],
                'order_id': order['id'],
                'pair': order['pair'],
                'side': order['side'],
                'amount': order['amount'],
                'status': 'CLOSED',
                'timestamp': time.time()
            })
        else:
            print(f"      ❌ Failed to close (will retry)")
            self.closure_report.append({
                'account': account['name'],
                'order_id': order['id'],
                'pair': order['pair'],
                'side': order['side'],
                'amount': order['amount'],
                'status': 'FAILED',
                'timestamp': time.time()
            })
        
        return success
    
    def close_all_orders_for_account(self, account: Dict) -> Tuple[int, int]:
        """
        Close all orders for a specific account.
        
        Args:
            account: Account configuration
            
        Returns:
            Tuple of (successful_closures, total_orders)
        """
        account_name = account['name']
        account_type = account.get('type', 'unknown')
        
        print(f"🔄 Processing {account_name} ({account_type})...")
        
        # Get all open orders
        open_orders = self.get_open_orders(account)
        
        if not open_orders:
            print(f"  📋 No open orders found")
            return 0, 0
        
        print(f"  📋 Found {len(open_orders)} open orders")
        
        successful_closures = 0
        
        # Close orders sequentially (not in parallel for safety)
        for order in open_orders:
            if self.close_order(account, order):
                successful_closures += 1
        
        print(f"  📊 Account Summary: {successful_closures}/{len(open_orders)} orders closed")
        return successful_closures, len(open_orders)
    
    def close_all_orders(self, target_account: str = None) -> Dict[str, Any]:
        """
        Close all open orders across all accounts or a specific account.
        
        Args:
            target_account: If specified, only close orders for this account
            
        Returns:
            Dictionary with closure results
        """
        print("🚀 Starting order closure process...")
        print()
        
        # Validate accounts
        valid_accounts, invalid_accounts, disabled_accounts = self.validate_accounts()
        
        if not valid_accounts:
            return {
                'success': False,
                'error': 'No active accounts found',
                'total_closed': 0,
                'total_orders': 0
            }
        
        # Filter to specific account if requested
        if target_account:
            target_accounts = [acc for acc in valid_accounts if acc['name'] == target_account]
            if not target_accounts:
                return {
                    'success': False,
                    'error': f'Account {target_account} not found or not active',
                    'total_closed': 0,
                    'total_orders': 0
                }
            accounts_to_process = target_accounts
        else:
            accounts_to_process = valid_accounts
        
        # Wait for strategy completion
        strategies_completed = self.wait_for_strategy_completion(accounts_to_process)
        
        # Close orders for each account
        total_closed = 0
        total_orders = 0
        
        for account in accounts_to_process:
            closed, orders = self.close_all_orders_for_account(account)
            total_closed += closed
            total_orders += orders
            print()  # Add spacing between accounts
        
        return {
            'success': True,
            'total_closed': total_closed,
            'total_orders': total_orders,
            'accounts_processed': len(accounts_to_process),
            'strategies_completed': strategies_completed,
            'closure_report': self.closure_report
        }
    
    def generate_closure_report(self, results: Dict[str, Any]) -> None:
        """
        Generate and display a comprehensive closure report.
        
        Args:
            results: Results from close_all_orders operation
        """
        print("📊 Order Closure Complete!")
        print("=" * 40)
        print(f"✅ Total Orders Closed: {results['total_closed']}")
        print(f"📋 Total Orders Found: {results['total_orders']}")
        print(f"🏦 Accounts Processed: {results['accounts_processed']}")
        print(f"⏱️  Strategies Completed: {'Yes' if results['strategies_completed'] else 'Timeout'}")
        print()
        
        if self.closure_report:
            successful_closures = [r for r in self.closure_report if r['status'] == 'CLOSED']
            failed_closures = [r for r in self.closure_report if r['status'] == 'FAILED']
            
            if successful_closures:
                print(f"✅ Successfully Closed ({len(successful_closures)}):")
                for report in successful_closures:
                    print(f"  • {report['account']}: {report['order_id']} ({report['pair']} {report['side']})")
                print()
            
            if failed_closures:
                print(f"❌ Failed to Close ({len(failed_closures)}):")
                for report in failed_closures:
                    print(f"  • {report['account']}: {report['order_id']} ({report['pair']} {report['side']})")
                print()
                print("💡 Retry failed closures with:")
                print("   genebot close-all-orders --force")
        
        print("🔒 Post-Closure Actions:")
        print("  • All strategies have been paused")
        print("  • No new orders will be placed")
        print("  • Account balances preserved")
        print("  • Trading can be resumed with 'genebot start'")


def demonstrate_close_all_orders():
    """Demonstrate the close-all-orders functionality."""
    print("🎯 GeneBot Close All Orders Demonstration")
    print("=" * 50)
    print()
    
    # Example 1: Basic closure
    print("📋 Example 1: Basic Order Closure")
    print("-" * 30)
    manager = OrderClosureManager(timeout=60, force_mode=False)
    results = manager.close_all_orders()
    manager.generate_closure_report(results)
    print()
    
    # Example 2: Force mode
    print("📋 Example 2: Force Mode Closure")
    print("-" * 30)
    manager_force = OrderClosureManager(timeout=60, force_mode=True)
    results_force = manager_force.close_all_orders()
    manager_force.generate_closure_report(results_force)
    print()
    
    # Example 3: Account-specific closure
    print("📋 Example 3: Account-Specific Closure")
    print("-" * 30)
    manager_specific = OrderClosureManager(timeout=60, force_mode=False)
    results_specific = manager_specific.close_all_orders(target_account='binance-demo')
    manager_specific.generate_closure_report(results_specific)


if __name__ == '__main__':
    demonstrate_close_all_orders()
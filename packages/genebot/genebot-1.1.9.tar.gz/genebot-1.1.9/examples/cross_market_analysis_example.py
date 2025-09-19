"""
Cross-Market Analysis Example

This example demonstrates the cross-market analysis capabilities including:
- Correlation analysis between crypto and forex markets
- Arbitrage opportunity detection
- Cross-market event analysis and impact assessment
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

# Add parent directory to path for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import analysis modules
from src.analysis.correlation_analyzer import CrossMarketCorrelationAnalyzer
from src.analysis.arbitrage_detector import ArbitrageDetector
from src.analysis.event_analyzer import CrossMarketEventAnalyzer, EventType, EventSeverity

# Import data models and types
from src.models.data_models import UnifiedMarketData
from src.markets.types import MarketType, UnifiedSymbol
from src.data.cross_market_store import CrossMarketDataStore
from src.database.connection import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockDataStore:
    """Mock data store for demonstration purposes."""
    
    def __init__(self):
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate sample market data for demonstration."""
        data = {}
        
        # BTC/USD crypto data
        btc_symbol = UnifiedSymbol(
            base_asset='BTC',
            quote_asset='USD',
            market_type=MarketType.CRYPTO,
            native_symbol='BTCUSD'
        )
        
        # EUR/USD forex data
        eur_symbol = UnifiedSymbol(
            base_asset='EUR',
            quote_asset='USD',
            market_type=MarketType.FOREX,
            native_symbol='EURUSD'
        )
        
        # Generate correlated sample data
        base_time = datetime.now() - timedelta(days=30)
        btc_data = []
        eur_data = []
        
        for i in range(100):
            timestamp = base_time + timedelta(hours=i * 6)
            
            # Generate somewhat correlated prices
            btc_base = 50000
            eur_base = 1.1
            
            # Add some correlation and noise
            market_factor = 0.02 * (i % 20 - 10)  # Market cycle
            btc_price = btc_base * (1 + market_factor + 0.01 * (i % 7 - 3))
            eur_price = eur_base * (1 + market_factor * 0.3 + 0.005 * (i % 5 - 2))
            
            btc_data.append(UnifiedMarketData(
                symbol=btc_symbol,
                timestamp=timestamp,
                open=Decimal(str(btc_price * 0.999)),
                high=Decimal(str(btc_price * 1.002)),
                low=Decimal(str(btc_price * 0.998)),
                close=Decimal(str(btc_price)),
                volume=Decimal('1000'),
                source='crypto_exchange',
                market_type=MarketType.CRYPTO
            ))
            
            eur_data.append(UnifiedMarketData(
                symbol=eur_symbol,
                timestamp=timestamp,
                open=Decimal(str(eur_price * 0.9999)),
                high=Decimal(str(eur_price * 1.0002)),
                low=Decimal(str(eur_price * 0.9998)),
                close=Decimal(str(eur_price)),
                volume=Decimal('10000'),
                source='forex_broker',
                market_type=MarketType.FOREX
            ))
        
        data[btc_symbol] = btc_data
        data[eur_symbol] = eur_data
        
        return data
    
    async def get_unified_data(self, symbol, start_time, end_time):
        """Mock method to get unified data."""
        if symbol in self.sample_data:
            return [
                d for d in self.sample_data[symbol]
                if start_time <= d.timestamp <= end_time
            ]
        return []
    
    async def get_latest_data(self, symbol):
        """Mock method to get latest data."""
        if symbol in self.sample_data and self.sample_data[symbol]:
            return self.sample_data[symbol][-1]
        return None
    
    async def store_correlation_data(self, symbol1, symbol2, correlation, period_days):
        """Mock method to store correlation data."""
        logger.info(f"Stored correlation: {symbol1.to_standard_format()} vs {symbol2.to_standard_format()} = {correlation:.4f}")
        return True


async def demonstrate_correlation_analysis():
    """Demonstrate cross-market correlation analysis."""
    logger.info("=== Cross-Market Correlation Analysis Demo ===")
    
    # Setup
    mock_store = MockDataStore()
    config = {
        'min_observations': 10,
        'significance_level': 0.05,
        'rolling_window_days': 30,
        'trend_detection_periods': 5
    }
    
    analyzer = CrossMarketCorrelationAnalyzer(mock_store, config)
    
    # Create symbols
    btc_symbol = UnifiedSymbol(
        base_asset='BTC',
        quote_asset='USD',
        market_type=MarketType.CRYPTO,
        native_symbol='BTCUSD'
    )
    
    eur_symbol = UnifiedSymbol(
        base_asset='EUR',
        quote_asset='USD',
        market_type=MarketType.FOREX,
        native_symbol='EURUSD'
    )
    
    # Analyze correlation between BTC and EUR
    logger.info("Analyzing correlation between BTC/USD and EUR/USD...")
    correlation_result = await analyzer.analyze_correlation(btc_symbol, eur_symbol)
    
    if correlation_result:
        logger.info(f"Correlation Result:")
        logger.info(f"  Pearson Correlation: {correlation_result.pearson_correlation:.4f}")
        logger.info(f"  Spearman Correlation: {correlation_result.spearman_correlation:.4f}")
        logger.info(f"  P-value: {correlation_result.p_value:.4f}")
        logger.info(f"  Significance: {'Yes' if correlation_result.is_significant else 'No'}")
        logger.info(f"  Strength: {correlation_result.correlation_strength}")
        logger.info(f"  Sample Size: {correlation_result.sample_size}")
    
    # Analyze correlation matrix
    logger.info("\nCalculating correlation matrix...")
    symbols = [btc_symbol, eur_symbol]
    matrix = await analyzer.analyze_correlation_matrix(symbols)
    
    logger.info("Correlation Matrix:")
    for sym1, correlations in matrix.items():
        for sym2, corr in correlations.items():
            if sym1 != sym2:
                logger.info(f"  {sym1} vs {sym2}: {corr:.4f}")
    
    # Get correlation insights
    logger.info("\nGenerating correlation insights...")
    insights = analyzer.get_correlation_insights(symbols)
    
    logger.info("Correlation Insights:")
    logger.info(f"  Total Symbols: {insights.get('total_symbols', 0)}")
    logger.info(f"  High Correlations: {len(insights.get('high_correlations', []))}")
    logger.info(f"  Diversification Score: {insights.get('diversification_score', 0):.2f}")
    
    # Test correlation-adjusted position sizing
    logger.info("\nTesting correlation-adjusted position sizing...")
    base_size = 1000.0
    portfolio_symbols = [eur_symbol]
    
    adjusted_size = analyzer.calculate_correlation_adjusted_position_size(
        base_size, btc_symbol, portfolio_symbols
    )
    
    logger.info(f"Position Size Adjustment:")
    logger.info(f"  Base Size: ${base_size:,.2f}")
    logger.info(f"  Adjusted Size: ${adjusted_size:,.2f}")
    logger.info(f"  Adjustment: {((adjusted_size - base_size) / base_size * 100):+.1f}%")


async def demonstrate_arbitrage_detection():
    """Demonstrate arbitrage opportunity detection."""
    logger.info("\n=== Arbitrage Detection Demo ===")
    
    # Setup
    mock_store = MockDataStore()
    config = {
        'min_profit_threshold': 0.001,
        'max_execution_time_seconds': 30,
        'min_volume_threshold': 1000,
        'max_spread_age_seconds': 10,
        'market_fees': {
            'exchange1': 0.001,
            'exchange2': 0.0015
        }
    }
    
    detector = ArbitrageDetector(mock_store, config)
    
    # Create sample symbols
    btc_symbol = UnifiedSymbol(
        base_asset='BTC',
        quote_asset='USD',
        market_type=MarketType.CRYPTO,
        native_symbol='BTCUSD'
    )
    
    # Create mock price discrepancy
    from src.analysis.arbitrage_detector import PriceDiscrepancy
    
    discrepancy = PriceDiscrepancy(
        symbol=btc_symbol,
        market1='exchange1',
        market2='exchange2',
        price1=Decimal('50000'),
        price2=Decimal('50500'),  # 1% spread
        spread=Decimal('500'),
        spread_percentage=1.0,
        volume1=Decimal('10000'),
        volume2=Decimal('8000'),
        detected_at=datetime.now(),
        is_actionable=True
    )
    
    # Create arbitrage opportunity
    logger.info("Creating arbitrage opportunity from price discrepancy...")
    opportunity = await detector._create_simple_arbitrage_opportunity(discrepancy)
    
    if opportunity:
        logger.info(f"Arbitrage Opportunity Found:")
        logger.info(f"  Type: {opportunity.opportunity_type}")
        logger.info(f"  Expected Profit: ${opportunity.expected_profit:.2f}")
        logger.info(f"  Profit Percentage: {opportunity.profit_percentage:.2f}%")
        logger.info(f"  Time Sensitivity: {opportunity.time_sensitivity}")
        logger.info(f"  Confidence: {opportunity.confidence:.1%}")
        logger.info(f"  Markets: {', '.join(opportunity.markets)}")
        
        # Get execution plan
        logger.info("\nGenerating execution plan...")
        plan = detector.get_execution_plan(opportunity)
        
        logger.info("Execution Plan:")
        logger.info(f"  Minimum Capital: ${plan.get('minimum_capital', 0):,.2f}")
        logger.info(f"  Estimated Execution Time: {plan.get('estimated_execution_time', 0):.1f}s")
        logger.info(f"  Risk Level: {plan.get('risk_assessment', {}).get('overall_risk', 0):.1%}")
        
        for i, step in enumerate(plan.get('steps', []), 1):
            logger.info(f"  Step {i}: {step.get('action')} {step.get('amount')} {step.get('symbol')} on {step.get('market')}")
    
    # Get opportunity summary
    detector.active_opportunities = [opportunity] if opportunity else []
    summary = detector.get_opportunity_summary()
    
    logger.info(f"\nOpportunity Summary:")
    logger.info(f"  Total Opportunities: {summary.get('total_opportunities', 0)}")
    logger.info(f"  Simple Arbitrage: {summary.get('simple_arbitrage', 0)}")
    logger.info(f"  Total Potential Profit: ${summary.get('total_potential_profit', 0):.2f}")


async def demonstrate_event_analysis():
    """Demonstrate cross-market event analysis."""
    logger.info("\n=== Cross-Market Event Analysis Demo ===")
    
    # Setup
    mock_store = MockDataStore()
    config = {
        'price_spike_threshold': 0.05,
        'volume_surge_threshold': 3.0,
        'volatility_threshold': 2.0
    }
    
    analyzer = CrossMarketEventAnalyzer(mock_store, config)
    
    # Create symbols
    btc_symbol = UnifiedSymbol(
        base_asset='BTC',
        quote_asset='USD',
        market_type=MarketType.CRYPTO,
        native_symbol='BTCUSD'
    )
    
    eur_symbol = UnifiedSymbol(
        base_asset='EUR',
        quote_asset='USD',
        market_type=MarketType.FOREX,
        native_symbol='EURUSD'
    )
    
    # Create mock event
    from src.analysis.event_analyzer import MarketEvent
    
    mock_event = MarketEvent(
        event_id='demo_price_spike',
        event_type=EventType.PRICE_SPIKE,
        severity=EventSeverity.HIGH,
        source_market=MarketType.CRYPTO,
        source_symbol=btc_symbol,
        detected_at=datetime.now(),
        event_data={
            'price_change': 0.08,
            'current_price': 54000,
            'previous_price': 50000
        },
        description='8% price spike in BTC/USD',
        confidence=0.95
    )
    
    logger.info("Analyzing mock market event...")
    logger.info(f"Event: {mock_event.description}")
    logger.info(f"Severity: {mock_event.severity.value}")
    logger.info(f"Confidence: {mock_event.confidence:.1%}")
    
    # Analyze cross-market impact
    logger.info("\nAnalyzing cross-market impact...")
    impacts = await analyzer.analyze_cross_market_impact(mock_event, [eur_symbol])
    
    for impact in impacts:
        logger.info(f"Impact on {impact.affected_symbols[0].to_standard_format()}:")
        logger.info(f"  Magnitude: {impact.impact_magnitude:+.2%}")
        logger.info(f"  Direction: {impact.impact_direction}")
        logger.info(f"  Confidence: {impact.confidence:.1%}")
        logger.info(f"  Propagation Delay: {impact.propagation_delay}")
    
    # Generate event alerts
    logger.info("\nGenerating event alerts...")
    alerts = await analyzer.generate_event_alerts([mock_event], [btc_symbol, eur_symbol])
    
    for alert in alerts:
        logger.info(f"Alert: {alert.alert_id}")
        logger.info(f"  Urgency: {alert.urgency}")
        logger.info(f"  Predicted Impacts: {len(alert.predicted_impacts)}")
        logger.info(f"  Recommended Actions:")
        for action in alert.recommended_actions:
            logger.info(f"    - {action}")
    
    # Get event summary
    analyzer.recent_events.append(mock_event)
    summary = analyzer.get_event_summary()
    
    logger.info(f"\nEvent Summary:")
    logger.info(f"  Recent Events (24h): {summary.get('recent_events_24h', 0)}")
    logger.info(f"  Event Breakdown: {summary.get('event_breakdown', {})}")
    logger.info(f"  Active Alerts: {summary.get('active_alerts', 0)}")


async def main():
    """Run all cross-market analysis demonstrations."""
    logger.info("Cross-Market Analysis Capabilities Demonstration")
    logger.info("=" * 60)
    
    try:
        # Run demonstrations
        await demonstrate_correlation_analysis()
        await demonstrate_arbitrage_detection()
        await demonstrate_event_analysis()
        
        logger.info("\n" + "=" * 60)
        logger.info("Cross-Market Analysis Demo Complete!")
        logger.info("\nKey Capabilities Demonstrated:")
        logger.info("✓ Correlation analysis between crypto and forex markets")
        logger.info("✓ Correlation-adjusted position sizing")
        logger.info("✓ Arbitrage opportunity detection and execution planning")
        logger.info("✓ Cross-market event detection and impact analysis")
        logger.info("✓ Automated alert generation for significant events")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
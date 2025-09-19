"""
Arbitrage Detector - Identifies cross-market price discrepancies and arbitrage opportunities.

This module detects various types of arbitrage opportunities across different markets,
including simple arbitrage, triangular arbitrage, and cross-market arbitrage.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from collections import defaultdict
import asyncio

from ..models.data_models import UnifiedMarketData
from ..markets.types import MarketType, UnifiedSymbol


@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity."""
    opportunity_type: str  # 'SIMPLE', 'TRIANGULAR', 'CROSS_MARKET'
    symbols: List[UnifiedSymbol]
    markets: List[str]  # Source exchanges/brokers
    expected_profit: Decimal
    profit_percentage: Decimal
    execution_path: List[Dict[str, Any]]  # Step-by-step execution plan
    risk_factors: List[str]
    confidence: float  # 0.0 to 1.0
    time_sensitivity: str  # 'HIGH', 'MEDIUM', 'LOW'
    detected_at: datetime
    expires_at: datetime
    minimum_capital: Decimal
    estimated_execution_time: timedelta


@dataclass
class PriceDiscrepancy:
    """Price discrepancy between markets."""
    symbol: UnifiedSymbol
    market1: str
    market2: str
    price1: Decimal
    price2: Decimal
    spread: Decimal
    spread_percentage: Decimal
    volume1: Decimal
    volume2: Decimal
    detected_at: datetime
    is_actionable: bool


@dataclass
class TriangularArbitrageChain:
    """Triangular arbitrage opportunity chain."""
    base_currency: str
    intermediate_currency: str
    quote_currency: str
    symbol1: UnifiedSymbol  # base/intermediate
    symbol2: UnifiedSymbol  # intermediate/quote
    symbol3: UnifiedSymbol  # base/quote
    market: str
    implied_rate: Decimal
    actual_rate: Decimal
    profit_opportunity: Decimal
    execution_sequence: List[str]


class ArbitrageDetector:
    """
    Advanced arbitrage detection system for cross-market opportunities.
    
    Features:
    - Simple arbitrage detection across markets
    - Triangular arbitrage within markets
    - Cross-market arbitrage opportunities
    - Real-time price discrepancy monitoring
    - Risk assessment and execution planning
    - Opportunity ranking and filtering
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the arbitrage detector.
        
        Args:
            config: Configuration parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.min_profit_threshold = Decimal(str(config.get('min_profit_threshold', 0.001)))  # 0.1%
        self.max_execution_time = timedelta(seconds=config.get('max_execution_time_seconds', 30))
        self.min_volume_threshold = Decimal(str(config.get('min_volume_threshold', 1000)))
        self.max_spread_age = timedelta(seconds=config.get('max_spread_age_seconds', 10))
        
        # Risk parameters
        self.max_slippage = Decimal(str(config.get('max_slippage', 0.002)))  # 0.2%
        self.execution_delay_penalty = Decimal(str(config.get('execution_delay_penalty', 0.0005)))  # 0.05%
        
        # Opportunity tracking
        self.active_opportunities: List[ArbitrageOpportunity] = []
        self.price_discrepancies: Dict[str, List[PriceDiscrepancy]] = defaultdict(list)
        self.triangular_chains: Dict[str, List[TriangularArbitrageChain]] = defaultdict(list)
        
        # Market-specific parameters
        self.market_fees = config.get('market_fees', {})
        self.market_latencies = config.get('market_latencies', {})
        
        self.logger.info("Arbitrage detector initialized")
    
    async def detect_simple_arbitrage(self, symbols: List[UnifiedSymbol]) -> List[ArbitrageOpportunity]:
        """
        Detect simple arbitrage opportunities across different markets.
        
        Args:
            symbols: List of symbols to analyze
            
        Returns:
            List of simple arbitrage opportunities
        """
        try:
            opportunities = []
            
            for symbol in symbols:
                # Get latest prices from all available sources
                latest_data = await self._get_latest_prices_all_sources(symbol)
                
                if len(latest_data) < 2:
                    continue
                
                # Find price discrepancies
                discrepancies = self._find_price_discrepancies(symbol, latest_data)
                
                for discrepancy in discrepancies:
                    if discrepancy.is_actionable:
                        opportunity = await self._create_simple_arbitrage_opportunity(discrepancy)
                        if opportunity:
                            opportunities.append(opportunity)
            
            # Sort by expected profit
            opportunities.sort(key=lambda x: x.expected_profit, reverse=True)
            
            self.logger.info(f"Detected {len(opportunities)} simple arbitrage opportunities")
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting simple arbitrage: {e}")
            return []
    
    def get_opportunity_summary(self) -> Dict[str, Any]:
        """
        Get summary of current arbitrage opportunities.
        
        Returns:
            Summary of opportunities and market conditions
        """
        try:
            # Filter active opportunities
            current_time = datetime.now()
            active_opportunities = [
                opp for opp in self.active_opportunities
                if opp.expires_at > current_time
            ]
            
            # Categorize opportunities
            simple_count = len([opp for opp in active_opportunities if opp.opportunity_type == 'SIMPLE'])
            triangular_count = len([opp for opp in active_opportunities if opp.opportunity_type == 'TRIANGULAR'])
            cross_market_count = len([opp for opp in active_opportunities if opp.opportunity_type == 'CROSS_MARKET'])
            
            # Calculate potential profits
            total_potential_profit = sum(opp.expected_profit for opp in active_opportunities)
            avg_profit_percentage = np.mean([float(opp.profit_percentage) for opp in active_opportunities]) if active_opportunities else 0.0
            
            # Time sensitivity analysis
            high_urgency = len([opp for opp in active_opportunities if opp.time_sensitivity == 'HIGH'])
            medium_urgency = len([opp for opp in active_opportunities if opp.time_sensitivity == 'MEDIUM'])
            low_urgency = len([opp for opp in active_opportunities if opp.time_sensitivity == 'LOW'])
            
            # Market activity
            total_discrepancies = sum(len(discs) for discs in self.price_discrepancies.values())
            
            return {
                'total_opportunities': len(active_opportunities),
                'simple_arbitrage': simple_count,
                'triangular_arbitrage': triangular_count,
                'cross_market_arbitrage': cross_market_count,
                'total_potential_profit': float(total_potential_profit),
                'average_profit_percentage': avg_profit_percentage,
                'urgency_breakdown': {
                    'high': high_urgency,
                    'medium': medium_urgency,
                    'low': low_urgency
                },
                'price_discrepancies': total_discrepancies,
                'last_updated': current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating opportunity summary: {e}")
            return {}
    
    # Private helper methods
    
    async def _get_latest_prices_all_sources(self, symbol: UnifiedSymbol) -> List[UnifiedMarketData]:
        """Get latest prices from all available sources for a symbol."""
        try:
            # Placeholder implementation
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting latest prices: {e}")
            return []
    
    def _find_price_discrepancies(self, symbol: UnifiedSymbol, 
                                 price_data: List[UnifiedMarketData]) -> List[PriceDiscrepancy]:
        """Find price discrepancies between different sources."""
        try:
            discrepancies = []
            
            for i, data1 in enumerate(price_data):
                for data2 in price_data[i+1:]:
                    if data1.source != data2.source:
                        spread = abs(data1.close - data2.close)
                        avg_price = (data1.close + data2.close) / 2
                        spread_percentage = (spread / avg_price) * 100
                        
                        # Check if discrepancy is actionable
                        is_actionable = (
                            spread_percentage > self.min_profit_threshold * 100 and
                            min(data1.volume, data2.volume) > self.min_volume_threshold and
                            abs((data1.timestamp - data2.timestamp).total_seconds()) < self.max_spread_age.total_seconds()
                        )
                        
                        discrepancy = PriceDiscrepancy(
                            symbol=symbol,
                            market1=data1.source,
                            market2=data2.source,
                            price1=data1.close,
                            price2=data2.close,
                            spread=spread,
                            spread_percentage=spread_percentage,
                            volume1=data1.volume,
                            volume2=data2.volume,
                            detected_at=datetime.now(),
                            is_actionable=is_actionable
                        )
                        
                        discrepancies.append(discrepancy)
            
            return discrepancies
            
        except Exception as e:
            self.logger.error(f"Error finding price discrepancies: {e}")
            return []
    
    async def _create_simple_arbitrage_opportunity(self, discrepancy: PriceDiscrepancy) -> Optional[ArbitrageOpportunity]:
        """Create a simple arbitrage opportunity from a price discrepancy."""
        try:
            # Determine buy and sell markets
            if discrepancy.price1 < discrepancy.price2:
                buy_market = discrepancy.market1
                sell_market = discrepancy.market2
                buy_price = discrepancy.price1
                sell_price = discrepancy.price2
            else:
                buy_market = discrepancy.market2
                sell_market = discrepancy.market1
                buy_price = discrepancy.price2
                sell_price = discrepancy.price1
            
            # Calculate expected profit (accounting for fees and slippage)
            gross_profit = sell_price - buy_price
            
            # Estimate fees
            buy_fee = buy_price * Decimal(str(self.market_fees.get(buy_market, 0.001)))
            sell_fee = sell_price * Decimal(str(self.market_fees.get(sell_market, 0.001)))
            
            # Estimate slippage
            slippage_cost = (buy_price + sell_price) * self.max_slippage / 2
            
            net_profit = gross_profit - buy_fee - sell_fee - slippage_cost
            profit_percentage = (net_profit / buy_price) * 100
            
            if net_profit <= Decimal('0'):
                return None
            
            # Create execution path
            execution_path = [
                {
                    'action': 'BUY',
                    'symbol': discrepancy.symbol.to_standard_format(),
                    'market': buy_market,
                    'amount': float(min(discrepancy.volume1, discrepancy.volume2) * Decimal('0.1')),
                    'expected_price': float(buy_price),
                    'timing': 'IMMEDIATE'
                },
                {
                    'action': 'SELL',
                    'symbol': discrepancy.symbol.to_standard_format(),
                    'market': sell_market,
                    'amount': float(min(discrepancy.volume1, discrepancy.volume2) * Decimal('0.1')),
                    'expected_price': float(sell_price),
                    'timing': 'IMMEDIATE',
                    'dependencies': ['step_1']
                }
            ]
            
            # Assess risk factors
            risk_factors = []
            if discrepancy.spread_percentage < 0.5:
                risk_factors.append('LOW_SPREAD_MARGIN')
            if min(discrepancy.volume1, discrepancy.volume2) < self.min_volume_threshold * 10:
                risk_factors.append('LIMITED_LIQUIDITY')
            
            # Determine time sensitivity
            if discrepancy.spread_percentage > 1.0:
                time_sensitivity = 'HIGH'
            elif discrepancy.spread_percentage > 0.5:
                time_sensitivity = 'MEDIUM'
            else:
                time_sensitivity = 'LOW'
            
            opportunity = ArbitrageOpportunity(
                opportunity_type='SIMPLE',
                symbols=[discrepancy.symbol],
                markets=[buy_market, sell_market],
                expected_profit=net_profit,
                profit_percentage=profit_percentage,
                execution_path=execution_path,
                risk_factors=risk_factors,
                confidence=0.8,
                time_sensitivity=time_sensitivity,
                detected_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=30),
                minimum_capital=buy_price * Decimal('0.1'),
                estimated_execution_time=timedelta(seconds=10)
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating simple arbitrage opportunity: {e}")
            return None
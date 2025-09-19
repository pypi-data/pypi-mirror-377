"""
Cross-market arbitrage strategy base class and implementations.

This module provides arbitrage strategies that identify and execute
opportunities across different markets (crypto and forex).
"""

import logging
import asyncio
from abc import abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass

from .market_agnostic_strategy import MarketAgnosticStrategy, StrategyConfig
from ..models.data_models import UnifiedMarketData, TradingSignal, SignalAction
from ..markets.types import MarketType, UnifiedSymbol
from ..analysis.arbitrage_detector import ArbitrageDetector, ArbitrageOpportunity
from ..data.cross_market_store import CrossMarketDataStore


@dataclass
class ArbitrageSignal(TradingSignal):
    """Enhanced trading signal for arbitrage opportunities."""
    
    opportunity: ArbitrageOpportunity = None
    execution_plan: Dict[str, Any] = None
    risk_assessment: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validate arbitrage signal after initialization."""
        super().__post_init__()
        if not self.opportunity:
            raise ValueError("Arbitrage opportunity cannot be None")
        if not self.execution_plan:
            raise ValueError("Execution plan cannot be empty")


class CrossMarketArbitrageStrategy(MarketAgnosticStrategy):
    """
    Base class for cross-market arbitrage strategies.
    
    This strategy identifies and executes arbitrage opportunities
    across different markets, handling the complexities of
    multi-market trading including timing, execution, and risk management.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the cross-market arbitrage strategy.
        
        Args:
            config: Strategy configuration parameters
        """
        super().__init__(config)
        
        # Arbitrage-specific configuration
        self.min_profit_threshold = Decimal(str(config.parameters.get('min_profit_threshold', 0.005)))  # 0.5%
        self.max_execution_time = timedelta(seconds=config.parameters.get('max_execution_time_seconds', 30))
        self.max_position_size = Decimal(str(config.parameters.get('max_position_size', 10000)))  # USD equivalent
        self.risk_tolerance = config.parameters.get('risk_tolerance', 'MEDIUM')
        
        # Market-specific settings
        self.crypto_exchanges = config.parameters.get('crypto_exchanges', ['binance', 'coinbase'])
        self.forex_brokers = config.parameters.get('forex_brokers', ['oanda', 'mt5'])
        
        # Arbitrage detector
        self.arbitrage_detector: Optional[ArbitrageDetector] = None
        self.data_store: Optional[CrossMarketDataStore] = None
        
        # Opportunity tracking
        self.active_opportunities: List[ArbitrageOpportunity] = []
        self.executed_opportunities: List[ArbitrageOpportunity] = []
        self.rejected_opportunities: List[ArbitrageOpportunity] = []
        
        # Performance metrics
        self.total_arbitrage_profit = Decimal('0')
        self.successful_arbitrages = 0
        self.failed_arbitrages = 0
        
        self.logger = logging.getLogger(f"arbitrage_strategy.{self.name}")
    
    def initialize(self) -> bool:
        """
        Initialize the arbitrage strategy with required components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Initialize arbitrage detector
            detector_config = {
                'min_profit_threshold': float(self.min_profit_threshold),
                'max_execution_time_seconds': self.max_execution_time.total_seconds(),
                'min_volume_threshold': 1000,
                'max_spread_age_seconds': 10,
                'market_fees': {
                    'binance': 0.001,
                    'coinbase': 0.005,
                    'oanda': 0.0001,
                    'mt5': 0.0002
                },
                'market_latencies': {
                    'binance': 0.1,
                    'coinbase': 0.2,
                    'oanda': 0.05,
                    'mt5': 0.1
                }
            }
            
            # Note: In a real implementation, these would be injected
            # For now, we'll create placeholder instances
            if not self.data_store:
                self.logger.warning("Data store not provided, creating placeholder")
                # In real implementation, this would be injected
                
            if not self.arbitrage_detector:
                self.logger.warning("Arbitrage detector not provided, creating placeholder")
                # In real implementation, this would be injected with data_store
            
            self.logger.info(f"Cross-market arbitrage strategy {self.name} initialized")
            self._initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize arbitrage strategy: {e}")
            return False
    
    def analyze_unified_data(self, market_data: List[UnifiedMarketData]) -> Optional[TradingSignal]:
        """
        Analyze unified market data for arbitrage opportunities.
        
        Args:
            market_data: List of unified market data points for analysis
            
        Returns:
            Optional[TradingSignal]: Arbitrage signal if opportunity found, None otherwise
        """
        try:
            if not market_data:
                return None
            
            # Group data by market type
            crypto_data = [d for d in market_data if d.market_type == MarketType.CRYPTO]
            forex_data = [d for d in market_data if d.market_type == MarketType.FOREX]
            
            # Find arbitrage opportunities
            opportunities = self._detect_arbitrage_opportunities(crypto_data, forex_data)
            
            if not opportunities:
                return None
            
            # Select best opportunity
            best_opportunity = self._select_best_opportunity(opportunities)
            
            if not best_opportunity:
                return None
            
            # Validate opportunity
            if not self._validate_opportunity(best_opportunity):
                self.logger.debug(f"Opportunity validation failed for {best_opportunity.opportunity_type}")
                return None
            
            # Create execution plan
            execution_plan = self._create_execution_plan(best_opportunity)
            
            # Assess risk
            risk_assessment = self._assess_opportunity_risk(best_opportunity)
            
            # Create arbitrage signal
            signal = ArbitrageSignal(
                symbol=best_opportunity.symbols[0].to_standard_format(),
                action=SignalAction.BUY,  # Arbitrage involves both buy and sell
                confidence=best_opportunity.confidence,
                timestamp=datetime.now(),
                strategy_name=self.name,
                metadata={
                    'opportunity_type': best_opportunity.opportunity_type,
                    'expected_profit': float(best_opportunity.expected_profit),
                    'profit_percentage': float(best_opportunity.profit_percentage),
                    'markets': best_opportunity.markets,
                    'time_sensitivity': best_opportunity.time_sensitivity
                },
                opportunity=best_opportunity,
                execution_plan=execution_plan,
                risk_assessment=risk_assessment
            )
            
            # Track opportunity
            self.active_opportunities.append(best_opportunity)
            
            self.logger.info(f"Arbitrage opportunity detected: {best_opportunity.opportunity_type} "
                           f"with {best_opportunity.profit_percentage:.2f}% profit potential")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error analyzing data for arbitrage: {e}")
            return None
    
    @abstractmethod
    def _detect_arbitrage_opportunities(self, crypto_data: List[UnifiedMarketData], 
                                      forex_data: List[UnifiedMarketData]) -> List[ArbitrageOpportunity]:
        """
        Detect specific arbitrage opportunities based on strategy type.
        
        Args:
            crypto_data: Crypto market data
            forex_data: Forex market data
            
        Returns:
            List[ArbitrageOpportunity]: List of detected opportunities
        """
        pass
    
    def get_cross_market_correlation_threshold(self) -> float:
        """
        Get the correlation threshold for cross-market analysis.
        
        Returns:
            float: Correlation threshold (0.0 to 1.0)
        """
        return 0.3  # Lower threshold for arbitrage strategies
    
    def get_required_data_length(self) -> int:
        """
        Get the minimum number of data points required for analysis.
        
        Returns:
            int: Minimum number of data points needed
        """
        return 2  # Need at least 2 data points to compare prices
    
    def validate_parameters(self) -> bool:
        """
        Validate arbitrage strategy parameters.
        
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        try:
            if not super().validate_parameters():
                return False
            
            # Validate profit threshold
            if self.min_profit_threshold <= 0:
                self.logger.error(f"Invalid profit threshold: {self.min_profit_threshold}")
                return False
            
            # Validate execution time
            if self.max_execution_time.total_seconds() <= 0:
                self.logger.error(f"Invalid execution time: {self.max_execution_time}")
                return False
            
            # Validate position size
            if self.max_position_size <= 0:
                self.logger.error(f"Invalid position size: {self.max_position_size}")
                return False
            
            # Validate risk tolerance
            valid_risk_levels = ['LOW', 'MEDIUM', 'HIGH']
            if self.risk_tolerance not in valid_risk_levels:
                self.logger.error(f"Invalid risk tolerance: {self.risk_tolerance}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {e}")
            return False
    
    def _select_best_opportunity(self, opportunities: List[ArbitrageOpportunity]) -> Optional[ArbitrageOpportunity]:
        """
        Select the best arbitrage opportunity from available options.
        
        Args:
            opportunities: List of available opportunities
            
        Returns:
            Optional[ArbitrageOpportunity]: Best opportunity or None
        """
        if not opportunities:
            return None
        
        # Filter by minimum profit threshold
        profitable_opportunities = [
            opp for opp in opportunities
            if opp.profit_percentage >= self.min_profit_threshold * 100
        ]
        
        if not profitable_opportunities:
            return None
        
        # Score opportunities based on multiple factors
        scored_opportunities = []
        for opp in profitable_opportunities:
            score = self._calculate_opportunity_score(opp)
            scored_opportunities.append((score, opp))
        
        # Sort by score (highest first)
        scored_opportunities.sort(key=lambda x: x[0], reverse=True)
        
        return scored_opportunities[0][1]
    
    def _calculate_opportunity_score(self, opportunity: ArbitrageOpportunity) -> float:
        """
        Calculate a score for an arbitrage opportunity.
        
        Args:
            opportunity: Arbitrage opportunity to score
            
        Returns:
            float: Opportunity score (higher is better)
        """
        # Base score from profit percentage
        score = float(opportunity.profit_percentage)
        
        # Adjust for confidence
        score *= opportunity.confidence
        
        # Adjust for time sensitivity (higher urgency = higher score)
        time_multiplier = {
            'HIGH': 1.5,
            'MEDIUM': 1.0,
            'LOW': 0.7
        }
        score *= time_multiplier.get(opportunity.time_sensitivity, 1.0)
        
        # Penalize for risk factors
        risk_penalty = len(opportunity.risk_factors) * 0.1
        score *= (1.0 - risk_penalty)
        
        # Adjust for execution time (faster = better)
        if opportunity.estimated_execution_time.total_seconds() > 0:
            time_factor = min(1.0, 30.0 / opportunity.estimated_execution_time.total_seconds())
            score *= time_factor
        
        return max(0.0, score)
    
    def _validate_opportunity(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Validate an arbitrage opportunity before execution.
        
        Args:
            opportunity: Opportunity to validate
            
        Returns:
            bool: True if opportunity is valid for execution
        """
        try:
            # Check if opportunity has expired
            if datetime.now() > opportunity.expires_at:
                self.logger.debug("Opportunity has expired")
                return False
            
            # Check minimum capital requirements
            if opportunity.minimum_capital > self.max_position_size:
                self.logger.debug(f"Opportunity requires too much capital: {opportunity.minimum_capital}")
                return False
            
            # Check execution time constraints
            if opportunity.estimated_execution_time > self.max_execution_time:
                self.logger.debug(f"Opportunity execution time too long: {opportunity.estimated_execution_time}")
                return False
            
            # Risk tolerance check
            risk_score = len(opportunity.risk_factors)
            max_risk_by_tolerance = {'LOW': 1, 'MEDIUM': 3, 'HIGH': 5}
            
            if risk_score > max_risk_by_tolerance.get(self.risk_tolerance, 3):
                self.logger.debug(f"Opportunity too risky: {risk_score} risk factors")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating opportunity: {e}")
            return False
    
    def _create_execution_plan(self, opportunity: ArbitrageOpportunity) -> Dict[str, Any]:
        """
        Create detailed execution plan for an arbitrage opportunity.
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Dict[str, Any]: Detailed execution plan
        """
        return {
            'opportunity_id': f"{opportunity.opportunity_type}_{opportunity.detected_at.timestamp()}",
            'type': opportunity.opportunity_type,
            'steps': opportunity.execution_path,
            'expected_profit': float(opportunity.expected_profit),
            'profit_percentage': float(opportunity.profit_percentage),
            'estimated_execution_time': opportunity.estimated_execution_time.total_seconds(),
            'minimum_capital': float(opportunity.minimum_capital),
            'markets_involved': opportunity.markets,
            'symbols_involved': [s.to_standard_format() for s in opportunity.symbols],
            'time_sensitivity': opportunity.time_sensitivity,
            'expires_at': opportunity.expires_at.isoformat(),
            'confidence': opportunity.confidence
        }
    
    def _assess_opportunity_risk(self, opportunity: ArbitrageOpportunity) -> Dict[str, Any]:
        """
        Assess risk factors for an arbitrage opportunity.
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Dict[str, Any]: Risk assessment
        """
        return {
            'risk_factors': opportunity.risk_factors,
            'risk_score': len(opportunity.risk_factors),
            'risk_level': self._categorize_risk_level(len(opportunity.risk_factors)),
            'mitigation_strategies': self._get_risk_mitigation_strategies(opportunity),
            'maximum_loss_estimate': self._estimate_maximum_loss(opportunity),
            'probability_of_success': self._estimate_success_probability(opportunity)
        }
    
    def _categorize_risk_level(self, risk_score: int) -> str:
        """Categorize risk level based on risk score."""
        if risk_score <= 1:
            return 'LOW'
        elif risk_score <= 3:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _get_risk_mitigation_strategies(self, opportunity: ArbitrageOpportunity) -> List[str]:
        """Get risk mitigation strategies for an opportunity."""
        strategies = []
        
        for factor in opportunity.risk_factors:
            if factor == 'LOW_SPREAD_MARGIN':
                strategies.append('Use limit orders to ensure favorable execution prices')
            elif factor == 'LIMITED_LIQUIDITY':
                strategies.append('Split orders into smaller sizes to minimize market impact')
            elif factor == 'HIGH_VOLATILITY':
                strategies.append('Execute trades simultaneously to minimize timing risk')
            elif factor == 'EXECUTION_DELAY':
                strategies.append('Use fastest available execution methods')
        
        return strategies
    
    def _estimate_maximum_loss(self, opportunity: ArbitrageOpportunity) -> float:
        """Estimate maximum potential loss for an opportunity."""
        # Conservative estimate: 2x the expected profit as potential loss
        return float(opportunity.expected_profit) * 2.0
    
    def _estimate_success_probability(self, opportunity: ArbitrageOpportunity) -> float:
        """Estimate probability of successful execution."""
        base_probability = 0.8  # Base 80% success rate
        
        # Adjust for risk factors
        risk_penalty = len(opportunity.risk_factors) * 0.1
        probability = base_probability - risk_penalty
        
        # Adjust for time sensitivity
        if opportunity.time_sensitivity == 'HIGH':
            probability *= 0.9  # Slightly lower due to time pressure
        elif opportunity.time_sensitivity == 'LOW':
            probability *= 1.1  # Higher due to more time
        
        return max(0.1, min(0.95, probability))
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get enhanced performance metrics for arbitrage strategy.
        
        Returns:
            Dict[str, Any]: Enhanced performance metrics
        """
        base_metrics = super().get_performance_metrics()
        
        # Calculate success rate
        total_arbitrages = self.successful_arbitrages + self.failed_arbitrages
        success_rate = (self.successful_arbitrages / total_arbitrages) if total_arbitrages > 0 else 0.0
        
        # Add arbitrage-specific metrics
        base_metrics.update({
            'strategy_type': 'cross_market_arbitrage',
            'total_arbitrage_profit': float(self.total_arbitrage_profit),
            'successful_arbitrages': self.successful_arbitrages,
            'failed_arbitrages': self.failed_arbitrages,
            'arbitrage_success_rate': success_rate,
            'active_opportunities': len(self.active_opportunities),
            'executed_opportunities': len(self.executed_opportunities),
            'rejected_opportunities': len(self.rejected_opportunities),
            'min_profit_threshold': float(self.min_profit_threshold),
            'max_execution_time_seconds': self.max_execution_time.total_seconds(),
            'risk_tolerance': self.risk_tolerance
        })
        
        return base_metrics
    
    def update_arbitrage_result(self, opportunity: ArbitrageOpportunity, 
                              successful: bool, profit: Optional[Decimal] = None):
        """
        Update arbitrage execution results.
        
        Args:
            opportunity: Executed opportunity
            successful: Whether execution was successful
            profit: Actual profit/loss (if available)
        """
        try:
            # Remove from active opportunities
            if opportunity in self.active_opportunities:
                self.active_opportunities.remove(opportunity)
            
            # Update counters
            if successful:
                self.successful_arbitrages += 1
                self.executed_opportunities.append(opportunity)
                
                if profit is not None:
                    self.total_arbitrage_profit += profit
                    self.logger.info(f"Successful arbitrage: {profit} profit")
            else:
                self.failed_arbitrages += 1
                self.rejected_opportunities.append(opportunity)
                self.logger.warning("Arbitrage execution failed")
            
            # Update signal success tracking
            self.update_signal_success(successful)
            
        except Exception as e:
            self.logger.error(f"Error updating arbitrage result: {e}")
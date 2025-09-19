"""
Crypto-Forex arbitrage strategy for currency arbitrage opportunities.

This strategy identifies arbitrage opportunities between cryptocurrency
and forex markets for the same currency pairs (e.g., BTC/USD vs USD/BTC equivalent).
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from .cross_market_arbitrage_strategy import CrossMarketArbitrageStrategy, StrategyConfig
from ..models.data_models import UnifiedMarketData
from ..markets.types import MarketType, UnifiedSymbol
from ..analysis.arbitrage_detector import ArbitrageOpportunity


class CryptoForexArbitrageStrategy(CrossMarketArbitrageStrategy):
    """
    Crypto-Forex arbitrage strategy for currency arbitrage.
    
    This strategy identifies price discrepancies between cryptocurrency
    and forex markets for equivalent currency pairs. For example:
    - BTC/USD in crypto vs USD/BTC equivalent in forex
    - ETH/EUR in crypto vs EUR/ETH equivalent in forex
    
    The strategy accounts for:
    - Currency conversion rates
    - Market session overlaps
    - Execution timing differences
    - Regulatory considerations
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the crypto-forex arbitrage strategy.
        
        Args:
            config: Strategy configuration parameters
        """
        super().__init__(config)
        
        # Crypto-forex specific configuration
        self.supported_crypto_currencies = config.parameters.get(
            'supported_crypto_currencies', ['BTC', 'ETH', 'LTC', 'XRP']
        )
        self.supported_fiat_currencies = config.parameters.get(
            'supported_fiat_currencies', ['USD', 'EUR', 'GBP', 'JPY']
        )
        
        # Conversion and timing parameters
        self.max_conversion_spread = Decimal(str(config.parameters.get('max_conversion_spread', 0.002)))  # 0.2%
        self.min_session_overlap = timedelta(minutes=config.parameters.get('min_session_overlap_minutes', 30))
        
        # Risk parameters specific to crypto-forex arbitrage
        self.max_crypto_volatility = config.parameters.get('max_crypto_volatility', 0.05)  # 5% in last hour
        self.forex_session_weight = config.parameters.get('forex_session_weight', 0.8)  # Prefer active forex sessions
        
        # Currency pair mappings
        self.currency_pair_mappings = self._initialize_currency_mappings()
        
        self.logger = logging.getLogger(f"crypto_forex_arbitrage.{self.name}")
    
    def _initialize_currency_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Initialize currency pair mappings between crypto and forex.
        
        Returns:
            Dict[str, Dict[str, str]]: Mapping of crypto pairs to forex equivalents
        """
        mappings = {}
        
        for crypto in self.supported_crypto_currencies:
            for fiat in self.supported_fiat_currencies:
                crypto_pair = f"{crypto}/{fiat}"
                
                # Direct forex equivalent (if exists)
                if crypto in ['BTC', 'ETH'] and fiat in ['USD', 'EUR']:
                    # Some brokers offer crypto CFDs
                    forex_equivalent = f"{crypto}{fiat}"
                    mappings[crypto_pair] = {
                        'forex_pair': forex_equivalent,
                        'conversion_type': 'DIRECT',
                        'requires_conversion': False
                    }
                else:
                    # Indirect through USD conversion
                    mappings[crypto_pair] = {
                        'forex_pair': f"{fiat}USD" if fiat != 'USD' else None,
                        'conversion_type': 'INDIRECT',
                        'requires_conversion': True,
                        'base_currency': 'USD'
                    }
        
        return mappings
    
    def _detect_arbitrage_opportunities(self, crypto_data: List[UnifiedMarketData], 
                                      forex_data: List[UnifiedMarketData]) -> List[ArbitrageOpportunity]:
        """
        Detect crypto-forex arbitrage opportunities.
        
        Args:
            crypto_data: Crypto market data
            forex_data: Forex market data
            
        Returns:
            List[ArbitrageOpportunity]: List of detected opportunities
        """
        opportunities = []
        
        try:
            # Group data by symbol for easier comparison
            crypto_by_symbol = self._group_data_by_symbol(crypto_data)
            forex_by_symbol = self._group_data_by_symbol(forex_data)
            
            # Find matching currency pairs
            for crypto_symbol_str, crypto_data_list in crypto_by_symbol.items():
                if not crypto_data_list:
                    continue
                
                crypto_symbol = crypto_data_list[0].symbol
                
                # Check if we have a mapping for this crypto pair
                if crypto_symbol_str not in self.currency_pair_mappings:
                    continue
                
                mapping = self.currency_pair_mappings[crypto_symbol_str]
                
                # Find corresponding forex data
                forex_opportunities = self._find_forex_equivalent_opportunities(
                    crypto_data_list, forex_by_symbol, mapping
                )
                
                opportunities.extend(forex_opportunities)
            
            # Filter opportunities by quality and feasibility
            filtered_opportunities = self._filter_crypto_forex_opportunities(opportunities)
            
            self.logger.debug(f"Detected {len(filtered_opportunities)} crypto-forex arbitrage opportunities")
            
            return filtered_opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting crypto-forex arbitrage opportunities: {e}")
            return []
    
    def _group_data_by_symbol(self, data: List[UnifiedMarketData]) -> Dict[str, List[UnifiedMarketData]]:
        """Group market data by symbol."""
        grouped = {}
        for item in data:
            symbol_str = item.symbol.to_standard_format()
            if symbol_str not in grouped:
                grouped[symbol_str] = []
            grouped[symbol_str].append(item)
        return grouped
    
    def _find_forex_equivalent_opportunities(self, crypto_data: List[UnifiedMarketData],
                                           forex_by_symbol: Dict[str, List[UnifiedMarketData]],
                                           mapping: Dict[str, str]) -> List[ArbitrageOpportunity]:
        """
        Find forex equivalent opportunities for crypto data.
        
        Args:
            crypto_data: Crypto market data for a specific symbol
            forex_by_symbol: Forex data grouped by symbol
            mapping: Currency pair mapping information
            
        Returns:
            List[ArbitrageOpportunity]: List of opportunities
        """
        opportunities = []
        
        try:
            if mapping['conversion_type'] == 'DIRECT':
                # Direct comparison (e.g., BTC/USD crypto vs BTCUSD forex CFD)
                forex_pair = mapping['forex_pair']
                if forex_pair in forex_by_symbol:
                    forex_data = forex_by_symbol[forex_pair]
                    opportunity = self._create_direct_arbitrage_opportunity(crypto_data, forex_data)
                    if opportunity:
                        opportunities.append(opportunity)
            
            elif mapping['conversion_type'] == 'INDIRECT':
                # Indirect comparison requiring currency conversion
                opportunities.extend(
                    self._create_indirect_arbitrage_opportunities(crypto_data, forex_by_symbol, mapping)
                )
            
        except Exception as e:
            self.logger.error(f"Error finding forex equivalent opportunities: {e}")
        
        return opportunities
    
    def _create_direct_arbitrage_opportunity(self, crypto_data: List[UnifiedMarketData],
                                           forex_data: List[UnifiedMarketData]) -> Optional[ArbitrageOpportunity]:
        """
        Create direct arbitrage opportunity between crypto and forex.
        
        Args:
            crypto_data: Crypto market data
            forex_data: Forex market data
            
        Returns:
            Optional[ArbitrageOpportunity]: Arbitrage opportunity if found
        """
        try:
            if not crypto_data or not forex_data:
                return None
            
            # Get latest prices
            crypto_latest = max(crypto_data, key=lambda x: x.timestamp)
            forex_latest = max(forex_data, key=lambda x: x.timestamp)
            
            # Check data freshness (within 30 seconds)
            max_age = timedelta(seconds=30)
            now = datetime.now()
            
            if (now - crypto_latest.timestamp > max_age or 
                now - forex_latest.timestamp > max_age):
                return None
            
            # Calculate price discrepancy
            crypto_price = crypto_latest.close
            forex_price = forex_latest.close
            
            # Determine arbitrage direction
            if crypto_price > forex_price:
                # Sell crypto, buy forex
                profit = crypto_price - forex_price
                buy_market = forex_latest.source
                sell_market = crypto_latest.source
                buy_price = forex_price
                sell_price = crypto_price
            else:
                # Buy crypto, sell forex
                profit = forex_price - crypto_price
                buy_market = crypto_latest.source
                sell_market = forex_latest.source
                buy_price = crypto_price
                sell_price = forex_price
            
            # Calculate profit percentage
            avg_price = (crypto_price + forex_price) / 2
            profit_percentage = (profit / avg_price) * 100
            
            # Check minimum profit threshold
            if profit_percentage < self.min_profit_threshold * 100:
                return None
            
            # Estimate fees and costs
            estimated_fees = self._estimate_cross_market_fees(crypto_latest, forex_latest)
            net_profit = profit - estimated_fees
            
            if net_profit <= 0:
                return None
            
            # Create execution path
            execution_path = [
                {
                    'action': 'BUY',
                    'symbol': buy_market == crypto_latest.source and crypto_latest.symbol.to_standard_format() or forex_latest.symbol.to_standard_format(),
                    'market': buy_market,
                    'amount': float(min(crypto_latest.volume, forex_latest.volume) * Decimal('0.01')),  # Conservative 1%
                    'expected_price': float(buy_price),
                    'timing': 'IMMEDIATE'
                },
                {
                    'action': 'SELL',
                    'symbol': sell_market == crypto_latest.source and crypto_latest.symbol.to_standard_format() or forex_latest.symbol.to_standard_format(),
                    'market': sell_market,
                    'amount': float(min(crypto_latest.volume, forex_latest.volume) * Decimal('0.01')),
                    'expected_price': float(sell_price),
                    'timing': 'IMMEDIATE',
                    'dependencies': ['step_1']
                }
            ]
            
            # Assess risk factors
            risk_factors = self._assess_crypto_forex_risks(crypto_latest, forex_latest)
            
            # Determine time sensitivity
            time_sensitivity = 'HIGH' if profit_percentage > 1.0 else 'MEDIUM'
            
            opportunity = ArbitrageOpportunity(
                opportunity_type='CRYPTO_FOREX',
                symbols=[crypto_latest.symbol, forex_latest.symbol],
                markets=[crypto_latest.source, forex_latest.source],
                expected_profit=net_profit,
                profit_percentage=profit_percentage,
                execution_path=execution_path,
                risk_factors=risk_factors,
                confidence=self._calculate_confidence(crypto_latest, forex_latest, risk_factors),
                time_sensitivity=time_sensitivity,
                detected_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=20),  # Short expiry for price arbitrage
                minimum_capital=buy_price * Decimal('0.01'),
                estimated_execution_time=timedelta(seconds=15)
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating direct arbitrage opportunity: {e}")
            return None
    
    def _create_indirect_arbitrage_opportunities(self, crypto_data: List[UnifiedMarketData],
                                               forex_by_symbol: Dict[str, List[UnifiedMarketData]],
                                               mapping: Dict[str, str]) -> List[ArbitrageOpportunity]:
        """
        Create indirect arbitrage opportunities requiring currency conversion.
        
        Args:
            crypto_data: Crypto market data
            forex_by_symbol: Forex data grouped by symbol
            mapping: Currency pair mapping information
            
        Returns:
            List[ArbitrageOpportunity]: List of opportunities
        """
        opportunities = []
        
        try:
            # For indirect arbitrage, we need to find conversion rates
            # This is more complex and requires multiple steps
            
            # For now, we'll implement a simplified version
            # In a full implementation, this would handle complex currency conversions
            
            if not crypto_data:
                return opportunities
            
            crypto_latest = max(crypto_data, key=lambda x: x.timestamp)
            base_currency = mapping.get('base_currency', 'USD')
            
            # Look for USD pairs that can be used for conversion
            usd_pairs = [symbol for symbol in forex_by_symbol.keys() if 'USD' in symbol]
            
            for usd_pair in usd_pairs:
                forex_data = forex_by_symbol[usd_pair]
                if forex_data:
                    # Create a simplified indirect opportunity
                    # This would be much more complex in a real implementation
                    opportunity = self._create_simplified_indirect_opportunity(
                        crypto_latest, forex_data, mapping
                    )
                    if opportunity:
                        opportunities.append(opportunity)
            
        except Exception as e:
            self.logger.error(f"Error creating indirect arbitrage opportunities: {e}")
        
        return opportunities
    
    def _create_simplified_indirect_opportunity(self, crypto_data: UnifiedMarketData,
                                              forex_data: List[UnifiedMarketData],
                                              mapping: Dict[str, str]) -> Optional[ArbitrageOpportunity]:
        """
        Create a simplified indirect arbitrage opportunity.
        
        This is a placeholder implementation. A full implementation would
        handle complex multi-step currency conversions.
        """
        try:
            if not forex_data:
                return None
            
            forex_latest = max(forex_data, key=lambda x: x.timestamp)
            
            # Simplified calculation - in reality this would be much more complex
            # involving multiple conversion steps and rates
            
            # For demonstration, we'll create a basic opportunity structure
            execution_path = [
                {
                    'action': 'BUY',
                    'symbol': crypto_data.symbol.to_standard_format(),
                    'market': crypto_data.source,
                    'amount': float(crypto_data.volume * Decimal('0.005')),  # Very conservative
                    'expected_price': float(crypto_data.close),
                    'timing': 'IMMEDIATE'
                },
                {
                    'action': 'CONVERT',
                    'symbol': forex_latest.symbol.to_standard_format(),
                    'market': forex_latest.source,
                    'amount': float(forex_latest.volume * Decimal('0.005')),
                    'expected_price': float(forex_latest.close),
                    'timing': 'IMMEDIATE',
                    'dependencies': ['step_1']
                }
            ]
            
            # Conservative profit estimate for indirect arbitrage
            estimated_profit = crypto_data.close * Decimal('0.001')  # 0.1%
            profit_percentage = Decimal('0.1')
            
            risk_factors = ['CURRENCY_CONVERSION', 'MULTI_STEP_EXECUTION', 'TIMING_RISK']
            
            opportunity = ArbitrageOpportunity(
                opportunity_type='CRYPTO_FOREX_INDIRECT',
                symbols=[crypto_data.symbol, forex_latest.symbol],
                markets=[crypto_data.source, forex_latest.source],
                expected_profit=estimated_profit,
                profit_percentage=profit_percentage,
                execution_path=execution_path,
                risk_factors=risk_factors,
                confidence=0.6,  # Lower confidence for indirect arbitrage
                time_sensitivity='MEDIUM',
                detected_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=45),
                minimum_capital=crypto_data.close * Decimal('0.005'),
                estimated_execution_time=timedelta(seconds=30)
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating simplified indirect opportunity: {e}")
            return None
    
    def _filter_crypto_forex_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        Filter crypto-forex opportunities based on quality and feasibility.
        
        Args:
            opportunities: List of opportunities to filter
            
        Returns:
            List[ArbitrageOpportunity]: Filtered opportunities
        """
        filtered = []
        
        for opportunity in opportunities:
            try:
                # Check profit threshold
                if opportunity.profit_percentage < self.min_profit_threshold * 100:
                    continue
                
                # Check execution time
                if opportunity.estimated_execution_time > self.max_execution_time:
                    continue
                
                # Check risk factors
                if len(opportunity.risk_factors) > 4:  # Too many risks
                    continue
                
                # Check for high volatility risk
                if 'HIGH_VOLATILITY' in opportunity.risk_factors and self.risk_tolerance == 'LOW':
                    continue
                
                # Check minimum capital
                if opportunity.minimum_capital > self.max_position_size:
                    continue
                
                filtered.append(opportunity)
                
            except Exception as e:
                self.logger.error(f"Error filtering opportunity: {e}")
                continue
        
        return filtered
    
    def _estimate_cross_market_fees(self, crypto_data: UnifiedMarketData, 
                                   forex_data: UnifiedMarketData) -> Decimal:
        """
        Estimate fees for cross-market execution.
        
        Args:
            crypto_data: Crypto market data
            forex_data: Forex market data
            
        Returns:
            Decimal: Estimated total fees
        """
        # Typical fees
        crypto_fee_rate = Decimal('0.001')  # 0.1%
        forex_fee_rate = Decimal('0.0002')  # 0.02%
        
        crypto_fee = crypto_data.close * crypto_fee_rate
        forex_fee = forex_data.close * forex_fee_rate
        
        # Add conversion costs if needed
        conversion_cost = (crypto_data.close + forex_data.close) * self.max_conversion_spread / 2
        
        return crypto_fee + forex_fee + conversion_cost
    
    def _assess_crypto_forex_risks(self, crypto_data: UnifiedMarketData, 
                                  forex_data: UnifiedMarketData) -> List[str]:
        """
        Assess risk factors specific to crypto-forex arbitrage.
        
        Args:
            crypto_data: Crypto market data
            forex_data: Forex market data
            
        Returns:
            List[str]: List of risk factors
        """
        risks = []
        
        # Check data age
        max_age = timedelta(seconds=30)
        now = datetime.now()
        
        if now - crypto_data.timestamp > max_age:
            risks.append('STALE_CRYPTO_DATA')
        
        if now - forex_data.timestamp > max_age:
            risks.append('STALE_FOREX_DATA')
        
        # Check volatility (simplified)
        if crypto_data.high - crypto_data.low > crypto_data.close * Decimal('0.02'):
            risks.append('HIGH_CRYPTO_VOLATILITY')
        
        # Check session timing for forex
        if forex_data.session_info and not forex_data.session_info.is_active:
            risks.append('FOREX_SESSION_CLOSED')
        
        # Check liquidity
        min_volume_threshold = Decimal('1000')
        if crypto_data.volume < min_volume_threshold:
            risks.append('LOW_CRYPTO_LIQUIDITY')
        
        if forex_data.volume < min_volume_threshold:
            risks.append('LOW_FOREX_LIQUIDITY')
        
        # Regulatory risks
        risks.append('REGULATORY_RISK')  # Always present in crypto-forex arbitrage
        
        return risks
    
    def _calculate_confidence(self, crypto_data: UnifiedMarketData, 
                            forex_data: UnifiedMarketData, 
                            risk_factors: List[str]) -> float:
        """
        Calculate confidence score for crypto-forex arbitrage.
        
        Args:
            crypto_data: Crypto market data
            forex_data: Forex market data
            risk_factors: List of risk factors
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.7  # Base confidence for crypto-forex arbitrage
        
        # Adjust for data freshness
        max_age = timedelta(seconds=30)
        now = datetime.now()
        
        crypto_age = (now - crypto_data.timestamp).total_seconds()
        forex_age = (now - forex_data.timestamp).total_seconds()
        
        if crypto_age < 10 and forex_age < 10:
            base_confidence += 0.1  # Fresh data bonus
        
        # Adjust for risk factors
        risk_penalty = len(risk_factors) * 0.05
        base_confidence -= risk_penalty
        
        # Adjust for forex session activity
        if forex_data.session_info and forex_data.session_info.is_active:
            base_confidence += 0.1
        
        # Adjust for volume
        if crypto_data.volume > 10000 and forex_data.volume > 10000:
            base_confidence += 0.05  # Good liquidity bonus
        
        return max(0.1, min(0.95, base_confidence))
    
    def validate_parameters(self) -> bool:
        """
        Validate crypto-forex arbitrage strategy parameters.
        
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        try:
            if not super().validate_parameters():
                return False
            
            # Validate supported currencies
            if not self.supported_crypto_currencies:
                self.logger.error("No supported crypto currencies specified")
                return False
            
            if not self.supported_fiat_currencies:
                self.logger.error("No supported fiat currencies specified")
                return False
            
            # Validate conversion spread
            if self.max_conversion_spread <= 0 or self.max_conversion_spread > Decimal('0.01'):
                self.logger.error(f"Invalid conversion spread: {self.max_conversion_spread}")
                return False
            
            # Validate session overlap
            if self.min_session_overlap.total_seconds() <= 0:
                self.logger.error(f"Invalid session overlap: {self.min_session_overlap}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {e}")
            return False
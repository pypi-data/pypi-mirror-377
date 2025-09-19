"""
Triangular arbitrage strategy for multi-currency opportunities.

This strategy identifies triangular arbitrage opportunities within
a single market by exploiting price discrepancies between three
related currency pairs.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import combinations

from .cross_market_arbitrage_strategy import CrossMarketArbitrageStrategy, StrategyConfig
from ..models.data_models import UnifiedMarketData
from ..markets.types import MarketType, UnifiedSymbol
from ..analysis.arbitrage_detector import ArbitrageOpportunity, TriangularArbitrageChain


class TriangularArbitrageStrategy(CrossMarketArbitrageStrategy):
    """
    Triangular arbitrage strategy for multi-currency opportunities.
    
    This strategy identifies triangular arbitrage opportunities by finding
    price discrepancies between three related currency pairs within the same market.
    
    Example triangular arbitrage:
    1. BTC/USD -> ETH/BTC -> ETH/USD should equal direct BTC/USD rate
    2. EUR/USD -> GBP/EUR -> GBP/USD should equal direct EUR/USD rate
    
    The strategy:
    - Identifies currency triangles with sufficient liquidity
    - Calculates implied vs actual exchange rates
    - Executes three-step arbitrage when profitable
    - Manages execution timing and slippage risks
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the triangular arbitrage strategy.
        
        Args:
            config: Strategy configuration parameters
        """
        super().__init__(config)
        
        # Triangular arbitrage specific configuration
        self.base_currencies = config.parameters.get(
            'base_currencies', ['USD', 'BTC', 'ETH', 'EUR']
        )
        self.min_triangle_volume = Decimal(str(config.parameters.get('min_triangle_volume', 5000)))
        self.max_execution_steps = config.parameters.get('max_execution_steps', 3)
        
        # Timing and execution parameters
        self.max_step_delay = timedelta(seconds=config.parameters.get('max_step_delay_seconds', 2))
        self.triangle_expiry_time = timedelta(seconds=config.parameters.get('triangle_expiry_seconds', 15))
        
        # Risk parameters
        self.max_slippage_per_step = Decimal(str(config.parameters.get('max_slippage_per_step', 0.001)))  # 0.1%
        self.min_profit_after_slippage = Decimal(str(config.parameters.get('min_profit_after_slippage', 0.003)))  # 0.3%
        
        # Market-specific settings
        self.preferred_markets = config.parameters.get('preferred_markets', ['binance', 'coinbase', 'oanda'])
        self.market_priorities = {market: i for i, market in enumerate(self.preferred_markets)}
        
        # Triangle tracking
        self.active_triangles: Dict[str, TriangularArbitrageChain] = {}
        self.executed_triangles: List[TriangularArbitrageChain] = []
        self.triangle_success_rate: Dict[str, float] = {}
        
        self.logger = logging.getLogger(f"triangular_arbitrage.{self.name}")
    
    def _detect_arbitrage_opportunities(self, crypto_data: List[UnifiedMarketData], 
                                      forex_data: List[UnifiedMarketData]) -> List[ArbitrageOpportunity]:
        """
        Detect triangular arbitrage opportunities within each market.
        
        Args:
            crypto_data: Crypto market data
            forex_data: Forex market data
            
        Returns:
            List[ArbitrageOpportunity]: List of detected opportunities
        """
        opportunities = []
        
        try:
            # Group data by market/source
            crypto_by_market = self._group_data_by_market(crypto_data)
            forex_by_market = self._group_data_by_market(forex_data)
            
            # Find triangular opportunities in crypto markets
            for market, data in crypto_by_market.items():
                crypto_opportunities = self._find_triangular_opportunities_in_market(
                    data, market, MarketType.CRYPTO
                )
                opportunities.extend(crypto_opportunities)
            
            # Find triangular opportunities in forex markets
            for market, data in forex_by_market.items():
                forex_opportunities = self._find_triangular_opportunities_in_market(
                    data, market, MarketType.FOREX
                )
                opportunities.extend(forex_opportunities)
            
            # Filter and rank opportunities
            filtered_opportunities = self._filter_triangular_opportunities(opportunities)
            
            self.logger.debug(f"Detected {len(filtered_opportunities)} triangular arbitrage opportunities")
            
            return filtered_opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting triangular arbitrage opportunities: {e}")
            return []
    
    def _group_data_by_market(self, data: List[UnifiedMarketData]) -> Dict[str, List[UnifiedMarketData]]:
        """Group market data by source/market."""
        grouped = {}
        for item in data:
            market = item.source
            if market not in grouped:
                grouped[market] = []
            grouped[market].append(item)
        return grouped
    
    def _find_triangular_opportunities_in_market(self, market_data: List[UnifiedMarketData],
                                               market: str, 
                                               market_type: MarketType) -> List[ArbitrageOpportunity]:
        """
        Find triangular arbitrage opportunities within a single market.
        
        Args:
            market_data: Market data for a specific market
            market: Market/exchange name
            market_type: Type of market (crypto/forex)
            
        Returns:
            List[ArbitrageOpportunity]: List of opportunities
        """
        opportunities = []
        
        try:
            # Create symbol lookup for quick access
            symbol_data = {data.symbol.to_standard_format(): data for data in market_data}
            
            # Find all possible triangular chains
            triangular_chains = self._find_triangular_chains(symbol_data, market, market_type)
            
            # Evaluate each chain for arbitrage opportunities
            for chain in triangular_chains:
                opportunity = self._evaluate_triangular_chain(chain, symbol_data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error finding triangular opportunities in {market}: {e}")
            return []
    
    def _find_triangular_chains(self, symbol_data: Dict[str, UnifiedMarketData],
                               market: str, 
                               market_type: MarketType) -> List[TriangularArbitrageChain]:
        """
        Find all possible triangular arbitrage chains in the market.
        
        Args:
            symbol_data: Symbol data lookup
            market: Market/exchange name
            market_type: Type of market
            
        Returns:
            List[TriangularArbitrageChain]: List of triangular chains
        """
        chains = []
        
        try:
            # Extract all available currencies
            currencies = set()
            available_pairs = {}
            
            for symbol_str, data in symbol_data.items():
                base = data.symbol.base_asset
                quote = data.symbol.quote_asset
                currencies.add(base)
                currencies.add(quote)
                available_pairs[symbol_str] = (base, quote)
            
            # Find triangular chains for each base currency
            for base_currency in self.base_currencies:
                if base_currency not in currencies:
                    continue
                
                chains.extend(
                    self._find_chains_for_base_currency(
                        base_currency, currencies, available_pairs, symbol_data, market
                    )
                )
            
            return chains
            
        except Exception as e:
            self.logger.error(f"Error finding triangular chains: {e}")
            return []
    
    def _find_chains_for_base_currency(self, base_currency: str,
                                     currencies: Set[str],
                                     available_pairs: Dict[str, Tuple[str, str]],
                                     symbol_data: Dict[str, UnifiedMarketData],
                                     market: str) -> List[TriangularArbitrageChain]:
        """
        Find triangular chains for a specific base currency.
        
        Args:
            base_currency: Base currency for the triangle
            currencies: Set of all available currencies
            available_pairs: Available currency pairs
            symbol_data: Symbol data lookup
            market: Market name
            
        Returns:
            List[TriangularArbitrageChain]: List of chains for the base currency
        """
        chains = []
        
        try:
            # Find intermediate currencies that can form triangles
            for intermediate in currencies:
                if intermediate == base_currency:
                    continue
                
                for quote in currencies:
                    if quote == base_currency or quote == intermediate:
                        continue
                    
                    # Check if we can form a triangle: base -> intermediate -> quote -> base
                    triangle = self._check_triangle_feasibility(
                        base_currency, intermediate, quote, available_pairs, symbol_data, market
                    )
                    
                    if triangle:
                        chains.append(triangle)
            
            return chains
            
        except Exception as e:
            self.logger.error(f"Error finding chains for {base_currency}: {e}")
            return []
    
    def _check_triangle_feasibility(self, base: str, intermediate: str, quote: str,
                                   available_pairs: Dict[str, Tuple[str, str]],
                                   symbol_data: Dict[str, UnifiedMarketData],
                                   market: str) -> Optional[TriangularArbitrageChain]:
        """
        Check if a triangular arbitrage chain is feasible.
        
        Args:
            base: Base currency
            intermediate: Intermediate currency
            quote: Quote currency
            available_pairs: Available currency pairs
            symbol_data: Symbol data lookup
            market: Market name
            
        Returns:
            Optional[TriangularArbitrageChain]: Chain if feasible, None otherwise
        """
        try:
            # Find required pairs for the triangle
            pair1 = self._find_pair(base, intermediate, available_pairs, symbol_data)  # base/intermediate
            pair2 = self._find_pair(intermediate, quote, available_pairs, symbol_data)  # intermediate/quote
            pair3 = self._find_pair(base, quote, available_pairs, symbol_data)  # base/quote (direct)
            
            if not (pair1 and pair2 and pair3):
                return None
            
            # Get the actual data
            data1 = symbol_data[pair1['symbol']]
            data2 = symbol_data[pair2['symbol']]
            data3 = symbol_data[pair3['symbol']]
            
            # Check data freshness
            max_age = timedelta(seconds=30)
            now = datetime.now()
            
            if any((now - data.timestamp) > max_age for data in [data1, data2, data3]):
                return None
            
            # Check minimum volume requirements
            if any(data.volume < self.min_triangle_volume for data in [data1, data2, data3]):
                return None
            
            # Calculate implied rate through the triangle
            implied_rate = self._calculate_implied_rate(pair1, pair2, data1, data2)
            
            # Get actual direct rate
            actual_rate = self._get_direct_rate(pair3, data3)
            
            if implied_rate is None or actual_rate is None:
                return None
            
            # Calculate profit opportunity
            profit_opportunity = abs(implied_rate - actual_rate)
            profit_percentage = (profit_opportunity / actual_rate) * 100
            
            # Check if profitable after accounting for slippage
            total_slippage = self.max_slippage_per_step * 3  # Three steps
            if profit_percentage <= total_slippage * 100:
                return None
            
            # Determine execution sequence
            execution_sequence = self._determine_execution_sequence(
                base, intermediate, quote, implied_rate, actual_rate, pair1, pair2, pair3
            )
            
            # Create triangular chain
            chain = TriangularArbitrageChain(
                base_currency=base,
                intermediate_currency=intermediate,
                quote_currency=quote,
                symbol1=data1.symbol,
                symbol2=data2.symbol,
                symbol3=data3.symbol,
                market=market,
                implied_rate=implied_rate,
                actual_rate=actual_rate,
                profit_opportunity=profit_opportunity,
                execution_sequence=execution_sequence
            )
            
            return chain
            
        except Exception as e:
            self.logger.error(f"Error checking triangle feasibility: {e}")
            return None
    
    def _find_pair(self, currency1: str, currency2: str,
                   available_pairs: Dict[str, Tuple[str, str]],
                   symbol_data: Dict[str, UnifiedMarketData]) -> Optional[Dict[str, Any]]:
        """
        Find a currency pair in available data.
        
        Args:
            currency1: First currency
            currency2: Second currency
            available_pairs: Available currency pairs
            symbol_data: Symbol data lookup
            
        Returns:
            Optional[Dict[str, Any]]: Pair information if found
        """
        # Try direct pair (currency1/currency2)
        direct_symbol = f"{currency1}/{currency2}"
        if direct_symbol in available_pairs:
            return {
                'symbol': direct_symbol,
                'base': currency1,
                'quote': currency2,
                'inverted': False
            }
        
        # Try inverted pair (currency2/currency1)
        inverted_symbol = f"{currency2}/{currency1}"
        if inverted_symbol in available_pairs:
            return {
                'symbol': inverted_symbol,
                'base': currency2,
                'quote': currency1,
                'inverted': True
            }
        
        return None
    
    def _calculate_implied_rate(self, pair1: Dict[str, Any], pair2: Dict[str, Any],
                               data1: UnifiedMarketData, data2: UnifiedMarketData) -> Optional[Decimal]:
        """
        Calculate implied exchange rate through two pairs.
        
        Args:
            pair1: First pair information
            pair2: Second pair information
            data1: First pair data
            data2: Second pair data
            
        Returns:
            Optional[Decimal]: Implied rate if calculable
        """
        try:
            rate1 = data1.close
            rate2 = data2.close
            
            # Adjust for pair inversions
            if pair1['inverted']:
                rate1 = Decimal('1') / rate1
            
            if pair2['inverted']:
                rate2 = Decimal('1') / rate2
            
            # Calculate implied rate
            implied_rate = rate1 * rate2
            
            return implied_rate
            
        except Exception as e:
            self.logger.error(f"Error calculating implied rate: {e}")
            return None
    
    def _get_direct_rate(self, pair3: Dict[str, Any], data3: UnifiedMarketData) -> Optional[Decimal]:
        """
        Get direct exchange rate from pair data.
        
        Args:
            pair3: Direct pair information
            data3: Direct pair data
            
        Returns:
            Optional[Decimal]: Direct rate if available
        """
        try:
            rate = data3.close
            
            if pair3['inverted']:
                rate = Decimal('1') / rate
            
            return rate
            
        except Exception as e:
            self.logger.error(f"Error getting direct rate: {e}")
            return None
    
    def _determine_execution_sequence(self, base: str, intermediate: str, quote: str,
                                    implied_rate: Decimal, actual_rate: Decimal,
                                    pair1: Dict[str, Any], pair2: Dict[str, Any], 
                                    pair3: Dict[str, Any]) -> List[str]:
        """
        Determine the optimal execution sequence for the triangle.
        
        Args:
            base: Base currency
            intermediate: Intermediate currency
            quote: Quote currency
            implied_rate: Implied rate through triangle
            actual_rate: Actual direct rate
            pair1: First pair info
            pair2: Second pair info
            pair3: Direct pair info
            
        Returns:
            List[str]: Execution sequence
        """
        if implied_rate > actual_rate:
            # Triangle rate is higher, so execute triangle path
            return [
                f"BUY {pair1['symbol']}",
                f"BUY {pair2['symbol']}",
                f"SELL {pair3['symbol']}"
            ]
        else:
            # Direct rate is higher, so execute reverse
            return [
                f"BUY {pair3['symbol']}",
                f"SELL {pair2['symbol']}",
                f"SELL {pair1['symbol']}"
            ]
    
    def _evaluate_triangular_chain(self, chain: TriangularArbitrageChain,
                                  symbol_data: Dict[str, UnifiedMarketData]) -> Optional[ArbitrageOpportunity]:
        """
        Evaluate a triangular chain for arbitrage opportunity.
        
        Args:
            chain: Triangular arbitrage chain
            symbol_data: Symbol data lookup
            
        Returns:
            Optional[ArbitrageOpportunity]: Arbitrage opportunity if profitable
        """
        try:
            # Calculate net profit after fees and slippage
            gross_profit = chain.profit_opportunity
            
            # Estimate fees for three transactions
            estimated_fees = self._estimate_triangular_fees(chain, symbol_data)
            
            # Estimate slippage for three steps
            estimated_slippage = self._estimate_triangular_slippage(chain, symbol_data)
            
            net_profit = gross_profit - estimated_fees - estimated_slippage
            
            if net_profit <= 0:
                return None
            
            # Calculate profit percentage
            base_amount = min(
                symbol_data[chain.symbol1.to_standard_format()].volume,
                symbol_data[chain.symbol2.to_standard_format()].volume,
                symbol_data[chain.symbol3.to_standard_format()].volume
            ) * Decimal('0.01')  # Use 1% of minimum volume
            
            profit_percentage = (net_profit / (base_amount * chain.actual_rate)) * 100
            
            # Check minimum profit threshold
            if profit_percentage < self.min_profit_after_slippage * 100:
                return None
            
            # Create execution path
            execution_path = self._create_triangular_execution_path(chain, symbol_data, base_amount)
            
            # Assess risk factors
            risk_factors = self._assess_triangular_risks(chain, symbol_data)
            
            # Calculate confidence
            confidence = self._calculate_triangular_confidence(chain, symbol_data, risk_factors)
            
            # Determine time sensitivity
            time_sensitivity = 'HIGH' if profit_percentage > 1.0 else 'MEDIUM'
            
            opportunity = ArbitrageOpportunity(
                opportunity_type='TRIANGULAR',
                symbols=[chain.symbol1, chain.symbol2, chain.symbol3],
                markets=[chain.market],
                expected_profit=net_profit,
                profit_percentage=profit_percentage,
                execution_path=execution_path,
                risk_factors=risk_factors,
                confidence=confidence,
                time_sensitivity=time_sensitivity,
                detected_at=datetime.now(),
                expires_at=datetime.now() + self.triangle_expiry_time,
                minimum_capital=base_amount * chain.actual_rate,
                estimated_execution_time=self.max_step_delay * 3
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error evaluating triangular chain: {e}")
            return None
    
    def _estimate_triangular_fees(self, chain: TriangularArbitrageChain,
                                 symbol_data: Dict[str, UnifiedMarketData]) -> Decimal:
        """
        Estimate total fees for triangular arbitrage execution.
        
        Args:
            chain: Triangular arbitrage chain
            symbol_data: Symbol data lookup
            
        Returns:
            Decimal: Estimated total fees
        """
        # Typical trading fees (varies by market)
        fee_rates = {
            'binance': Decimal('0.001'),  # 0.1%
            'coinbase': Decimal('0.005'),  # 0.5%
            'oanda': Decimal('0.0001'),   # 0.01%
            'mt5': Decimal('0.0002')      # 0.02%
        }
        
        fee_rate = fee_rates.get(chain.market, Decimal('0.002'))  # Default 0.2%
        
        # Three transactions, so triple the fee
        total_fee_rate = fee_rate * 3
        
        # Estimate based on average price
        data1 = symbol_data[chain.symbol1.to_standard_format()]
        data2 = symbol_data[chain.symbol2.to_standard_format()]
        data3 = symbol_data[chain.symbol3.to_standard_format()]
        
        avg_price = (data1.close + data2.close + data3.close) / 3
        estimated_volume = min(data1.volume, data2.volume, data3.volume) * Decimal('0.01')
        
        return avg_price * estimated_volume * total_fee_rate
    
    def _estimate_triangular_slippage(self, chain: TriangularArbitrageChain,
                                     symbol_data: Dict[str, UnifiedMarketData]) -> Decimal:
        """
        Estimate slippage for triangular arbitrage execution.
        
        Args:
            chain: Triangular arbitrage chain
            symbol_data: Symbol data lookup
            
        Returns:
            Decimal: Estimated total slippage
        """
        # Conservative slippage estimate per step
        slippage_per_step = self.max_slippage_per_step
        total_slippage_rate = slippage_per_step * 3
        
        # Estimate based on average price and volume
        data1 = symbol_data[chain.symbol1.to_standard_format()]
        data2 = symbol_data[chain.symbol2.to_standard_format()]
        data3 = symbol_data[chain.symbol3.to_standard_format()]
        
        avg_price = (data1.close + data2.close + data3.close) / 3
        estimated_volume = min(data1.volume, data2.volume, data3.volume) * Decimal('0.01')
        
        return avg_price * estimated_volume * total_slippage_rate
    
    def _create_triangular_execution_path(self, chain: TriangularArbitrageChain,
                                        symbol_data: Dict[str, UnifiedMarketData],
                                        base_amount: Decimal) -> List[Dict[str, Any]]:
        """
        Create execution path for triangular arbitrage.
        
        Args:
            chain: Triangular arbitrage chain
            symbol_data: Symbol data lookup
            base_amount: Base amount to trade
            
        Returns:
            List[Dict[str, Any]]: Execution path steps
        """
        execution_path = []
        
        try:
            data1 = symbol_data[chain.symbol1.to_standard_format()]
            data2 = symbol_data[chain.symbol2.to_standard_format()]
            data3 = symbol_data[chain.symbol3.to_standard_format()]
            
            # Create three-step execution plan
            for i, (action, symbol, data) in enumerate([
                (chain.execution_sequence[0].split()[0], chain.symbol1.to_standard_format(), data1),
                (chain.execution_sequence[1].split()[0], chain.symbol2.to_standard_format(), data2),
                (chain.execution_sequence[2].split()[0], chain.symbol3.to_standard_format(), data3)
            ]):
                step = {
                    'action': action,
                    'symbol': symbol,
                    'market': chain.market,
                    'amount': float(base_amount),
                    'expected_price': float(data.close),
                    'timing': 'IMMEDIATE',
                    'step_delay': self.max_step_delay.total_seconds()
                }
                
                if i > 0:
                    step['dependencies'] = [f'step_{i}']
                
                execution_path.append(step)
            
            return execution_path
            
        except Exception as e:
            self.logger.error(f"Error creating triangular execution path: {e}")
            return []
    
    def _assess_triangular_risks(self, chain: TriangularArbitrageChain,
                               symbol_data: Dict[str, UnifiedMarketData]) -> List[str]:
        """
        Assess risk factors for triangular arbitrage.
        
        Args:
            chain: Triangular arbitrage chain
            symbol_data: Symbol data lookup
            
        Returns:
            List[str]: List of risk factors
        """
        risks = []
        
        try:
            # Check data freshness
            max_age = timedelta(seconds=30)
            now = datetime.now()
            
            for symbol in [chain.symbol1, chain.symbol2, chain.symbol3]:
                data = symbol_data[symbol.to_standard_format()]
                if now - data.timestamp > max_age:
                    risks.append('STALE_DATA')
                    break
            
            # Check execution timing risk
            if self.max_step_delay.total_seconds() > 5:
                risks.append('EXECUTION_TIMING_RISK')
            
            # Check liquidity
            min_volume = min(
                symbol_data[chain.symbol1.to_standard_format()].volume,
                symbol_data[chain.symbol2.to_standard_format()].volume,
                symbol_data[chain.symbol3.to_standard_format()].volume
            )
            
            if min_volume < self.min_triangle_volume * 2:
                risks.append('LIMITED_LIQUIDITY')
            
            # Check profit margin
            if chain.profit_opportunity < self.min_profit_threshold * 2:
                risks.append('LOW_PROFIT_MARGIN')
            
            # Multi-step execution risk
            risks.append('MULTI_STEP_EXECUTION')
            
            # Market-specific risks
            if chain.market not in self.preferred_markets:
                risks.append('NON_PREFERRED_MARKET')
            
            return risks
            
        except Exception as e:
            self.logger.error(f"Error assessing triangular risks: {e}")
            return ['ASSESSMENT_ERROR']
    
    def _calculate_triangular_confidence(self, chain: TriangularArbitrageChain,
                                       symbol_data: Dict[str, UnifiedMarketData],
                                       risk_factors: List[str]) -> float:
        """
        Calculate confidence for triangular arbitrage opportunity.
        
        Args:
            chain: Triangular arbitrage chain
            symbol_data: Symbol data lookup
            risk_factors: List of risk factors
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.6  # Base confidence for triangular arbitrage
        
        # Adjust for market preference
        if chain.market in self.preferred_markets:
            priority = self.market_priorities.get(chain.market, len(self.preferred_markets))
            base_confidence += (len(self.preferred_markets) - priority) * 0.05
        
        # Adjust for profit margin
        if chain.profit_opportunity > self.min_profit_threshold * 3:
            base_confidence += 0.1
        
        # Adjust for risk factors
        risk_penalty = len(risk_factors) * 0.08
        base_confidence -= risk_penalty
        
        # Adjust for historical success rate
        triangle_key = f"{chain.base_currency}-{chain.intermediate_currency}-{chain.quote_currency}"
        historical_success = self.triangle_success_rate.get(triangle_key, 0.7)
        base_confidence = (base_confidence + historical_success) / 2
        
        return max(0.1, min(0.9, base_confidence))
    
    def _filter_triangular_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        Filter triangular opportunities based on quality and feasibility.
        
        Args:
            opportunities: List of opportunities to filter
            
        Returns:
            List[ArbitrageOpportunity]: Filtered opportunities
        """
        filtered = []
        
        for opportunity in opportunities:
            try:
                # Check basic requirements
                if opportunity.profit_percentage < self.min_profit_after_slippage * 100:
                    continue
                
                if opportunity.estimated_execution_time > self.max_execution_time:
                    continue
                
                if len(opportunity.risk_factors) > 5:  # Too many risks
                    continue
                
                # Check confidence threshold
                if opportunity.confidence < 0.4:
                    continue
                
                # Check market preference
                if opportunity.markets[0] not in self.preferred_markets and len(filtered) > 3:
                    continue  # Limit non-preferred markets when we have better options
                
                filtered.append(opportunity)
                
            except Exception as e:
                self.logger.error(f"Error filtering triangular opportunity: {e}")
                continue
        
        # Sort by profit percentage and confidence
        filtered.sort(key=lambda x: (x.profit_percentage * x.confidence), reverse=True)
        
        # Limit to top opportunities to avoid overexecution
        return filtered[:5]
    
    def update_triangle_success_rate(self, triangle_key: str, successful: bool):
        """
        Update historical success rate for a triangle pattern.
        
        Args:
            triangle_key: Triangle identifier
            successful: Whether the execution was successful
        """
        if triangle_key not in self.triangle_success_rate:
            self.triangle_success_rate[triangle_key] = 0.7  # Default
        
        # Simple exponential moving average
        current_rate = self.triangle_success_rate[triangle_key]
        new_rate = 1.0 if successful else 0.0
        alpha = 0.2  # Learning rate
        
        self.triangle_success_rate[triangle_key] = current_rate * (1 - alpha) + new_rate * alpha
    
    def validate_parameters(self) -> bool:
        """
        Validate triangular arbitrage strategy parameters.
        
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        try:
            if not super().validate_parameters():
                return False
            
            # Validate base currencies
            if not self.base_currencies:
                self.logger.error("No base currencies specified")
                return False
            
            # Validate triangle volume
            if self.min_triangle_volume <= 0:
                self.logger.error(f"Invalid triangle volume: {self.min_triangle_volume}")
                return False
            
            # Validate execution parameters
            if self.max_step_delay.total_seconds() <= 0:
                self.logger.error(f"Invalid step delay: {self.max_step_delay}")
                return False
            
            if self.max_slippage_per_step <= 0:
                self.logger.error(f"Invalid slippage per step: {self.max_slippage_per_step}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {e}")
            return False
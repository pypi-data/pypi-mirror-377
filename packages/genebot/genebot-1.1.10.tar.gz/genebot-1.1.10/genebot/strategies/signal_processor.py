"""
Signal processor for handling trading signals from strategies.
"""

import logging
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading

from ..models.data_models import TradingSignal


class SignalPriority(Enum):
    """Priority levels for trading signals."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ProcessedSignal:
    """A processed trading signal with additional metadata."""
    original_signal: TradingSignal
    priority: SignalPriority
    processed_at: datetime
    confidence_adjusted: float
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SignalFilter:
    """Base class for signal filters."""
    
    def __init__(self, name: str):
        self.name = name
        
    def filter(self, signal: TradingSignal) -> bool:
        """
        Filter a trading signal.
        
        Args:
            signal: Trading signal to filter
            
        Returns:
            bool: True if signal should be kept, False if filtered out
        """
        return True


class ConfidenceFilter(SignalFilter):
    """Filter signals based on confidence threshold."""
    
    def __init__(self, min_confidence: float = 0.5):
        super().__init__("confidence_filter")
        self.min_confidence = min_confidence
        
    def filter(self, signal: TradingSignal) -> bool:
        """Filter based on confidence level."""
        return signal.confidence >= self.min_confidence


class DuplicateFilter(SignalFilter):
    """Filter duplicate signals within a time window."""
    
    def __init__(self, time_window_minutes: int = 5):
        super().__init__("duplicate_filter")
        self.time_window = timedelta(minutes=time_window_minutes)
        self.recent_signals: Dict[str, datetime] = {}
        self._lock = threading.Lock()
        
    def filter(self, signal: TradingSignal) -> bool:
        """Filter duplicate signals."""
        with self._lock:
            key = f"{signal.symbol}_{signal.action}_{signal.strategy_name}"
            now = signal.timestamp
            
            if key in self.recent_signals:
                last_time = self.recent_signals[key]
                if now - last_time < self.time_window:
                    return False  # Duplicate signal
                    
            self.recent_signals[key] = now
            
            # Clean up old entries
            cutoff_time = now - self.time_window
            self.recent_signals = {
                k: v for k, v in self.recent_signals.items() 
                if v > cutoff_time
            }
            
            return True


class SignalProcessor:
    """
    Processes trading signals from strategies with filtering, prioritization, and aggregation.
    
    The SignalProcessor handles:
    - Signal filtering and validation
    - Priority assignment and confidence adjustment
    - Signal aggregation and conflict resolution
    - Risk assessment and scoring
    """
    
    def __init__(self):
        """Initialize the signal processor."""
        self.filters: List[SignalFilter] = []
        self.priority_rules: List[Callable[[TradingSignal], SignalPriority]] = []
        self.confidence_adjusters: List[Callable[[TradingSignal], float]] = []
        self.risk_assessors: List[Callable[[TradingSignal], float]] = []
        
        # Statistics
        self.stats = {
            'total_signals_received': 0,
            'signals_filtered_out': 0,
            'signals_processed': 0,
            'last_processing_time': None
        }
        
        self._lock = threading.RLock()
        self.logger = logging.getLogger("signal_processor")
        
        # Add default filters
        self._add_default_filters()
        self._add_default_priority_rules()
        
    def add_filter(self, signal_filter: SignalFilter):
        """
        Add a signal filter.
        
        Args:
            signal_filter: Filter to add
        """
        with self._lock:
            self.filters.append(signal_filter)
            self.logger.info(f"Added filter: {signal_filter.name}")
    
    def remove_filter(self, filter_name: str) -> bool:
        """
        Remove a signal filter by name.
        
        Args:
            filter_name: Name of the filter to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        with self._lock:
            for i, f in enumerate(self.filters):
                if f.name == filter_name:
                    del self.filters[i]
                    self.logger.info(f"Removed filter: {filter_name}")
                    return True
            return False
    
    def add_priority_rule(self, rule: Callable[[TradingSignal], SignalPriority]):
        """
        Add a priority assignment rule.
        
        Args:
            rule: Function that takes a TradingSignal and returns SignalPriority
        """
        with self._lock:
            self.priority_rules.append(rule)
            self.logger.info("Added priority rule")
    
    def add_confidence_adjuster(self, adjuster: Callable[[TradingSignal], float]):
        """
        Add a confidence adjustment function.
        
        Args:
            adjuster: Function that takes a TradingSignal and returns adjusted confidence
        """
        with self._lock:
            self.confidence_adjusters.append(adjuster)
            self.logger.info("Added confidence adjuster")
    
    def add_risk_assessor(self, assessor: Callable[[TradingSignal], float]):
        """
        Add a risk assessment function.
        
        Args:
            assessor: Function that takes a TradingSignal and returns risk score
        """
        with self._lock:
            self.risk_assessors.append(assessor)
            self.logger.info("Added risk assessor")
    
    def process_signals(self, signals: List[TradingSignal]) -> List[ProcessedSignal]:
        """
        Process a list of trading signals.
        
        Args:
            signals: List of trading signals to process
            
        Returns:
            List[ProcessedSignal]: List of processed signals
        """
        if not signals:
            return []
            
        start_time = datetime.now()
        processed_signals = []
        
        with self._lock:
            self.stats['total_signals_received'] += len(signals)
            
            for signal in signals:
                try:
                    # Apply filters
                    if not self._apply_filters(signal):
                        self.stats['signals_filtered_out'] += 1
                        continue
                    
                    # Process the signal
                    processed_signal = self._process_single_signal(signal)
                    processed_signals.append(processed_signal)
                    self.stats['signals_processed'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing signal: {str(e)}")
                    self.stats['signals_filtered_out'] += 1
            
            # Resolve conflicts between signals
            processed_signals = self._resolve_conflicts(processed_signals)
            
            # Sort by priority and confidence
            processed_signals.sort(
                key=lambda s: (s.priority.value, s.confidence_adjusted), 
                reverse=True
            )
            
            self.stats['last_processing_time'] = datetime.now()
            
        processing_time = (datetime.now() - start_time).total_seconds()
        self.logger.debug(f"Processed {len(processed_signals)} signals in {processing_time:.3f}s")
        
        return processed_signals
    
    def _apply_filters(self, signal: TradingSignal) -> bool:
        """
        Apply all filters to a signal.
        
        Args:
            signal: Signal to filter
            
        Returns:
            bool: True if signal passes all filters, False otherwise
        """
        for signal_filter in self.filters:
            try:
                if not signal_filter.filter(signal):
                    self.logger.debug(f"Signal filtered out by {signal_filter.name}")
                    return False
            except Exception as e:
                self.logger.error(f"Error in filter {signal_filter.name}: {str(e)}")
                return False
        return True
    
    def _process_single_signal(self, signal: TradingSignal) -> ProcessedSignal:
        """
        Process a single trading signal.
        
        Args:
            signal: Signal to process
            
        Returns:
            ProcessedSignal: Processed signal with metadata
        """
        # Determine priority
        priority = self._calculate_priority(signal)
        
        # Adjust confidence
        confidence_adjusted = self._adjust_confidence(signal)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(signal)
        
        return ProcessedSignal(
            original_signal=signal,
            priority=priority,
            processed_at=datetime.now(),
            confidence_adjusted=confidence_adjusted,
            risk_score=risk_score,
            metadata={
                'original_confidence': signal.confidence,
                'processing_timestamp': datetime.now().isoformat()
            }
        )
    
    def _calculate_priority(self, signal: TradingSignal) -> SignalPriority:
        """Calculate signal priority using priority rules."""
        if not self.priority_rules:
            return SignalPriority.MEDIUM
            
        priorities = []
        for rule in self.priority_rules:
            try:
                priority = rule(signal)
                priorities.append(priority)
            except Exception as e:
                self.logger.error(f"Error in priority rule: {str(e)}")
                
        if not priorities:
            return SignalPriority.MEDIUM
            
        # Return the highest priority
        return max(priorities, key=lambda p: p.value)
    
    def _adjust_confidence(self, signal: TradingSignal) -> float:
        """Adjust signal confidence using confidence adjusters."""
        confidence = signal.confidence
        
        for adjuster in self.confidence_adjusters:
            try:
                confidence = adjuster(signal)
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
            except Exception as e:
                self.logger.error(f"Error in confidence adjuster: {str(e)}")
                
        return confidence
    
    def _calculate_risk_score(self, signal: TradingSignal) -> float:
        """Calculate risk score using risk assessors."""
        risk_scores = []
        
        for assessor in self.risk_assessors:
            try:
                risk_score = assessor(signal)
                risk_scores.append(risk_score)
            except Exception as e:
                self.logger.error(f"Error in risk assessor: {str(e)}")
                
        if not risk_scores:
            return 0.0
            
        # Return average risk score
        return sum(risk_scores) / len(risk_scores)
    
    def _resolve_conflicts(self, signals: List[ProcessedSignal]) -> List[ProcessedSignal]:
        """
        Resolve conflicts between signals for the same symbol.
        
        Args:
            signals: List of processed signals
            
        Returns:
            List[ProcessedSignal]: List with conflicts resolved
        """
        if len(signals) <= 1:
            return signals
            
        # Group signals by symbol
        symbol_groups: Dict[str, List[ProcessedSignal]] = {}
        for signal in signals:
            symbol = signal.original_signal.symbol
            if symbol not in symbol_groups:
                symbol_groups[symbol] = []
            symbol_groups[symbol].append(signal)
        
        resolved_signals = []
        
        for symbol, group_signals in symbol_groups.items():
            if len(group_signals) == 1:
                resolved_signals.extend(group_signals)
            else:
                # Resolve conflicts for this symbol
                resolved = self._resolve_symbol_conflicts(group_signals)
                resolved_signals.extend(resolved)
                
        return resolved_signals
    
    def _resolve_symbol_conflicts(self, signals: List[ProcessedSignal]) -> List[ProcessedSignal]:
        """
        Resolve conflicts for signals of the same symbol.
        
        Args:
            signals: List of signals for the same symbol
            
        Returns:
            List[ProcessedSignal]: Resolved signals
        """
        # Simple conflict resolution: keep the highest priority and confidence signal
        best_signal = max(signals, key=lambda s: (s.priority.value, s.confidence_adjusted))
        
        self.logger.debug(f"Resolved conflict for {best_signal.original_signal.symbol}: "
                         f"kept signal from {best_signal.original_signal.strategy_name}")
        
        return [best_signal]
    
    def _add_default_filters(self):
        """Add default signal filters."""
        self.add_filter(ConfidenceFilter(min_confidence=0.3))
        self.add_filter(DuplicateFilter(time_window_minutes=5))
    
    def _add_default_priority_rules(self):
        """Add default priority rules."""
        def confidence_priority_rule(signal: TradingSignal) -> SignalPriority:
            """Assign priority based on confidence level."""
            if signal.confidence >= 0.9:
                return SignalPriority.CRITICAL
            elif signal.confidence >= 0.7:
                return SignalPriority.HIGH
            elif signal.confidence >= 0.5:
                return SignalPriority.MEDIUM
            else:
                return SignalPriority.LOW
                
        self.add_priority_rule(confidence_priority_rule)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get signal processing statistics.
        
        Returns:
            Dict[str, Any]: Processing statistics
        """
        with self._lock:
            return self.stats.copy()
    
    def reset_statistics(self):
        """Reset processing statistics."""
        with self._lock:
            self.stats = {
                'total_signals_received': 0,
                'signals_filtered_out': 0,
                'signals_processed': 0,
                'last_processing_time': None
            }
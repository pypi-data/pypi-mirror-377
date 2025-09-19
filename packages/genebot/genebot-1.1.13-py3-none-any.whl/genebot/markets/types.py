"""
Core market types and data structures for multi-market trading.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re


class MarketType(Enum):
    """Enumeration of supported market types."""
    CRYPTO = "crypto"
    FOREX = "forex"


@dataclass
class UnifiedSymbol:
    """
    Normalized symbol representation across different markets.
    
    This class provides a unified way to represent trading symbols
    across crypto and forex markets, handling different naming conventions.
    """
    base_asset: str
    quote_asset: str
    market_type: MarketType
    native_symbol: str  # Original exchange/broker symbol
    
    def __post_init__(self):
        """Validate and normalize symbol components."""
        self.base_asset = self.base_asset.upper()
        self.quote_asset = self.quote_asset.upper()
        
        # Validate asset names
        if not self.base_asset or not self.quote_asset:
            raise ValueError("Base and quote assets cannot be empty")
        
        # Validate native symbol format
        if not self.native_symbol:
            raise ValueError("Native symbol cannot be empty")
    
    def to_standard_format(self) -> str:
        """
        Convert to standard format (e.g., BTC/USD, EUR/USD).
        
        Returns:
            str: Symbol in standard format with forward slash separator
        """
        return f"{self.base_asset}/{self.quote_asset}"
    
    def to_crypto_format(self) -> str:
        """
        Convert to typical crypto exchange format (e.g., BTCUSDT).
        
        Returns:
            str: Symbol in crypto exchange format
        """
        return f"{self.base_asset}{self.quote_asset}"
    
    def to_forex_format(self) -> str:
        """
        Convert to typical forex format (e.g., EURUSD).
        
        Returns:
            str: Symbol in forex format
        """
        return f"{self.base_asset}{self.quote_asset}"
    
    @classmethod
    def from_standard_format(cls, symbol: str, market_type: MarketType, 
                           native_symbol: Optional[str] = None) -> 'UnifiedSymbol':
        """
        Create UnifiedSymbol from standard format (e.g., BTC/USD).
        
        Args:
            symbol: Symbol in standard format with forward slash
            market_type: Type of market this symbol belongs to
            native_symbol: Original exchange/broker symbol (optional)
            
        Returns:
            UnifiedSymbol: New instance created from standard format
            
        Raises:
            ValueError: If symbol format is invalid
        """
        if '/' not in symbol:
            raise ValueError(f"Invalid standard format symbol: {symbol}. Expected format: BASE/QUOTE")
        
        parts = symbol.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid standard format symbol: {symbol}. Expected format: BASE/QUOTE")
        
        base_asset, quote_asset = parts
        native = native_symbol or symbol.replace('/', '')
        
        return cls(
            base_asset=base_asset,
            quote_asset=quote_asset,
            market_type=market_type,
            native_symbol=native
        )
    
    @classmethod
    def from_crypto_symbol(cls, symbol: str, native_symbol: Optional[str] = None) -> 'UnifiedSymbol':
        """
        Create UnifiedSymbol from crypto exchange symbol (e.g., BTCUSDT).
        
        Args:
            symbol: Crypto symbol without separator
            native_symbol: Original exchange symbol (optional)
            
        Returns:
            UnifiedSymbol: New instance for crypto market
            
        Raises:
            ValueError: If symbol cannot be parsed
        """
        # Common crypto quote assets (ordered by length, longest first)
        quote_assets = ['USDT', 'USDC', 'BUSD', 'DAI', 'USD', 'BTC', 'ETH', 'BNB', 'EUR', 'GBP']
        
        for quote in quote_assets:
            if symbol.upper().endswith(quote):
                base = symbol.upper()[:-len(quote)]
                if base:  # Ensure base asset is not empty
                    return cls(
                        base_asset=base,
                        quote_asset=quote,
                        market_type=MarketType.CRYPTO,
                        native_symbol=native_symbol or symbol
                    )
        
        raise ValueError(f"Cannot parse crypto symbol: {symbol}")
    
    @classmethod
    def from_forex_symbol(cls, symbol: str, native_symbol: Optional[str] = None) -> 'UnifiedSymbol':
        """
        Create UnifiedSymbol from forex symbol (e.g., EURUSD).
        
        Args:
            symbol: Forex symbol (typically 6 characters)
            native_symbol: Original broker symbol (optional)
            
        Returns:
            UnifiedSymbol: New instance for forex market
            
        Raises:
            ValueError: If symbol format is invalid
        """
        # Remove common forex suffixes and separators
        clean_symbol = re.sub(r'[._-]', '', symbol.upper())
        
        # Standard forex pairs are 6 characters (3+3)
        if len(clean_symbol) == 6:
            base_asset = clean_symbol[:3]
            quote_asset = clean_symbol[3:]
            
            return cls(
                base_asset=base_asset,
                quote_asset=quote_asset,
                market_type=MarketType.FOREX,
                native_symbol=native_symbol or symbol
            )
        
        raise ValueError(f"Invalid forex symbol format: {symbol}. Expected 6 characters (e.g., EURUSD)")
    
    def is_crypto_pair(self) -> bool:
        """Check if this is a cryptocurrency pair."""
        return self.market_type == MarketType.CRYPTO
    
    def is_forex_pair(self) -> bool:
        """Check if this is a forex pair."""
        return self.market_type == MarketType.FOREX
    
    def __str__(self) -> str:
        """String representation in standard format."""
        return self.to_standard_format()
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"UnifiedSymbol(base='{self.base_asset}', quote='{self.quote_asset}', "
                f"market={self.market_type.value}, native='{self.native_symbol}')")
    
    def __eq__(self, other) -> bool:
        """Check equality based on all fields."""
        if not isinstance(other, UnifiedSymbol):
            return False
        return (self.base_asset == other.base_asset and 
                self.quote_asset == other.quote_asset and
                self.market_type == other.market_type)
    
    def __hash__(self) -> int:
        """Hash based on base asset, quote asset, and market type."""
        return hash((self.base_asset, self.quote_asset, self.market_type))
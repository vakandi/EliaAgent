# Markov MCP - Market Analysis Tools

**MCP Server**: `markov`  
**Purpose**: Real-time market data, technical analysis, sentiment analysis, and backtesting

## Available Tools

### Market Data

#### `market_snapshot`
Get comprehensive global market overview.
```
Parameters: None required
Returns: S&P500, NASDAQ, VIX, BTC, ETH, EUR/USD, SPY, GLD
```

#### `yahoo_price`
Get real-time quote for any asset.
```
Parameters:
- symbol: Asset symbol
  Forex: "EURUSD=X", "GBPUSD=X", "USDJPY=X", "DXY=X"
  Crypto: "BTC-USD", "ETH-USD"
  Stocks: "AAPL", "TSLA", "NVDA"
  ETFs: "SPY", "QQQ", "GLD"
  Indices: "^GSPC", "^IXIC", "^VIX"
```

### Technical Analysis

#### `get_technical_analysis`
Full technical analysis with 23+ indicators.
```
Parameters:
- symbol: Trading pair (e.g., "BTCUSDT", "EURUSD", "XAUUSD")
- exchange: "KUCOIN" | "BINANCE" | "NYSE" | "NASDAQ" | "FOREX"
- timeframe: "1m" | "5m" | "15m" | "1h" | "4h" | "1D" | "1W"

Preferred Settings by Asset:
- XAUUSD: exchange="FOREX", primary=1D, confirmation=4H, entry=15m
- BTC/USDT: exchange="KUCOIN", primary=1D, confirmation=4H, entry=1H
- EUR/USD: exchange="FOREX", primary=4H, confirmation=1D, entry=1H
```

#### `get_bollinger_band_analysis`
Proprietary Bollinger Band rating system (-3 to +3).
```
Parameters: symbol, exchange, timeframe
Returns: BBW (Bandwidth), Rating (-3 to +3), Position within bands
```

#### `get_candlestick_patterns`
Detect 15+ candlestick patterns.
```
Parameters: symbol, exchange, timeframe
Returns: Detected patterns with buy/sell signals
```

#### `get_multi_timeframe_analysis`
Analyze trend alignment across timeframes.
```
Parameters: symbol, exchange
Returns: Weekly → Daily → 4H → 1H → 15m analysis
```

#### `get_stock_decision`
3-layer decision engine.
```
Parameters: symbol, exchange
Returns: Recommendation + ranking + trade setup + quality score
```

### Backtesting

#### `backtest_strategy`
Test one strategy with institutional metrics.
```
Parameters:
- strategy: "rsi" | "bollinger" | "macd" | "ema_cross" | "supertrend" | "donchian"
- symbol: Trading pair
- period: "1mo" | "3mo" | "6mo" | "1y" | "2y" | "5y"
Returns: Win Rate, Total Return, Sharpe Ratio, Calmar Ratio, Max Drawdown, Profit Factor
```

#### `compare_strategies`
Run all 6 strategies on same symbol.
```
Parameters: symbol, period
Returns: Ranked list of all strategies with metrics
```

### Sentiment & News

#### `market_sentiment`
Reddit-based sentiment analysis.
```
Parameters: tickers: "crypto" | "stocks" | specific symbols
Returns: Bullish/Bearish score (-1 to +1)
  - Score > +0.3: Extremely Bullish
  - Score +0.1 to +0.3: Moderately Bullish
  - Score -0.1 to +0.1: Neutral
  - Score -0.3 to -0.1: Moderately Bearish
  - Score < -0.3: Extremely Bearish
```

#### `financial_news`
Live RSS news from major sources.
```
Parameters: symbols (optional)
Returns: Headlines from Reuters, CoinDesk, CoinTelegraph
```

#### `combined_analysis`
POWER TOOL – Technical + Sentiment + News confluence.
```
Parameters: symbol, exchange, include_news=true, include_sentiment=true
Returns: Final BUY/SELL/HOLD with confidence %
```

## Error Handling

If `markov` MCP is not available:
1. Check if MCP is loaded: Look for `markov_*` tools
2. If tools missing, the MCP server may not be running
3. Fallback: Use `yahoo_price` from this skill if available
4. Alternative: Use web search for market data

## Symbol Reference

### Tier 1 (Always Active)
| Asset | Yahoo Symbol | TV Symbol | Exchange | Priority |
|-------|--------------|-----------|----------|----------|
| Gold | XAUUSD | XAUUSD | FOREX | #1 |
| Dollar Index | DXY=X | DXY | - | #2 |
| EUR/USD | EURUSD=X | EURUSD | FOREX | #3 |
| Bitcoin | BTC-USD | BTCUSDT | KUCOIN | #4 |

### Tier 2 (Conditional)
| Asset | Yahoo Symbol | TV Symbol | Trigger |
|-------|--------------|-----------|---------|
| S&P 500 | ^GSPC | US500 | Risk sentiment |
| GBP/USD | GBPUSD=X | GBPUSD | UK data events |
| ETH | ETH-USD | ETHUSDT | Crypto correlation |
| USD/JPY | USDJPY=X | USDJPY | BoJ events |

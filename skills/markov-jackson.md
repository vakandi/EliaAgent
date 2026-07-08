# Markov MCP Jackson - Desktop Control

**MCP Server**: `tradingview-jackson`  
**Purpose**: Control live Markov Desktop chart via CDP (Chrome DevTools Protocol)

**Prerequisites**: Markov Desktop app running with CDP port 9222 enabled

## Architecture

```
OpenCode ←→ MCP Server (stdio) ←→ CDP (localhost:9222) ←→ Markov Desktop (Electron)
```

## Decision Tree — Which Tool When

### "What's on my chart right now?"
1. `chart_get_state` → symbol, timeframe, chart type, all indicators with entity IDs
2. `data_get_study_values` → current numeric values from indicators (RSI, MACD, EMAs, etc.)
3. `quote_get` → real-time price, OHLC, volume

### "What levels/lines/labels are showing?"
Custom Pine indicators draw with `line.new()`, `label.new()`, `table.new()`. Use:
- `data_get_pine_lines` → horizontal price levels (deduplicated, sorted high→low)
- `data_get_pine_labels` → text annotations with prices
- `data_get_pine_tables` → formatted table data
- `data_get_pine_boxes` → price zones as {high, low} pairs

### "Give me price data"
- `data_get_ohlcv` with `summary: true` → compact stats (high, low, range, change%, volume)
- `quote_get` → single latest price snapshot

### "Analyze my chart" (full report)
1. `quote_get` → current price
2. `data_get_study_values` → all indicator readings
3. `data_get_pine_lines` → key price levels
4. `data_get_pine_labels` → labeled levels
5. `data_get_pine_tables` → session stats
6. `data_get_ohlcv` with `summary: true` → price action summary
7. `capture_screenshot` → visual confirmation

### "Change the chart"
- `chart_set_symbol` → switch ticker ("AAPL", "ES1!", "XAUUSD")
- `chart_set_timeframe` → switch resolution ("1", "5", "15", "60", "D", "W")
- `chart_set_type` → switch chart style (Candles, HeikinAshi, Line, etc.)
- `chart_manage_indicator` → add/remove studies

### "Work on Pine Script"
1. `pine_set_source` → inject code into editor
2. `pine_smart_compile` → compile with error check
3. `pine_get_errors` → read compilation errors
4. `pine_save` → save to TradingView cloud

### "Practice with Replay"
1. `replay_start` with `date: "2025-01-15"` → enter replay mode
2. `replay_step` → advance one bar
3. `replay_autoplay` → auto-advance
4. `replay_trade` with `action: "buy"/"sell"/"close"` → execute trades
5. `replay_status` → check position, P&L, current date
6. `replay_stop` → return to realtime

### "Screen multiple symbols"
- `batch_run` with `symbols: ["ES1!", "NQ1!"]` and `action: "screenshot"` or `"get_ohlcv"`

### "Draw on the chart"
- `draw_shape` → horizontal_line, trend_line, rectangle, text
- `draw_list` → see what's drawn
- `draw_remove_one` → remove by ID
- `draw_clear` → remove all

### "Manage alerts"
- `alert_create` → set price alert
- `alert_list` → view active alerts
- `alert_delete` → remove alerts

### "TradingView isn't running"
- `tv_launch` → auto-detect and launch TradingView with CDP
- `tv_health_check` → verify connection

## Output Size Guidelines

| Tool | Typical Output |
|------|---------------|
| `quote_get` | ~200 bytes |
| `data_get_study_values` | ~500 bytes |
| `data_get_pine_lines` | ~1-3 KB |
| `data_get_ohlcv` (summary) | ~500 bytes |
| `capture_screenshot` | ~300 bytes (file path) |

## Context Management Rules

1. **Always use `summary: true` on `data_get_ohlcv`** unless you need individual bars
2. **Always use `study_filter`** when you know which indicator you want
3. **Never use `verbose: true`** unless specifically asked
4. **Avoid `pine_get_source`** on complex scripts (can be 200KB+)
5. **Use `capture_screenshot`** for visual context instead of large datasets
6. **Call `chart_get_state` once** at start, then reference entity IDs
7. **Cap OHLCV requests**: `count: 20` quick, `count: 100` deeper, `count: 500` only when needed

## Tool Conventions

- All tools return `{ success: true/false, ... }`
- Entity IDs are session-specific — don't cache across sessions
- Pine indicators must be **visible** on chart for pine graphics tools
- `chart_manage_indicator` requires **full names**: "Relative Strength Index" not "RSI"
- Screenshots save to `screenshots/` directory
- OHLCV capped at 500 bars, trades at 20 per request

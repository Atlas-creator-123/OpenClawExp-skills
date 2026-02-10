# 📈 Stock Analysis Skill

Multi-source stock analysis tool for OpenClaw. Analyzes Chinese and US stocks using real-time data from 雪球 (Xueqiu) via browser scraping.

## Features

- 📊 **Real-time Market Data** - Price, volume, PE, PB, market cap
- 📈 **Technical Indicators** - MA, RSI, support/resistance levels
- 🗣️ **Market Sentiment** - Bullish/bearish arguments from 雪球 discussions
- 💡 **Comprehensive Assessment** - Technical/fundamental scores
- 🎯 **Actionable Recommendations** - Short/medium/long-term advice

## Quick Start

```bash
# Navigate to skill scripts
cd "/Users/Spike/Library/Application Support/OpenClaw/skills/stock-analysis/scripts"

# Run analysis
python3 stock_analysis_xueqiu.py BABA       # Alibaba (US)
python3 stock_analysis_xueqiu.py 0700.HK    # Tencent (HK)
python3 stock_analysis_xueqiu.py SH600900    # 长江电力 (China A-share)
```

## Output Example

```
======================================================================
        📊 BABA Comprehensive Stock Analysis
======================================================================

💰 REAL-TIME MARKET DATA (Source: 雪球)
--------------------------------------------------
  Current Price:     $166.09
  Change:            +1.90% (+3.09)
  PE (TTM):          22.22
  ...

📊 TECHNICAL ANALYSIS
--------------------------------------------------
  MA5:               $165.76
  RSI(14):            65

💡 COMPREHENSIVE ASSESSMENT
======================================================================
  Technical Score:     ████░░ (4/6) - BULLISH
  Market Sentiment:   ████░░ (4/6) - POSITIVE

🎯 RECOMMENDATION
======================================================================
  SHORT-TERM (1-3 months): ⚠️ CAUTIOUS
  MEDIUM-TERM (6-12 months): ✅ BULLISH
  LONG-TERM: ✅ HOLD
```

## Scripts

| Script | Purpose | Data Source |
|--------|---------|-------------|
| `stock_analysis_xueqiu.py` | Multi-source analysis | 雪球 (Recommended) |
| `stock_analysis.py` | Yahoo Finance version | Yahoo Finance |
| `stock_quant.py` | Technical indicators | Yahoo Finance |
| `stock_chart.py` | Price charts | Yahoo Finance |
| `stock_fundamental.py` | Fundamental analysis | Yahoo Finance |

## Supported Markets

| Market | Examples |
|--------|----------|
| US | BABA, NVDA, AAPL, TSLA |
| Hong Kong | 0700.HK, 9988.HK, BABA.HK |
| China A | 600519.SH, 000001.SZ, SH600900 |

## Why 雪球 Version?

✅ Solves 403 Forbidden issue for Chinese users
✅ More accurate real-time data
✅ Includes market sentiment from Chinese investors
✅ Better timing for Chinese market

## Browser Integration

This skill uses OpenClaw's browser automation to scrape 雪球 for real-time data. No API keys required!

## License

MIT

## Contributing

Feel free to submit issues and pull requests!

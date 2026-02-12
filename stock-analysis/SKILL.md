---
name: stock-analysis
description: Comprehensive stock analysis with technical indicators, fundamental estimates, capital flow, and macro analysis. Use for any stock analysis, investment research, or market data queries. Supports 雪球 browser scraping for Chinese stocks.
---

# Stock Analysis Skill

## Scripts Overview

| Script | Purpose | Data Source |
|--------|---------|-------------|
| `stock_chart.py` | Price & volume chart | Yahoo Finance |
| `stock_quant.py` | Technical indicators | Yahoo Finance |
| `stock_analysis.py` | Comprehensive report | Yahoo Finance |
| `stock_analysis_xueqiu.py` | Multi-source analysis | 雪球 + Browser |
| `stock_analysis_html.py` | **NEW** HTML report generator | JSON input |

---

## Usage

```bash
# Price chart
python scripts/stock_chart.py <SYMBOL>

# Technical analysis only
python scripts/stock_quant.py <SYMBOL>

# Full comprehensive analysis (Yahoo Finance)
python scripts/stock_analysis.py <SYMBOL> --market <HK|US|CN>

# Enhanced multi-source analysis (雪球 browser)
python scripts/stock_analysis_xueqiu.py <SYMBOL>

# Generate HTML report from JSON data
python scripts/stock_analysis_html.py <JSON_FILE> [--upload HOST]
```

### Examples

```bash
# Enhanced version with 雪球 (RECOMMENDED)
python scripts/stock_analysis_xueqiu.py BABA       # Alibaba US
python scripts/stock_analysis_xueqiu.py 0700.HK   # Tencent HK
python scripts/stock_analysis_xueqiu.py SH600900    # 长江电力 CN

# Yahoo Finance version (if available)
python scripts/stock_analysis.py NVDA --market US      # NVIDIA US
python scripts/stock_analysis.py 0700.HK --market HK  # Tencent HK
python scripts/stock_analysis.py 600519.SH --market CN # Maotai CN
```

---

## stock_analysis_xueqiu.py - Multi-Source Enhanced Analysis

### Features

1. **📊 Real-time Market Data**
   - Price, volume, market cap
   - PE, PB, dividend metrics
   - 52-week range

2. **📈 Technical Indicators**
   - MA(5/20/60)
   - RSI(14)
   - Support/resistance levels
   - 52-week position

3. **🗣️ Market Sentiment (雪球)**
   - Bullish arguments
   - Bearish arguments
   - Key news highlights
   - User discussions

4. **💡 Comprehensive Assessment**
   - Technical/fundamental/sentiment scores
   - Catalysts & risks
   - Short/medium/long-term recommendations

### Output Example

```
======================================================================
        📊 BABA Comprehensive Stock Analysis
======================================================================
🕐 Generated: 2026-02-11 01:36

💰 REAL-TIME MARKET DATA (Source: 雪球)
--------------------------------------------------
  Current Price:     $166.09
  Change:            +1.90% (+3.09)
  ...

📈 KEY METRICS
--------------------------------------------------
  PE (TTM):          22.22
  PB:                 2.65
  ...

📊 TECHNICAL ANALYSIS
--------------------------------------------------
  MA5:               $165.76
  RSI(14):            65
  52W Position:       72.8%

💡 COMPREHENSIVE ASSESSMENT
======================================================================
  Technical Score:     ████░░ (4/6) - BULLISH
  Fundamental Score:  ███░░░ (3/6) - NEUTRAL
  Market Sentiment:   ████░░ (4/6) - POSITIVE
  ...
```

---

## stock_analysis_html.py - HTML Report Generator

### Features

Generates beautiful, responsive HTML reports from stock analysis data.

1. **📊 Visual Dashboard**
   - Gradient dark theme with modern UI
   - Real-time price display with color-coded changes
   - Score meters (technical/fundamental/sentiment)

2. **📈 Chart Integration**
   - Inline SVG charts for price and volume
   - Technical indicator visualization

3. **☁️ Tencent Cloud COS Upload (RECOMMENDED)**
   - Upload HTML reports to Tencent Cloud COS
   - Generate shareable HTTPS URLs
   - Secure and fast CDN access
   - Supports inline credentials or environment variables

### Usage

```bash
# Generate HTML from JSON file
python scripts/stock_analysis_html.py <SYMBOL> <DATA.json> [OUTPUT.html]

# Generate and upload to COS (inline credentials)
python scripts/stock_analysis_html.py BABA data.json --cos \
    --secret-id YOUR_SECRET_ID \
    --secret-key YOUR_SECRET_KEY \
    --region ap-shanghai \
    --bucket your-bucket-name

# Upload existing HTML to COS
python scripts/stock_analysis_html.py --upload report.html --cos \
    --secret-id YOUR_SECRET_ID \
    --secret-key YOUR_SECRET_KEY \
    --region ap-shanghai \
    --bucket your-bucket-name
```

### Environment Variables (Optional)

Set default COS credentials for repeated use:

```bash
export TENCENT_COS_SECRET_ID="your_secret_id"
export TENCENT_COS_SECRET_KEY="your_secret_key"
export TENCENT_COS_REGION="ap-shanghai"
export TENCENT_COS_BUCKET="your-bucket-name"
```

Then simply use `--cos` without credentials:

```bash
python scripts/stock_analysis_html.py BABA data.json --cos
```

### COS URL Format

Uploaded files are accessible at:
```
https://{bucket}.cos.{region}.myqcloud.com/stock-reports/{filename}.html
```

Example:
```
https://my-stock-bucket.cos.ap-shanghai.myqcloud.com/stock-reports/BABA_report.html
```

### Integration

The HTML generator works with `stock_analysis_xueqiu.py` output:

1. Run xueqiu analysis to get raw data
2. Generate HTML report
3. Upload to COS
4. Share the HTTPS URL

---

## stock_analysis.py - Yahoo Finance Version

### Five Sections:

1. **📈 Technical Analysis**
   - Price & 52-week range
   - MA(5/20/60)
   - RSI(14), MACD
   - Bollinger Bands
   - Volatility, Max Drawdown, Sharpe Ratio

2. **💼 Fundamental Analysis**
   - Sector classification
   - Estimated PE, EPS, PEG
   - Growth rate estimate
   - Monthly performance vs 30-day high/low

3. **💰 Capital Flow**
   - Volume analysis
   - Trend detection (increasing/decreasing)

4. **🌍 Macro Environment**
   - Interest rates
   - Inflation/GDP
   - Market-specific notes

5. **🎯 Summary & Recommendation**
   - Technical signal (Bullish/Neutral/Bearish)
   - Risk assessment
   - Disclaimer

---

## Supported Markets

| Market | Code Examples |
|--------|---------------|
| Hong Kong | 0700.HK, 9988.HK, BABA.HK |
| US | NVDA, AAPL, TSLA, MSFT, BABA |
| China A | 600519.SH, 000001.SZ, SH600900 |
| Europe | BMW.DE, SAP.DE |
| Japan | 7203.T, 9984.T |

---

## Data Sources

### Enhanced Version (stock_analysis_xueqiu.py)

| Data Type | Source |
|-----------|--------|
| Real-time price | 雪球 Browser |
| Market metrics | 雪球 Browser |
| Discussions | 雪球 Browser |
| Technical indicators | Calculated |

### Yahoo Finance Version (stock_analysis.py)

| Data Type | Source |
|-----------|--------|
| Price/Volume | Yahoo Finance API |
| Technical | Calculated from price |
| Fundamental | Sector estimates |
| Macro | Built-in economic data |

---

## Browser Integration

For Chinese stocks (A-shares, HK stocks), **use stock_analysis_xueqiu.py** which leverages browser scraping of 雪球 for:

✅ Real-time prices (more accurate)
✅ Chinese market context
✅ Investor sentiment from discussions
✅ Local news coverage
✅ Better market timing

### Browser Setup

1. Ensure OpenClaw browser gateway is running
2. Browser will automatically open 雪球 pages
3. Data extracted from browser snapshots

---

## Cache

- Location: `~/.cache/stock_data/`
- Price data cached for 1 hour (Yahoo version)
- Browser data is real-time (no cache)

---

## Quick Start

```bash
# Navigate to skill scripts
cd "/Users/Spike/Library/Application Support/OpenClaw/skills/stock-analysis/scripts"

# Test with Alibaba (recommended)
python3 stock_analysis_xueqiu.py BABA

# Test with Hong Kong stock
python3 stock_analysis_xueqiu.py 0700.HK

# Test with Chinese A-share
python3 stock_analysis_xueqiu.py SH600900
```

---

## Integration with OpenClaw

The skill automatically:
- Opens browser to 雪球 for Chinese stocks
- Scrapes real-time data
- Analyzes market sentiment
- Generates comprehensive reports

No API keys needed for 雪球 version!

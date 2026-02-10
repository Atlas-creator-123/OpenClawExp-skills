#!/usr/bin/env python3
"""
Comprehensive Stock Analysis - Technical, Fundamental, Capital Flow, and Macro Analysis.
Usage: python stock_analysis.py <SYMBOL> [--market HK|US|CN]
Example: python stock_analysis.py NVDA --market US
         python stock_analysis.py 0700.HK --market HK
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
import urllib.request

CACHE_DIR = os.path.expanduser("~/.cache/stock_data")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(symbol):
    return os.path.join(CACHE_DIR, f"{symbol.replace('.', '_')}_full.json")

def load_cache(symbol, hours=1):
    cache_path = get_cache_path(symbol)
    if os.path.exists(cache_path):
        file_age = os.path.getmtime(cache_path)
        age_hours = (datetime.now().timestamp() - file_age) / 3600
        if age_hours < hours:
            with open(cache_path) as f:
                return json.load(f)
    return None

def save_cache(symbol, data):
    cache_path = get_cache_path(symbol)
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)

# ==================== TECHNICAL ANALYSIS ====================

def moving_average(data, period):
    if len(data) < period: return None
    return sum(data[-period:]) / period

def exponential_moving_average(data, period):
    if len(data) < period: return None
    multiplier = 2 / (period + 1)
    ema = data[-period]
    for price in data[-period:]:
        ema = price * multiplier + ema * (1 - multiplier)
    return ema

def rsi(prices, period=14):
    if len(prices) < period + 1: return None
    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        gains.append(change if change > 0 else 0)
        losses.append(abs(change) if change < 0 else 0)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(prices, fast=12, slow=26):
    ema_fast = exponential_moving_average(prices, fast)
    ema_slow = exponential_moving_average(prices, slow)
    if ema_fast is None or ema_slow is None: return None, None
    return ema_fast - ema_slow, exponential_moving_average(prices[-26:], 9)

def bollinger_bands(prices, period=20):
    if len(prices) < period: return None, None, None
    sma = moving_average(prices, period)
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std = variance ** 0.5
    return sma + (2 * std), sma, sma - (2 * std)

def volatility(returns):
    if len(returns) < 2: return None
    daily_vol = ((sum((r - sum(returns)/len(returns))**2 for r in returns) / (len(returns) - 1)) ** 0.5)
    return daily_vol * (252 ** 0.5) * 100

def max_drawdown(prices):
    max_price = max(prices)
    return max((max_price - p) / max_price for p in prices) * 100

def daily_returns(closes):
    return [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]

def sharpe_ratio(returns, rf=0.02):
    if len(returns) < 2: return None
    avg_ret = sum(returns) / len(returns) * 252
    std = ((sum((r - avg_ret/252)**2 for r in returns)) ** 0.5) * (252 ** 0.5)
    if std == 0: return None
    return (avg_ret - rf) / std

# ==================== DATA FETCHING ====================

def fetch_technical_data(symbol):
    """Fetch from Yahoo Finance"""
    cached = load_cache(symbol, hours=1)
    if cached and 'technical' in cached:
        print(f"Using cached technical data for {symbol}")
        return cached['technical']
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())
    
    if 'result' not in data['chart'] or not data['chart']['result']:
        raise ValueError(f"No data for {symbol}")
    
    result = data['chart']['result'][0]
    meta = result['meta']
    closes = [c for c in result['indicators']['quote'][0]['close'] if c]
    volumes = [v for v in result['indicators']['quote'][0]['volume'] if v]
    
    returns = daily_returns(closes)
    
    tech = {
        'symbol': meta.get('symbol', symbol),
        'currency': meta.get('currency', 'USD'),
        'current_price': meta.get('regularMarketPrice', closes[-1]),
        '52w_high': meta.get('fiftyTwoWeekHigh'),
        '52w_low': meta.get('fiftyTwoWeekLow'),
        'closes': closes,
        'volumes': volumes,
        'ma5': moving_average(closes, 5),
        'ma20': moving_average(closes, 20),
        'ma60': moving_average(closes, 60) if len(closes) >= 60 else None,
        'rsi14': rsi(closes, 14),
        'macd': macd(closes)[0],
        'macd_signal': macd(closes)[1],
        'bb_upper': bollinger_bands(closes)[0],
        'bb_middle': bollinger_bands(closes)[1],
        'bb_lower': bollinger_bands(closes)[2],
        'volatility': volatility(returns),
        'max_drawdown': max_drawdown(closes),
        'sharpe': sharpe_ratio(returns),
        'avg_volume': sum(volumes[-15:]) / 15 if len(volumes) >= 15 else sum(volumes) / len(volumes),
    }
    
    result = {'technical': tech}
    save_cache(symbol, result)
    return tech

def fetch_fundamental_data_hk(symbol):
    """Fetch fundamental data for HK stocks from Yahoo Finance"""
    try:
        info_url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=defaultKeyStatistics,financialData"
        req = urllib.request.Request(info_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        
        summary = data.get('quoteSummary', {}).get('result', [{}])[0]
        
        fd = summary.get('financialData', {})
        kvs = summary.get('defaultKeyStatistics', {})
        
        return {
            'pe_ratio': kvs.get('trailingPE', {}).get('raw'),
            'forward_pe': kvs.get('forwardPE', {}).get('raw'),
            'market_cap': kvs.get('marketCap', {}).get('raw'),
            'dividend_yield': kvs.get('dividendYield', {}).get('raw'),
            'profit_margin': fd.get('profitMargins', {}).get('raw'),
            'revenue_growth': fd.get('revenueGrowth', {}).get('raw'),
            'ebitda': fd.get('ebitda', {}).get('raw'),
            'debt_to_equity': fd.get('debtToEquity', {}).get('raw'),
            'roe': fd.get('returnOnEquity', {}).get('raw'),
            'beta': kvs.get('beta', {}).get('raw'),
        }
    except Exception as e:
        print(f"Fundamental data fetch error: {e}")
        return {}

def fetch_fundamental_data_us(symbol):
    """Fetch fundamental data for US stocks"""
    try:
        info_url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=defaultKeyStatistics,financialData"
        req = urllib.request.Request(info_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        
        summary = data.get('quoteSummary', {}).get('result', [{}])[0]
        fd = summary.get('financialData', {})
        kvs = summary.get('defaultKeyStatistics', {})
        
        return {
            'pe_ratio': kvs.get('trailingPE', {}).get('raw'),
            'forward_pe': kvs.get('forwardPE', {}).get('raw'),
            'market_cap': kvs.get('marketCap', {}).get('raw'),
            'peg_ratio': kvs.get('pegRatio', {}).get('raw'),
            'profit_margin': fd.get('profitMargins', {}).get('raw'),
            'revenue_growth': fd.get('revenueGrowth', {}).get('raw'),
            'earnings_growth': fd.get('earningsGrowth', {}).get('raw'),
            'beta': kvs.get('beta', {}).get('raw'),
        }
    except Exception as e:
        print(f"Fundamental data fetch error: {e}")
        return {}

def fetch_news_sentiment(symbol, market='US'):
    """Fetch recent news and sentiment (simplified)"""
    # Note: Full news sentiment requires paid APIs
    # This provides a framework for news summary
    
    if market == 'HK':
        search_term = symbol.replace('.HK', '')
    else:
        search_term = symbol
    
    news_data = {
        'recent_news': [],
        'analyst_ratings': None,
        'institutional_holdings': None,
    }
    
    return news_data

def get_macro_overview(market='US'):
    """Get macro environment overview"""
    macro = {
        'US': {
            'interest_rate': '5.25-5.50% (Fed)',
            'inflation': '~3.2%',
            'gdp_growth': '~2.5%',
            'usd_index': '~103-105',
            'notes': 'Fed维持高利率，密切关注通胀走势'
        },
        'HK': {
            'interest_rate': '5.75% (与美挂钩)',
            'hkd_usd': '7.80-7.85',
            'china_gdp': '~5%',
            'notes': '受美联储政策影响，资金流向关注北向资金'
        },
        'CN': {
            'lpr_rate': '3.45%',
            'inflation': '~0.5%',
            'gdp_target': '5%',
            'notes': '货币政策宽松，关注稳增长政策'
        }
    }
    return macro.get(market, macro['US'])

def load_fundamental_estimate(symbol):
    """Load fundamental estimate from stock_fundamental.py cache"""
    cache_path = f"{CACHE_DIR}/{symbol.replace('.', '_')}_full.json"
    try:
        with open(cache_path) as f:
            data = json.load(f)
            return data
    except:
        return None

def estimate_fundamentals_v2(symbol):
    """
    Estimate fundamental metrics from price data
    Fallback when API is unavailable
    """
    import math
    
    # Get price data directly
    price_data = fetch_technical_data(symbol)
    current_price = price_data.get('current_price', 0)
    closes = price_data.get('closes', [])
    
    if not closes:
        return None
    
    # Sector estimates
    sector_estimates = {
        'NVDA': {'sector': 'Semiconductors', 'avg_pe': 35, 'growth_rate': 0.40},
        'AAPL': {'sector': 'Technology', 'avg_pe': 28, 'growth_rate': 0.08},
        'MSFT': {'sector': 'Software', 'avg_pe': 35, 'growth_rate': 0.12},
        'GOOGL': {'sector': 'Internet', 'avg_pe': 25, 'growth_rate': 0.15},
        'AMZN': {'sector': 'E-commerce', 'avg_pe': 60, 'growth_rate': 0.20},
        'TSLA': {'sector': 'EV/Auto', 'avg_pe': 50, 'growth_rate': 0.25},
        '0700.HK': {'sector': 'Internet/Tech', 'avg_pe': 18, 'growth_rate': 0.10},
        '9988.HK': {'sector': 'E-commerce', 'avg_pe': 20, 'growth_rate': 0.08},
        '600519.SH': {'sector': 'Consumer', 'avg_pe': 35, 'growth_rate': 0.15},
    }
    
    base_symbol = symbol.split('.')[0]
    sector_info = sector_estimates.get(symbol) or sector_estimates.get(base_symbol) or {
        'sector': 'Unknown', 'avg_pe': 25, 'growth_rate': 0.10
    }
    
    estimated_pe = sector_info['avg_pe']
    estimated_eps = current_price / estimated_pe if current_price else 0
    peg = estimated_pe / (sector_info['growth_rate'] * 100) if sector_info['growth_rate'] else 0
    
    monthly_return = (closes[-1] - closes[0]) / closes[0] if closes[0] else 0
    recent_closes = closes[-30:] if len(closes) >= 30 else closes
    vol_high = max(recent_closes) if recent_closes else current_price
    vol_low = min(recent_closes) if recent_closes else current_price
    
    return {
        'sector': sector_info['sector'],
        'estimated_pe': estimated_pe,
        'estimated_eps': round(estimated_eps, 2),
        'peg_ratio': round(peg, 2),
        'growth_rate': sector_info['growth_rate'],
        'monthly_return': round(monthly_return * 100, 1),
        'vs_30d_high': round((current_price - vol_high) / vol_high * 100, 1),
        'vs_30d_low': round((current_price - vol_low) / vol_low * 100, 1),
    }

# ==================== COMPREHENSIVE ANALYSIS ====================

def comprehensive_analysis(symbol, market='US'):
    """Main comprehensive analysis function"""
    
    print(f"\n{'='*70}")
    print(f"        📊 {symbol} Comprehensive Stock Analysis")
    print(f"{'='*70}")
    
    # 1. Technical Analysis
    print("\n🔧 Fetching technical data...")
    tech = fetch_technical_data(symbol)
    
    # 2. Fundamental Analysis
    print("📈 Fetching fundamental data...")
    fund = estimate_fundamentals_v2(symbol)
    
    # 3. News & Sentiment
    print("📰 Fetching news...")
    news = fetch_news_sentiment(symbol, market)
    
    # 4. Macro Environment
    print("🌍 Analyzing macro environment...")
    macro = get_macro_overview(market)
    
    # ==================== OUTPUT REPORT ====================
    
    print(f"\n{'='*70}")
    print(f"              📊 {symbol} 综合分析报告")
    print(f"              生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}")
    
    # --- Technical Section ---
    print(f"\n{'─'*70}")
    print("📈 一、技术分析 (Technical Analysis)")
    print(f"{'─'*70}")
    print(f"  当前价格: {tech['currency']}${tech['current_price']:.2f}")
    print(f"  52周区间: {tech['currency']}${tech['52w_low']:.2f} - {tech['currency']}${tech['52w_high']:.2f}")
    print(f"\n  均线系统:")
    print(f"    MA(5):  {tech['currency']}${tech['ma5']:.2f} ({'above' if tech['current_price'] > tech['ma5'] else 'below'})")
    print(f"    MA(20): {tech['currency']}${tech['ma20']:.2f} ({'above' if tech['current_price'] > tech['ma20'] else 'below'})")
    if tech['ma60']:
        print(f"    MA(60): {tech['currency']}${tech['ma60']:.2f} ({'above' if tech['current_price'] > tech['ma60'] else 'below'})")
    
    print(f"\n  动量指标:")
    rsi = tech['rsi14']
    rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "中性"
    print(f"    RSI(14): {rsi:.1f} ({rsi_status})")
    
    macd = tech['macd']
    if macd is not None:
        macd_status = "金叉" if macd > 0 else "死叉"
        print(f"    MACD: {macd:.3f} ({macd_status})")
    else:
        print(f"    MACD: N/A")
    
    print(f"\n  布林带:")
    print(f"    上轨: {tech['currency']}${tech['bb_upper']:.2f}")
    print(f"    中轨: {tech['currency']}${tech['bb_middle']:.2f}")
    print(f"    下轨: {tech['currency']}${tech['bb_lower']:.2f}")
    bb_pos = "above" if tech['current_price'] > tech['bb_upper'] else "below" if tech['current_price'] < tech['bb_lower'] else "middle"
    print(f"    位置: {bb_pos} band")
    
    print(f"\n  风险指标:")
    print(f"    年化波动率: {tech['volatility']:.2f}%")
    print(f"    最大回撤: {tech['max_drawdown']:.2f}%")
    print(f"    夏普比率: {tech['sharpe']:.2f}")
    print(f"    平均成交量: {tech['avg_volume']/1e6:.1f}M")
    
    # --- Fundamental Section ---
    print(f"\n{'─'*70}")
    print("💼 二、基本面分析 (Fundamental Analysis)")
    print(f"{'─'*70}")
    
    if fund and 'estimated_pe' in fund:
        print(f"  板块: {fund['sector']}")
        print(f"\n  估值指标:")
        print(f"    估算PE (TTM): {fund['estimated_pe']:.1f}")
        print(f"    估算EPS: ${fund['estimated_eps']:.2f}")
        print(f"    PEG比率: {fund['peg_ratio']:.2f}")
        print(f"\n  增长指标:")
        print(f"    估算增长率: {fund['growth_rate']*100:.0f}%")
        print(f"\n  相对表现:")
        print(f"    月收益率: {fund['monthly_return']:+.1f}%")
        print(f"    距30日高点: {fund['vs_30d_high']:.1f}%")
        print(f"    距30日低点: {fund['vs_30d_low']:+.1f}%")
        print(f"\n  ⚠️  免责声明: 以上为基于板块估算的基本面数据")
        print(f"     准确数据需使用付费API")
    elif fund:
        # Fallback to Yahoo Finance data if available
        pe = fund.get('pe_ratio')
        print(f"  估值:")
        print(f"    PE(TTM): {pe:.2f}" if pe else "    PE(TTM): N/A")
        fwd_pe = fund.get('forward_pe')
        print(f"    PE(Forward): {fwd_pe:.2f}" if fwd_pe else "    PE(Forward): N/A")
        
        growth = fund.get('revenue_growth')
        print(f"  成长性:")
        print(f"    营收增长: {growth*100:.1f}%" if growth else "    营收增长: N/A")
        eg = fund.get('earnings_growth')
        print(f"    盈利增长: {eg*100:.1f}%" if eg else "    盈利增长: N/A")
        
        margins = fund.get('profit_margin')
        print(f"  盈利能力:")
        print(f"    净利润率: {margins*100:.1f}%" if margins else "    净利润率: N/A")
        roe = fund.get('roe')
        print(f"    ROE: {roe*100:.1f}%" if roe else "    ROE: N/A")
        
        beta = fund.get('beta')
        print(f"  风险特征:")
        print(f"    Beta: {beta:.2f}" if beta else "    Beta: N/A")
    else:
        print("  (基本面数据获取失败)")
    
    # --- Capital Flow Section ---
    print(f"\n{'─'*70}")
    print("💰 三、资金面分析 (Capital Flow)")
    print(f"{'─'*70}")
    print(f"  ⚠️  Note: 详细资金流向需要专业数据源")
    print(f"\n  成交量趋势 (近15日):")
    volumes = tech['volumes'][-15:]
    avg_vol = sum(volumes) / len(volumes)
    recent_vol = volumes[-1] if volumes else avg_vol
    vol_trend = "放量" if recent_vol > avg_vol * 1.2 else "缩量" if recent_vol < avg_vol * 0.8 else "正常"
    print(f"    平均成交量: {avg_vol/1e6:.1f}M")
    print(f"    近5日均量: {sum(volumes[-5:])/5/1e6:.1f}M")
    print(f"    成交量趋势: {vol_trend}")
    
    # --- Macro Section ---
    print(f"\n{'─'*70}")
    print("🌍 四、宏观环境分析 (Macro Environment)")
    print(f"{'─'*70}")
    print(f"  市场: {market}")
    print(f"  利率环境: {macro['interest_rate']}")
    print(f"  通胀/经济: {macro.get('inflation', 'N/A')}")
    print(f"  GDP: {macro.get('gdp_growth', macro.get('china_gdp', 'N/A'))}")
    print(f"  备注: {macro['notes']}")
    
    # --- Summary & Recommendation ---
    print(f"\n{'─'*70}")
    print("🎯 五、综合结论与建议")
    print(f"{'─'*70}")
    
    # Technical Summary
    tech_score = 0
    if tech['current_price'] > tech['ma20']: tech_score += 1
    if tech['ma5'] > tech['ma20']: tech_score += 1
    if 40 < rsi < 60: tech_score += 1
    if rsi < 30: tech_score += 1  # Oversold is good for long
    macd_val = tech['macd']
    macd_status = "N/A" if macd_val is None else ("金叉" if macd_val > 0 else "死叉")
    if macd_val is not None and macd_val > 0: tech_score += 1
    if tech['sharpe'] > 0: tech_score += 1
    
    tech_signal = "看多" if tech_score >= 4 else "中性" if tech_score >= 2 else "看空"
    print(f"  技术面信号: {tech_signal} (评分: {tech_score}/6)")
    print(f"    - 价格{'高于' if tech['current_price'] > tech['ma20'] else '低于'}MA20")
    print(f"    - RSI {rsi_status}")
    print(f"    - MACD {macd_status}")
    
    print(f"\n  风险收益评估:")
    print(f"    波动率: {'高' if tech['volatility'] > 30 else '中' if tech['volatility'] > 15 else '低'} ({tech['volatility']:.1f}%)")
    print(f"    最大回撤: {'高' if tech['max_drawdown'] > 20 else '中' if tech['max_drawdown'] > 10 else '低'} ({tech['max_drawdown']:.1f}%)")
    
    print(f"\n  {'='*70}")
    print(f"  ⚠️ 免责声明: 此分析仅供参考，不构成投资建议")
    print(f"  {'='*70}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python stock_analysis.py <SYMBOL> [--market HK|US|CN]")
        print("Examples:")
        print("  python stock_analysis.py NVDA --market US")
        print("  python stock_analysis.py 0700.HK --market HK")
        print("  python stock_analysis.py 600519.SH --market CN")
        sys.exit(1)
    
    symbol = sys.argv[1]
    market = 'US'
    
    if '--market' in sys.argv:
        idx = sys.argv.index('--market')
        if idx + 1 < len(sys.argv):
            market = sys.argv[idx + 1]
    
    try:
        comprehensive_analysis(symbol, market)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

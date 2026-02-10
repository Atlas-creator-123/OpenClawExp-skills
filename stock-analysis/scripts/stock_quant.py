#!/usr/bin/env python3
"""
Quantitative Stock Analysis - Technical indicators and quantitative metrics.
Usage: python stock_quant.py <SYMBOL>
Example: python stock_quant.py NVDA
"""

import sys
import os
import json
import math
from datetime import datetime

CACHE_DIR = os.path.expanduser("~/.cache/stock_data")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(symbol):
    return os.path.join(CACHE_DIR, f"{symbol.replace('.', '_')}.json")

def load_cache(symbol):
    cache_path = get_cache_path(symbol)
    if os.path.exists(cache_path):
        file_age = os.path.getmtime(cache_path)
        age_hours = (datetime.now().timestamp() - file_age) / 3600
        if age_hours < 1:
            with open(cache_path) as f:
                return json.load(f)
    return None

def fetch_stock_data(symbol):
    cached = load_cache(symbol)
    if cached:
        return cached
    
    import urllib.request
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())
    
    if 'result' not in data['chart'] or not data['chart']['result']:
        raise ValueError(f"No data for: {symbol}")
    
    result = data['chart']['result'][0]
    meta = result['meta']
    timestamps = result['timestamp']
    quotes = result['indicators']['quote'][0]
    
    processed = {
        'symbol': meta.get('symbol', symbol),
        'currency': meta.get('currency', 'USD'),
        'current_price': meta.get('regularMarketPrice', quotes['close'][-1]),
        '52w_high': meta.get('fiftyTwoWeekHigh'),
        '52w_low': meta.get('fiftyTwoWeekLow'),
        'timestamps': timestamps,
        'closes': quotes['close'],
        'volumes': quotes['volume'],
        'last_updated': datetime.now().isoformat()
    }
    
    cache_path = get_cache_path(symbol)
    with open(cache_path, 'w') as f:
        json.dump(processed, f, indent=2)
    
    return processed

def moving_average(data, period):
    """Simple Moving Average"""
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

def exponential_moving_average(data, period):
    """Exponential Moving Average"""
    if len(data) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = data[-period]
    for price in data[-period:]:
        ema = price * multiplier + ema * (1 - multiplier)
    return ema

def rsi(prices, period=14):
    """Relative Strength Index"""
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val

def macd(prices, fast=12, slow=26, signal=9):
    """MACD - Moving Average Convergence Divergence"""
    ema_fast = exponential_moving_average(prices, fast)
    ema_slow = exponential_moving_average(prices, slow)
    
    if ema_fast is None or ema_slow is None:
        return None, None, None
    
    macd_line = ema_fast - ema_slow
    signal_line = exponential_moving_average(prices[-slow:], signal)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def bollinger_bands(prices, period=20, std_dev=2):
    """Bollinger Bands"""
    if len(prices) < period:
        return None, None, None
    
    sma = moving_average(prices, period)
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std = math.sqrt(variance)
    
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    
    return upper, sma, lower

def volatility(returns):
    """Annualized Volatility"""
    if len(returns) < 2:
        return None
    
    daily_vol = math.sqrt(sum((r - sum(returns)/len(returns))**2 for r in returns) / (len(returns) - 1))
    annualized = daily_vol * math.sqrt(252)  # Trading days per year
    return annualized * 100  # Convert to percentage

def max_drawdown(prices):
    """Maximum Drawdown"""
    max_price = max(prices)
    max_dd = 0
    
    for price in prices:
        dd = (max_price - price) / max_price
        if dd > max_dd:
            max_dd = dd
    
    return max_dd * 100

def daily_returns(closes):
    """Calculate daily returns"""
    returns = []
    for i in range(1, len(closes)):
        ret = (closes[i] - closes[i-1]) / closes[i-1]
        returns.append(ret)
    return returns

def sharpe_ratio(returns, risk_free_rate=0.02):
    """Sharpe Ratio (annualized)"""
    if len(returns) < 2:
        return None
    
    avg_return = sum(returns) / len(returns) * 252  # Annualized
    std = math.sqrt(sum((r - avg_return/252)**2 for r in returns)) * math.sqrt(252)
    
    if std == 0:
        return None
    
    sharpe = (avg_return - risk_free_rate) / std
    return sharpe

def quant_analysis(symbol):
    """Main quantitative analysis"""
    data = fetch_stock_data(symbol)
    closes = [c for c in data['closes'] if c]
    volumes = [v for v in data['volumes'] if v]
    
    current_price = data['current_price']
    prev_close = closes[-1] if len(closes) > 1 else current_price
    
    returns = daily_returns(closes)
    daily_vol = volatility(returns) if returns else None
    mdd = max_drawdown(closes)
    sharpe = sharpe_ratio(returns)
    
    # Technical indicators
    ma5 = moving_average(closes, 5)
    ma10 = moving_average(closes, 10)
    ma20 = moving_average(closes, 20)
    ema12, ema26, _ = macd(closes)
    rsi14 = rsi(closes, 14)
    bb_upper, bb_middle, bb_lower = bollinger_bands(closes)
    
    # Position indicators
    price_vs_ma5 = ((current_price - ma5) / ma5 * 100) if ma5 else None
    price_vs_ma20 = ((current_price - ma20) / ma20 * 100) if ma20 else None
    
    print(f"\n{'='*70}")
    print(f"              📊 {symbol} Quantitative Analysis")
    print(f"{'='*70}")
    
    print(f"\n💰 PRICE & TREND")
    print(f"   Current: {data['currency']}${current_price:.2f}")
    print(f"   MA(5):  {data['currency']}${ma5:.2f} ({price_vs_ma5:+.1f}%)" if ma5 else "   MA(5):  N/A")
    print(f"   MA(20): {data['currency']}${ma20:.2f} ({price_vs_ma20:+.1f}%)" if ma20 else "   MA(20): N/A")
    
    print(f"\n📈 MOMENTUM INDICATORS")
    print(f"   RSI(14): {rsi14:.1f}" if rsi14 else "   RSI(14): N/A")
    print(f"   MACD: {ema12 - ema26:.2f}" if ema12 and ema26 else "   MACD: N/A")
    
    print(f"\n📐 VOLATILITY")
    print(f"   Daily Volatility: {daily_vol:.2f}%" if daily_vol else "   Daily Volatility: N/A")
    print(f"   Max Drawdown: {mdd:.2f}%")
    
    print(f"\n⚖️ RISK-ADJUSTED")
    print(f"   Sharpe Ratio: {sharpe:.2f}" if sharpe else "   Sharpe Ratio: N/A")
    
    print(f"\n📊 BOLLINGER BANDS")
    if bb_upper and bb_middle and bb_lower:
        position = "Upper" if current_price > bb_upper else "Lower" if current_price < bb_lower else "Middle"
        print(f"   Upper: {data['currency']}${bb_upper:.2f}")
        print(f"   Middle: {data['currency']}${bb_middle:.2f}")
        print(f"   Lower: {data['currency']}${bb_lower:.2f}")
        print(f"   Current Position: {position} Band")
    
    print(f"\n{'='*70}")
    
    # Simple recommendation
    print("\n🎯 SUMMARY:")
    if rsi14:
        if rsi14 > 70:
            print("   ⚠️ RSI indicates OVERBOUGHT (70+)")
        elif rsi14 < 30:
            print("   ⚠️ RSI indicates OVERSOLD (30-)")
        else:
            print("   ✅ RSI in neutral range (30-70)")
    
    if sharpe and sharpe > 1:
        print("   ✅ Good risk-adjusted returns (Sharpe > 1)")
    elif sharpe and sharpe < 0:
        print("   ⚠️ Poor risk-adjusted returns (Sharpe < 0)")
    
    if mdd > 20:
        print(f"   ⚠️ High max drawdown ({mdd:.1f}%)")
    else:
        print(f"   ✅ Reasonable max drawdown ({mdd:.1f}%)")
    
    print(f"\n{'='*70}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python stock_quant.py <SYMBOL>")
        print("Example: python stock_quant.py NVDA")
        print("\nFeatures:")
        print("  - Moving Averages (MA5, MA10, MA20)")
        print("  - RSI (Relative Strength Index)")
        print("  - MACD (Moving Average Convergence Divergence)")
        print("  - Bollinger Bands")
        print("  - Volatility & Max Drawdown")
        print("  - Sharpe Ratio")
        sys.exit(1)
    
    symbol = sys.argv[1]
    
    try:
        quant_analysis(symbol)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

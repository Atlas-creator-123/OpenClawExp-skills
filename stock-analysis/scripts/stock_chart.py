#!/usr/bin/env python3
"""
Stock Chart Generator - Fetches data from Yahoo Finance, caches locally, and generates SVG chart.
Usage: python stock_chart.py <SYMBOL>
Example: python stock_chart.py 0700.HK
"""

import sys
import os
import json
import pygal
from datetime import datetime

CACHE_DIR = os.path.expanduser("~/.cache/stock_data")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(symbol):
    return os.path.join(CACHE_DIR, f"{symbol.replace('.', '_')}.json")

def load_cache(symbol):
    """Load cached data if exists and recent (< 1 hour)"""
    cache_path = get_cache_path(symbol)
    if os.path.exists(cache_path):
        file_age = os.path.getmtime(cache_path)
        age_hours = (datetime.now().timestamp() - file_age) / 3600
        if age_hours < 1:
            with open(cache_path) as f:
                return json.load(f)
    return None

def save_cache(symbol, data):
    """Save data to cache"""
    cache_path = get_cache_path(symbol)
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)

def fetch_stock_data(symbol):
    """Fetch stock data from Yahoo Finance API"""
    # Check cache first
    cached = load_cache(symbol)
    if cached:
        print(f"Using cached data for {symbol}")
        return cached
    
    import urllib.request
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0'
    })
    
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())
        
    if 'result' not in data['chart'] or not data['chart']['result']:
        raise ValueError(f"No data for symbol: {symbol}")
    
    result = data['chart']['result'][0]
    meta = result['meta']
    timestamps = result['timestamp']
    quotes = result['indicators']['quote'][0]
    
    processed_data = {
        'symbol': meta.get('symbol', symbol),
        'currency': meta.get('currency', 'USD'),
        'current_price': meta.get('regularMarketPrice', quotes['close'][-1]),
        '52w_high': meta.get('fiftyTwoWeekHigh'),
        '52w_low': meta.get('fiftyTwoWeekLow'),
        'timestamps': timestamps,
        'opens': quotes['open'],
        'closes': quotes['close'],
        'highs': quotes['high'],
        'lows': quotes['low'],
        'volumes': quotes['volume'],
        'last_updated': datetime.now().isoformat()
    }
    
    # Save to cache
    save_cache(symbol, processed_data)
    print(f"Fetched and cached data for {symbol}")
    
    return processed_data

def generate_chart(data, output_path):
    """Generate SVG line chart with price and volume using pygal"""
    dates = [datetime.fromtimestamp(ts).strftime('%-m/%-d') for ts in data['timestamps']]
    closes = data['closes']
    volumes = data['volumes']
    highs = data['highs']
    lows = data['lows']
    
    # Monthly high/low
    max_price = max(closes)
    max_idx = closes.index(max_price)
    min_price = min([c for c in closes if c])
    min_idx = closes.index(min_price)
    
    # Create combined chart
    chart = pygal.Line(
        x_label_rotation=45,
        height=500,
        width=1000,
        explicit_size=True,
        show_legend=True,
        margin=40
    )
    chart.title = f"{data['symbol']} - 1 Month Price & Volume Chart"
    chart.x_labels = dates
    
    # Add price line
    chart.add('Close', closes)
    
    # Add volume as percentage of max
    max_vol = max(volumes) if volumes else 1
    vol_display = [round(v / max_vol * 100, 1) for v in volumes]
    chart.add('Volume (%)', vol_display)
    
    # Add 52-week reference lines
    if data['52w_high']:
        chart.add(f'52W High: ${data["52w_high"]:.0f}', [data['52w_high']] * len(dates))
    if data['52w_low']:
        chart.add(f'52W Low: ${data["52w_low"]:.0f}', [data['52w_low']] * len(dates))
    
    # Mark monthly high point
    high_point = [None] * len(closes)
    high_point[max_idx] = max_price
    chart.add(f'📈 Month High: ${max_price:.2f}', high_point)
    
    # Mark monthly low point
    low_point = [None] * len(closes)
    low_point[min_idx] = min_price
    chart.add(f'📉 Month Low: ${min_price:.2f}', low_point)
    
    chart.render_to_file(output_path)
    return output_path

def print_metrics(data):
    """Print key metrics and analysis"""
    closes = data['closes']
    volumes = data['volumes']
    dates = [datetime.fromtimestamp(ts).strftime('%-m/%-d') for ts in data['timestamps']]
    
    current_price = data['current_price']
    prev_close = closes[-2] if len(closes) > 1 else data['opens'][-1]
    change = current_price - prev_close
    pct_change = (change / prev_close) * 100
    
    monthly_high = max(closes)
    monthly_low = min([c for c in closes if c])
    monthly_high_idx = closes.index(monthly_high)
    monthly_low_idx = closes.index(monthly_low)
    
    avg_volume = sum(volumes) / len(volumes)
    max_vol = max(volumes)
    
    # Monthly change
    first_close = closes[0]
    monthly_change = current_price - first_close
    monthly_pct = (monthly_change / first_close) * 100
    
    print(f"\n{'='*65}")
    print(f"              {data['symbol']} Stock Analysis")
    print(f"{'='*65}")
    print(f"💰 Current Price: {data['currency']}${current_price:.2f}")
    print(f"📈 Today's Change: {change:+.2f} ({pct_change:+.2f}%)")
    print(f"📊 52-Week Range: {data['currency']}${data['52w_low']:.2f} - {data['currency']}${data['52w_high']:.2f}")
    print(f"{'-'*65}")
    print(f"Monthly Performance:")
    print(f"  • Monthly Change: {monthly_change:+.2f} ({monthly_pct:+.2f}%)")
    print(f"  • Monthly High: {data['currency']}${monthly_high:.2f} ({dates[monthly_high_idx]})")
    print(f"  • Monthly Low: {data['currency']}${monthly_low:.2f} ({dates[monthly_low_idx]})")
    print(f"  • Average Volume: {avg_volume/1e6:.1f}M")
    print(f"  • Max Volume: {max_vol/1e6:.1f}M")
    print(f"{'='*65}\n")
    print(f"✅ Chart saved: /tmp/{data['symbol'].replace('.', '_')}_chart.svg")
    print(f"📁 Cache: {get_cache_path(data['symbol'])}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python stock_chart.py <SYMBOL>")
        print("Example: python stock_chart.py 0700.HK")
        print("\nFeatures:")
        print("  - Fetches from Yahoo Finance API")
        print("  - Caches data locally (~/.cache/stock_data)")
        print("  - Generates SVG chart with price & volume")
        print("  - Marks monthly high/low points")
        print("  - Shows 52-week range reference")
        sys.exit(1)
    
    symbol = sys.argv[1]
    
    try:
        data = fetch_stock_data(symbol)
        output_path = f"/tmp/{symbol.replace('.', '_')}_chart.svg"
        generate_chart(data, output_path)
        print_metrics(data)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

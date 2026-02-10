#!/usr/bin/env python3
"""
Stock Fundamental Estimator - Estimates fundamental metrics from price data.
Uses price-based estimation when API is unavailable.
"""

import sys
import json
from datetime import datetime, timedelta
import urllib.request

CACHE_DIR = "/Users/Spike/.cache/stock_data"

def load_price_data(symbol):
    """Load cached price data"""
    cache_path = f"{CACHE_DIR}/{symbol.replace('.', '_')}.json"
    try:
        with open(cache_path) as f:
            data = json.load(f)
        return data
    except:
        return None

def estimate_fundamentals(symbol, market='US'):
    """
    Estimate fundamental metrics from available data
    Note: These are ESTIMATES only - real data requires paid API
    """
    
    data = load_price_data(symbol)
    
    if not data:
        return {'error': 'No price data available. Run stock_chart.py first.'}
    
    current_price = data.get('current_price', 0)
    closes = data.get('closes', [])
    
    if not closes:
        return {'error': 'No price history available'}
    
    # Basic calculations from price data
    recent_closes = closes[-30:] if len(closes) >= 30 else closes
    
    # Estimate returns
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
    monthly_return = (closes[-1] - closes[0]) / closes[0] if closes[0] else 0
    volatility = (max(recent_closes) - min(recent_closes)) / min(recent_closes) * 100 if recent_closes else 0
    
    # Trend estimation
    short_trend = "up" if len(closes) >= 5 and closes[-1] > closes[-5] else "down"
    medium_trend = "up" if len(closes) >= 20 and closes[-1] > closes[-20] else "down"
    
    # Estimate PE based on sector averages (rough estimates)
    # These are SECTOR averages, not company specific
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
    
    # Get symbol base (remove .HK, .SH, etc)
    base_symbol = symbol.split('.')[0] if '.' in symbol else symbol
    
    # Try exact match first, then sector defaults
    sector_info = sector_estimates.get(symbol) or sector_estimates.get(base_symbol) or {
        'sector': 'Unknown', 'avg_pe': 25, 'growth_rate': 0.10
    }
    
    # Calculate estimated EPS (very rough)
    # Assuming typical PE for sector
    estimated_pe = sector_info['avg_pe']
    estimated_eps = current_price / estimated_pe if current_price else 0
    
    # Estimate PEG ratio (PE / Growth Rate)
    peg = estimated_pe / (sector_info['growth_rate'] * 100) if sector_info['growth_rate'] else 0
    
    fund = {
        'symbol': symbol,
        'sector': sector_info['sector'],
        'last_updated': datetime.now().isoformat(),
        'note': '⚠️ 估算值 - 需要付费API获取准确数据',
        
        'price_data': {
            'current_price': current_price,
            'monthly_return': f"{monthly_return*100:+.1f}%",
            'monthly_volatility': f"{volatility:.1f}%",
        },
        
        'estimates': {
            'estimated_pe': f"{estimated_pe:.1f}",
            'estimated_eps': f"${estimated_eps:.2f}",
            'peg_ratio': f"{peg:.2f}",
            'growth_rate_est': f"{sector_info['growth_rate']*100:.0f}%",
        },
        
        'trend': {
            'short_term': short_trend,
            'medium_term': medium_trend,
        },
        
        'performance_indicators': {
            'vs_30d_high': f"{(current_price - max(recent_closes))/max(recent_closes)*100:.1f}%" if recent_closes else "N/A",
            'vs_30d_low': f"{(current_price - min(recent_closes))/min(recent_closes)*100:+.1f}%" if recent_closes else "N/A",
        },
        
        'data_sources': {
            'price': 'Yahoo Finance (cached)',
            'fundamentals': 'Sector Estimates',
            'api_needed': 'Yahoo Finance API / FMP / Alpha Vantage (paid)'
        }
    }
    
    return fund

def print_fundamental_report(symbol, market='US'):
    """Print formatted fundamental report"""
    
    fund = estimate_fundamentals(symbol, market)
    
    if 'error' in fund:
        print(f"\n❌ Error: {fund['error']}")
        return
    
    print(f"\n{'='*70}")
    print(f"              💼 {symbol} 基本面估算报告")
    print(f"              生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}")
    
    print(f"\n📌 基本信息:")
    print(f"   板块: {fund['sector']}")
    print(f"   ⚠️  免责声明: 以下为估算值，非实际财报数据")
    
    print(f"\n💰 价格数据:")
    pd = fund['price_data']
    print(f"   当前价格: {pd['current_price']}")
    print(f"   月收益率: {pd['monthly_return']}")
    print(f"   月波动率: {pd['monthly_volatility']}")
    
    print(f"\n📊 估值估算:")
    est = fund['estimates']
    print(f"   估算PE (TTM): {est['estimated_pe']}")
    print(f"   估算EPS: {est['estimated_eps']}")
    print(f"   PEG比率: {est['peg_ratio']}")
    print(f"   估算增长率: {est['growth_rate_est']}")
    
    print(f"\n📈 趋势判断:")
    trend = fund['trend']
    short = "↑ 短期看涨" if trend['short_term'] == 'up' else "↓ 短期看跌"
    medium = "↑ 中期看涨" if trend['medium_term'] == 'up' else "↓ 中期看跌"
    print(f"   {short}")
    print(f"   {medium}")
    
    perf = fund['performance_indicators']
    print(f"\n🎯 相对表现:")
    print(f"   距30日高点: {perf['vs_30d_high']}")
    print(f"   距30日低点: {perf['vs_30d_low']}")
    
    print(f"\n{'─'*70}")
    print("💡 说明:")
    print("   - 估值基于板块平均PE，仅供参考")
    print("   - 准确基本面数据需使用付费API:")
    print("     • Yahoo Finance API (企业级)")
    print("     • Financial Modeling Prep (fmp.io)")
    print("     • Alpha Vantage (alphavantage.co)")
    print(f"{'─'*70}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python stock_fundamental.py <SYMBOL>")
        print("Example: python stock_fundamental.py NVDA")
        print("\nFeatures:")
        print("  - Price-based fundamental estimation")
        print("  - Trend analysis")
        print("  - Performance metrics")
        print("  - API recommendations")
        sys.exit(1)
    
    symbol = sys.argv[1]
    market = sys.argv[2] if len(sys.argv) > 2 else 'US'
    
    try:
        print_fundamental_report(symbol, market)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

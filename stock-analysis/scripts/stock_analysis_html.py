#!/usr/bin/env python3
"""
Stock Analysis HTML Report Generator
Generates beautiful, responsive HTML reports for stocks
Supports upload to remote servers (cvm_nj, etc.)
"""

import json
import sys
import os
from datetime import datetime

# HTML templates
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Stock Analysis Report</title>
    <style>
        :root {{
            --primary-color: #1a73e8;
            --text-color: #333;
            --positive: #26a69a;
            --negative: #ef5350;
            --neutral: #ff9800;
            --background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--background);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            color: var(--text-color);
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, #4a90d9 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{ margin: 0; font-size: 2em; }}
        .header .subtitle {{ margin-top: 10px; opacity: 0.9; }}
        .header .meta {{ margin-top: 15px; font-size: 0.9em; background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; display: inline-block; }}
        
        .content {{ padding: 40px; }}
        
        .section {{ margin-bottom: 35px; }}
        
        .section-title {{
            font-size: 1.4em;
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid var(--primary-color);
        }}
        
        .price-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
        }}
        
        .current-price {{ font-size: 3em; font-weight: 700; }}
        .price-change {{ font-size: 1.5em; margin-top: 10px; }}
        .price-change.up {{ background: var(--positive); }}
        .price-change.down {{ background: var(--negative); }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .metric-card .value {{ font-size: 1.8em; font-weight: 700; color: var(--primary-color); }}
        .metric-card .label {{ color: #666; margin-top: 5px; }}
        
        .tech-analysis {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .tech-item {{ background: #f8f9fa; padding: 20px; border-radius: 12px; }}
        
        .signal {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            margin-top: 10px;
        }}
        .signal.bullish {{ background: #e8f5e9; color: var(--positive); }}
        .signal.bearish {{ background: #ffebee; color: var(--negative); }}
        .signal.neutral {{ background: #fff3e0; color: var(--neutral); }}
        
        .discussion {{ background: #f8f9fa; padding: 25px; border-radius: 12px; }}
        
        .bullish-points, .bearish-points {{ margin-bottom: 15px; }}
        
        .point {{
            padding: 8px 15px;
            margin-bottom: 8px;
            border-radius: 8px;
        }}
        .bullish-points .point {{ background: #e8f5e9; }}
        .bearish-points .point {{ background: #ffebee; }}
        
        .assessment-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .assessment {{ background: #f8f9fa; padding: 20px; border-radius: 12px; }}
        
        .score-bar {{
            height: 12px;
            background: #e0e0e0;
            border-radius: 6px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .score-fill {{ height: 100%; border-radius: 6px; }}
        .score-fill.good {{ background: var(--positive); }}
        .score-fill.bad {{ background: var(--negative); }}
        .score-fill.neutral {{ background: var(--neutral); }}
        
        .catalysts-risks {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        
        .catalysts {{ background: #e8f5e9; padding: 20px; border-radius: 12px; border-left: 4px solid var(--positive); }}
        .risks {{ background: #ffebee; padding: 20px; border-radius: 12px; border-left: 4px solid var(--negative); }}
        
        .recommendation {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
        }}
        
        .period {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        
        .position-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: rgba(255,255,255,0.1);
        }}
        
        .position-table th, .position-table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .comparison-table th, .comparison-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .comparison-table th {{ background: #f5f5f5; }}
        
        .personal-view {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 25px;
            border-radius: 12px;
            margin-top: 20px;
        }}
        
        .pros-cons {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .pros {{ background: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 4px solid var(--positive); }}
        .cons {{ background: #ffebee; padding: 15px; border-radius: 10px; border-left: 4px solid var(--negative); }}
        
        .disclaimer {{
            background: #fff3e0;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 0.9em;
            color: #e65100;
            margin-top: 30px;
            border-left: 4px solid var(--neutral);
        }}
        
        .footer {{
            background: #1a1a2e;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.85em;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid, .tech-analysis, .assessment-grid, .catalysts-risks, .pros-cons {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{emoji} {symbol}</h1>
            <div class="subtitle">{name}</div>
            <div class="meta">📊 {source} | {timestamp}</div>
        </div>
        
        <div class="content">
            {sections}
        </div>
        
        <div class="footer">
            <p>🦅 Generated by AirClaw Stock Analysis | {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""

SECTION_PRICE = """
            <div class="section">
                <div class="section-title">💰 实时行情</div>
                <div class="price-card">
                    <div class="current-price">{price}</div>
                    <div class="price-change {change_class}">{change} ({pct}) 📈</div>
                </div>
                <div class="metrics-grid">
                    <div class="metric-card"><div class="value">{open}</div><div class="label">今开</div></div>
                    <div class="metric-card"><div class="value">{high}</div><div class="label">最高</div></div>
                    <div class="metric-card"><div class="value">{low}</div><div class="label">最低</div></div>
                    <div class="metric-card"><div class="value">{volume}</div><div class="label">成交量</div></div>
                    <div class="metric-card"><div class="value">{market_cap}</div><div class="label">市值</div></div>
                    <div class="metric-card"><div class="value">{pe}</div><div class="label">PE</div></div>
                </div>
            </div>
"""

SECTION_METRICS = """
            <div class="section">
                <div class="section-title">📈 基础指标</div>
                <div class="metrics-grid">
                    <div class="metric-card"><div class="value">{pe}</div><div class="label">PE (TTM)</div></div>
                    <div class="metric-card"><div class="value">{pb}</div><div class="label">PB</div></div>
                    <div class="metric-card"><div class="value">{eps}</div><div class="label">每股收益</div></div>
                    <div class="metric-card"><div class="value">{dividend}</div><div class="label">股息率</div></div>
                    <div class="metric-card"><div class="value">{market_cap}</div><div class="label">市值</div></div>
                    <div class="metric-card"><div class="value">{week_52}</div><div class="label">52周区间</div></div>
                </div>
            </div>
"""

SECTION_TECH = """
            <div class="section">
                <div class="section-title">📊 技术分析</div>
                <div class="tech-analysis">
                    <div class="tech-item">
                        <div><strong>📍 52周位置:</strong> {position}</div>
                        <div class="signal {tech_signal1}">{tech_msg1}</div>
                    </div>
                    <div class="tech-item">
                        <div><strong>📈 技术信号:</strong> {tech_msg2}</div>
                        <div class="signal {tech_signal2}">{tech_msg3}</div>
                    </div>
                    <div class="tech-item">
                        <div><strong>💪 支撑位:</strong> {support}</div>
                        <div class="signal neutral">参考</div>
                    </div>
                    <div class="tech-item">
                        <div><strong>🔒 阻力位:</strong> {resistance}</div>
                        <div class="signal neutral">参考</div>
                    </div>
                </div>
            </div>
"""

SECTION_DISCUSSION = """
            <div class="section">
                <div class="section-title">🗣️ 市场讨论热点</div>
                <div class="discussion">
                    <p><strong>🔥 热门话题:</strong> {hot_topics}</p>
                    
                    <div class="bullish-points">
                        <p><strong>🟢 多方观点:</strong></p>
                        {bullish_points}
                    </div>
                    
                    <div class="bearish-points">
                        <p><strong>🔴 空方观点:</strong></p>
                        {bearish_points}
                    </div>
                </div>
            </div>
"""

SECTION_ASSESSMENT = """
            <div class="section">
                <div class="section-title">💡 综合评估</div>
                <div class="assessment-grid">
                    <div class="assessment">
                        <div><strong>技术面</strong></div>
                        <div class="score-bar"><div class="score-fill {tech_class}" style="width: {tech_pct}%;"></div></div>
                        <div>{tech_score}/6 - {tech_msg}</div>
                    </div>
                    <div class="assessment">
                        <div><strong>基本面</strong></div>
                        <div class="score-bar"><div class="score-fill {funda_class}" style="width: {funda_pct}%;"></div></div>
                        <div>{funda_score}/6 - {funda_msg}</div>
                    </div>
                    <div class="assessment">
                        <div><strong>增长潜力</strong></div>
                        <div class="score-bar"><div class="score-fill {growth_class}" style="width: {growth_pct}%;"></div></div>
                        <div>{growth_score}/6 - {growth_msg}</div>
                    </div>
                    <div class="assessment">
                        <div><strong>估值水平</strong></div>
                        <div class="score-bar"><div class="score-fill {value_class}" style="width: {value_pct}%;"></div></div>
                        <div>{value_score}/6 - {value_msg}</div>
                    </div>
                </div>
                
                <div class="catalysts-risks" style="margin-top: 20px;">
                    <div class="catalysts">
                        <h4>🚀 催化剂</h4>
                        <ul>
                            {catalysts}
                        </ul>
                    </div>
                    <div class="risks">
                        <h4>⚠️ 风险</h4>
                        <ul>
                            {risks}
                        </ul>
                    </div>
                </div>
            </div>
"""

SECTION_RECOMMENDATION = """
            <div class="section">
                <div class="section-title">🎯 操作建议</div>
                <div class="recommendation">
                    <h3>📈 投资建议</h3>
                    
                    <div class="period">
                        <div><strong>📉 短周期:</strong> {short_term}</div>
                    </div>
                    
                    <div class="period">
                        <div><strong>📈 中周期:</strong> {medium_term}</div>
                    </div>
                    
                    <div class="period">
                        <div><strong>💎 长周期:</strong> {long_term}</div>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <strong>📊 仓位建议:</strong>
                        <table class="position-table">
                            <tr><th>价位</th><th>行动</th><th>建议</th></tr>
                            {position_table}
                        </table>
                    </div>
                </div>
            </div>
"""

SECTION_PERSONAL = """
            <div class="section">
                <div class="section-title">📝 个人看法</div>
                <div class="personal-view">
                    <h4>💭 核心观点</h4>
                    
                    <div class="pros-cons">
                        <div class="pros">
                            <h5>✅ 看好理由</h5>
                            <ul>
                                {pros}
                            </ul>
                        </div>
                        <div class="cons">
                            <h5>⚠️ 风险提示</h5>
                            <ul>
                                {cons}
                            </ul>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 15px; border-radius: 10px;">
                        <p><strong>🎯 投资策略:</strong> {summary}</p>
                    </div>
                </div>
            </div>
"""

SECTION_DISCLAIMER = """
            <div class="disclaimer">
                ⚠️ <strong>免责声明:</strong> 本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。
            </div>
"""


def generate_html_report(symbol, data, output_path=None):
    """
    Generate HTML report for a stock
    
    Args:
        symbol: Stock symbol (e.g., TSLA, 0700.HK)
        data: Dictionary with stock data
        output_path: Path to save HTML file (optional)
    
    Returns:
        HTML content string
    """
    
    # Build sections
    sections = []
    
    # Price section
    if 'price' in data:
        change_class = 'up' if data.get('change_pct', 0) >= 0 else 'down'
        sections.append(SECTION_PRICE.format(
            price=data.get('price', 'N/A'),
            change=data.get('change', 'N/A'),
            pct=data.get('change_pct', 'N/A'),
            change_class=change_class,
            open=data.get('open', 'N/A'),
            high=data.get('high', 'N/A'),
            low=data.get('low', 'N/A'),
            volume=data.get('volume', 'N/A'),
            market_cap=data.get('market_cap', 'N/A'),
            pe=data.get('pe', 'N/A')
        ))
    
    # Metrics section
    if 'pe' in data:
        sections.append(SECTION_METRICS.format(
            pe=data.get('pe', 'N/A'),
            pb=data.get('pb', 'N/A'),
            eps=data.get('eps', 'N/A'),
            dividend=data.get('dividend', 'N/A'),
            market_cap=data.get('market_cap', 'N/A'),
            week_52=f"{data.get('week_52_low', 'N/A')} - {data.get('week_52_high', 'N/A')}"
        ))
    
    # Technical section
    if 'position_52w' in data:
        pos = data.get('position_52w', 50)
        if pos > 70:
            tech_signal1 = 'bearish'
            tech_msg1 = '接近高点 - 回调风险'
        elif pos < 30:
            tech_signal1 = 'bullish'
            tech_msg1 = '处于低位 - 机会区间'
        else:
            tech_signal1 = 'neutral'
            tech_msg1 = '中位震荡 - 观望'
        
        sections.append(SECTION_TECH.format(
            position=f"{pos:.1f}%",
            tech_signal1=tech_signal1,
            tech_msg1=tech_msg1,
            tech_msg2=data.get('tech_summary', '中性'),
            tech_signal2='neutral',
            tech_msg3=data.get('tech_signal', '观望'),
            support=data.get('support', 'N/A'),
            resistance=data.get('resistance', 'N/A')
        ))
    
    # Discussion section
    if 'bullish' in data or 'bearish' in data:
        bullish_html = ''.join([f'<div class="point">✅ {p}</div>' for p in data.get('bullish', [])[:4]])
        bearish_html = ''.join([f'<div class="point">⚠️ {p}</div>' for p in data.get('bearish', [])[:4]])
        
        sections.append(SECTION_DISCUSSION.format(
            hot_topics=data.get('hot_topics', '市场关注度高'),
            bullish_points=bullish_html,
            bearish_points=bearish_html
        ))
    
    # Assessment section
    if 'scores' in data:
        scores = data.get('scores', {})
        catalysts = data.get('catalysts', [])
        risks = data.get('risks', [])
        
        # Get style classes
        def get_score_class(score):
            if score >= 4:
                return 'good'
            elif score <= 2:
                return 'bad'
            else:
                return 'neutral'
        
        sections.append(SECTION_ASSESSMENT.format(
            tech_class=get_score_class(scores.get('tech', 3)),
            tech_pct=scores.get('tech', 3) * 100 / 6,
            tech_score=scores.get('tech', 3),
            tech_msg=scores.get('tech_msg', '中性'),
            funda_class=get_score_class(scores.get('fundamental', 3)),
            funda_pct=scores.get('fundamental', 3) * 100 / 6,
            funda_score=scores.get('fundamental', 3),
            funda_msg=scores.get('fundamental_msg', '中性'),
            growth_class=get_score_class(scores.get('growth', 3)),
            growth_pct=scores.get('growth', 3) * 100 / 6,
            growth_score=scores.get('growth', 3),
            growth_msg=scores.get('growth_msg', '中性'),
            value_class=get_score_class(scores.get('value', 3)),
            value_pct=scores.get('value', 3) * 100 / 6,
            value_score=scores.get('value', 3),
            value_msg=scores.get('value_msg', '中性'),
            catalysts='<li>'.join(catalysts[:4]) or '<li>业绩增长</li>',
            risks='<li>'.join(risks[:4]) or '<li>市场竞争</li>'
        ))
    
    # Recommendation section
    if 'recommendation' in data:
        rec = data.get('recommendation', {})
        pos_table = data.get('position_table', [])
        
        pos_html = ''
        for p in pos_table:
            pos_html += f'<tr><td>{p.get("price", "")}</td><td>{p.get("action", "")}</td><td>{p.get("reason", "")}</td></tr>'
        
        sections.append(SECTION_RECOMMENDATION.format(
            short_term=rec.get('short_term', '观望为主'),
            medium_term=rec.get('medium_term', '谨慎乐观'),
            long_term=rec.get('long_term', '长期看好'),
            position_table=pos_html
        ))
    
    # Personal view section
    if 'pros' in data or 'cons' in data:
        pros = data.get('pros', [])
        cons = data.get('cons', [])
        
        sections.append(SECTION_PERSONAL.format(
            pros='<li>'.join(pros[:4]) or '<li>基本面良好</li>',
            cons='<li>'.join(cons[:4]) or '<li>估值偏高</li>',
            summary=data.get('summary', '需要根据个人风险偏好决定')
        ))
    
    # Disclaimer
    sections.append(SECTION_DISCLAIMER)
    
    # Generate HTML
    emoji_map = {
        'TSLA': '🚗',
        'BABA': '🏢',
        '0700.HK': '🐧',
        '03690': '🍜',
        '00700': '🐧',
        '600938': '🐉',
        '000333': '🏠',
        'NVDA': '🎮',
        'AAPL': '📱',
        'MSFT': '💻',
        'META': '📘'
    }
    
    html = HTML_TEMPLATE.format(
        title=f"{symbol} - Stock Analysis",
        emoji=emoji_map.get(symbol, '📈'),
        symbol=symbol,
        name=data.get('name', symbol),
        source=data.get('source', 'AirClaw'),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
        sections=''.join(sections)
    )
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ HTML report saved to: {output_path}")
    
    return html


def demo():
    """Generate demo HTML report"""
    demo_data = {
        'symbol': 'TSLA',
        'name': '特斯拉 (Tesla)',
        'price': '$423.87',
        'change': '-$1.34',
        'change_pct': -0.32,
        'open': '$427.95',
        'high': '$436.35',
        'low': '$423.10',
        'volume': '1616万',
        'market_cap': '$1.59万亿',
        'pe': '418.94',
        'pb': '19.35',
        'eps': '$1.01',
        'dividend': 'N/A',
        'week_52_low': '$214.25',
        'week_52_high': '$498.83',
        'position_52w': 68,
        'support': '$400',
        'resistance': '$480',
        'tech_summary': '短线回调',
        'tech_signal': '观望',
        'hot_topics': 'FSD全自动驾驶、人形机器人、光伏业务',
        'bullish': [
            '特斯拉不仅是车企，更是AI/能源公司',
            'FSD落地领先对手',
            '光伏+储能+电动车生态完整',
            '人形机器人行业领先'
        ],
        'bearish': [
            'PE 419倍，严重高估',
            '比亚迪等中国车企崛起',
            '销量增速放缓',
            '马斯克分心太多'
        ],
        'scores': {
            'tech': 4,
            'tech_msg': '短线回调',
            'fundamental': 4,
            'fundamental_msg': '增长放缓',
            'growth': 5,
            'growth_msg': 'AI+能源故事性感',
            'value': 2,
            'value_msg': '极度高估'
        },
        'catalysts': [
            'FSD全自动驾驶突破',
            '人形机器人商业化',
            'Semi卡车量产交付',
            '光伏业务超预期'
        ],
        'risks': [
            '估值泡沫 - 419倍PE',
            '销量不及预期',
            '比亚迪追赶',
            '马斯克风险'
        ],
        'recommendation': {
            'short_term': '🔴 观望 - 当前$424处于区间中部，可能下探$380-400',
            'medium_term': '⚠️ 不确定 - 目标价$350-$500',
            'long_term': '🟡 谨慎 - 本质是"故事股"'
        },
        'position_table': [
            {'price': '$400以下', 'action': '首次建仓', 'reason': '试探性买入'},
            {'price': '$350以下', 'action': '加仓', 'reason': '越跌越买'},
            {'price': '$480以上', 'action': '减仓', 'reason': '获利了结'},
            {'price': '跌破$300', 'action': '清仓', 'reason': '趋势破坏'}
        ],
        'pros': [
            'AI故事性感',
            '马斯克执行力强',
            '品牌力强',
            '生态完整'
        ],
        'cons': [
            '估值离谱',
            '销量瓶颈',
            '利润率下降',
            '马斯克双刃剑'
        ],
        'summary': '适合高风险偏好投资者，最佳买入区间$350以下'
    }
    
    html = generate_html_report('TSLA', demo_data, '/tmp/tesla_demo.html')
    print(f"Generated demo report: /tmp/tesla_demo.html")
    print(f"File size: {len(html)} bytes")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo()
    elif len(sys.argv) > 2:
        # Load JSON data and generate report
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            data = json.load(f)
        generate_html_report(sys.argv[1], data, sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        print("Usage:")
        print("  python stock_analysis_html.py --demo          # Generate demo report")
        print("  python stock_analysis_html.py <SYMBOL> <DATA.json> [OUTPUT.html]")
        print("\nExample:")
        print("  python stock_analysis_html.py TSLA data.json report.html")

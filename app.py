import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import requests

# 配置Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'btc-analysis-platform-2025'

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 环境变量获取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")

# 内存存储（替代数据库）
news_cache = []
analysis_cache = []

class BTCAnalyzer:
    def __init__(self):
        self.last_price_update = 0
        self.cached_price = None

    def get_btc_price(self):
        """获取BTC价格 - 多重备用方案"""
        current_time = time.time()

        # 缓存机制：30秒内返回缓存数据
        if self.cached_price and (current_time - self.last_price_update) < 30:
            return self.cached_price

        # 方案1：OKX API
        try:
            if OKX_API_KEY:
                headers = {
                    'OK-ACCESS-KEY': OKX_API_KEY,
                    'Content-Type': 'application/json'
                }
                response = requests.get(
                    'https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT',
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == '0' and data.get('data'):
                        price_data = data['data'][0]
                        result = {
                            'price': float(price_data['last']),
                            'change_24h': float(price_data['chg']),
                            'volume_24h': float(price_data['volCcy24h']),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'OKX'
                        }
                        self.cached_price = result
                        self.last_price_update = current_time
                        return result
        except Exception as e:
            logger.warning(f"OKX API失败: {e}")

        # 方案2：CoinGecko API（备用）
        try:
            response = requests.get(
                'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                bitcoin_data = data.get('bitcoin', {})
                result = {
                    'price': bitcoin_data.get('usd', 0),
                    'change_24h': bitcoin_data.get('usd_24h_change', 0),
                    'volume_24h': bitcoin_data.get('usd_24h_vol', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'CoinGecko'
                }
                self.cached_price = result
                self.last_price_update = current_time
                return result
        except Exception as e:
            logger.warning(f"CoinGecko API失败: {e}")

        # 方案3：Binance API（最后备用）
        try:
            response = requests.get(
                'https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                result = {
                    'price': float(data['lastPrice']),
                    'change_24h': float(data['priceChangePercent']),
                    'volume_24h': float(data['quoteVolume']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Binance'
                }
                self.cached_price = result
                self.last_price_update = current_time
                return result
        except Exception as e:
            logger.warning(f"Binance API失败: {e}")

        # 如果所有API都失败，返回错误信息
        return {
            'error': '所有价格API暂时不可用',
            'price': 0,
            'change_24h': 0,
            'volume_24h': 0,
            'timestamp': datetime.now().isoformat(),
            'source': 'Error'
        }

    def get_ai_analysis(self, context="当前BTC市场分析"):
        """DeepSeek AI分析"""
        try:
            if not DEEPSEEK_API_KEY:
                return "DeepSeek API密钥未配置"

            # 获取当前价格信息
            price_data = self.get_btc_price()

            prompt = f"""
作为专业的加密货币分析师，请基于以下信息进行BTC市场分析：

当前BTC价格：${price_data.get('price', 'N/A')}
24小时涨跌：{price_data.get('change_24h', 0):.2f}%
数据来源：{price_data.get('source', 'Unknown')}

分析背景：{context}

请提供：
1. 短期价格走势预测（1-3天）
2. 关键技术指标分析
3. 市场情绪评估
4. 投资建议（长线/短线）
5. 风险提示

请保持专业客观，避免过度乐观或悲观。
"""

            headers = {
                'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7
            }

            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']

                # 缓存分析结果
                analysis_cache.append({
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat(),
                    'context': context,
                    'price_at_analysis': price_data.get('price', 0)
                })

                # 保持缓存大小
                if len(analysis_cache) > 10:
                    analysis_cache.pop(0)

                return analysis
            else:
                return f"AI分析服务暂时不可用 (状态码: {response.status_code})"

        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return f"AI分析服务临时不可用: {str(e)}"

# 创建分析器实例
analyzer = BTCAnalyzer()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/price')
def get_price():
    """获取BTC价格API"""
    try:
        price_data = analyzer.get_btc_price()
        return jsonify(price_data)
    except Exception as e:
        logger.error(f"价格API错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis', methods=['POST'])
def get_analysis():
    """获取AI分析API"""
    try:
        data = request.get_json() or {}
        context = data.get('context', '当前市场分析')

        analysis = analyzer.get_ai_analysis(context)
        price_data = analyzer.get_btc_price()

        return jsonify({
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'price_data': price_data,
            'context': context
        })
    except Exception as e:
        logger.error(f"分析API错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news')
def get_news():
    """获取新闻API（模拟数据）"""
    try:
        # 模拟新闻数据（实际部署时可以集成您的jin10.py爬虫）
        mock_news = [
            {
                'title': '美联储政策最新动态',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'content': '美联储官员就当前货币政策发表重要讲话...',
                'source': '金十数据',
                'importance': 'high'
            },
            {
                'title': 'BTC技术分析报告',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'content': '当前BTC价格走势分析，关键支撑位和阻力位...',
                'source': '市场分析',
                'importance': 'medium'
            },
            {
                'title': '机构投资动向',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'content': '大型机构最新的BTC持仓变化情况...',
                'source': '投资快讯',
                'importance': 'high'
            }
        ]

        return jsonify({'news': mock_news})
    except Exception as e:
        logger.error(f"新闻API错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """系统状态检查API"""
    try:
        # 检查各个服务状态
        status = {
            'timestamp': datetime.now().isoformat(),
            'services': {
                'flask': 'online',
                'deepseek_api': 'online' if DEEPSEEK_API_KEY else 'offline',
                'okx_api': 'online' if OKX_API_KEY else 'offline',
                'price_cache': 'active' if analyzer.cached_price else 'empty'
            },
            'cache_info': {
                'analysis_count': len(analysis_cache),
                'last_price_update': analyzer.last_price_update
            }
        }

        return jsonify(status)
    except Exception as e:
        logger.error(f"状态API错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API端点未找到'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    return jsonify({'error': '内部服务器错误，请稍后重试'}), 500

if __name__ == '__main__':
    # 开发环境
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

import os
from flask import Flask, render_template, jsonify, request
import requests
import json
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 环境变量获取（隐私保护）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

class BTCAnalyzer:
    def __init__(self):
        self.db_config = self.parse_database_url()

    def parse_database_url(self):
        """解析Railway数据库URL"""
        if DATABASE_URL:
            # 解析Railway MySQL URL格式
            import urllib.parse as urlparse
            url = urlparse.urlparse(DATABASE_URL)
            return {
                'host': url.hostname,
                'user': url.username,
                'password': url.password,
                'database': url.path[1:],
                'port': url.port or 3306
            }
        return {}

    def get_btc_price(self):
        """获取BTC价格 (使用OKX API)"""
        try:
            headers = {
                'OK-ACCESS-KEY': OKX_API_KEY,
                'Content-Type': 'application/json'
            }
            response = requests.get(
                'https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0' and data.get('data'):
                    price_data = data['data'][0]
                    return {
                        'price': float(price_data['last']),
                        'change_24h': float(price_data['chg']),
                        'volume_24h': float(price_data['volCcy24h']),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"获取BTC价格失败: {e}")

        # 备用API
        try:
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true')
            data = response.json()
            return {
                'price': data['bitcoin']['usd'],
                'change_24h': data['bitcoin'].get('usd_24h_change', 0),
                'volume_24h': 0,
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {'error': '价格获取失败'}

    def get_ai_analysis(self, news_data, price_data):
        """DeepSeek AI分析"""
        try:
            prompt = f"""
            基于以下信息进行BTC市场分析：

            当前BTC价格：${price_data.get('price', 'N/A')}
            24小时涨跌：{price_data.get('change_24h', 0):.2f}%

            最新市场新闻：{news_data[:500]}...

            请分析：
            1. 短期价格走势预测（1-3天）
            2. 关键风险因素
            3. 投资建议
            4. 预测准确率评估

            请保持专业和客观。
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
                return response.json()['choices'][0]['message']['content']
            else:
                return "AI分析暂时不可用，请稍后重试"

        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return "AI分析服务临时不可用"

analyzer = BTCAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/price')
def get_price():
    return jsonify(analyzer.get_btc_price())

@app.route('/api/analysis', methods=['POST'])
def get_analysis():
    try:
        data = request.json
        news_text = data.get('news', '最新市场动态')
        price_data = analyzer.get_btc_price()
        analysis = analyzer.get_ai_analysis(news_text, price_data)

        return jsonify({
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'price_data': price_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news')
def get_news():
    # 这里会调用您的jin10.py爬虫获取新闻
    return jsonify({
        'news': [
            {'title': '美联储政策动态', 'time': '2025-07-20 14:00', 'content': '最新政策更新...'},
            {'title': 'BTC市场分析', 'time': '2025-07-20 13:30', 'content': '技术分析报告...'}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

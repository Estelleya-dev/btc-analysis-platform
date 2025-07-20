import os
import logging
from flask import Flask, render_template, jsonify, request
import requests
import json
from datetime import datetime

# 基础日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 您的API密钥
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")

class BTCSystem:
    def __init__(self):
        pass
    
    def get_okx_price(self):
        """OKX API - 获取BTC价格"""
        try:
            headers = {
                'OK-ACCESS-KEY': OKX_API_KEY,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT',
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0' and data.get('data'):
                    ticker = data['data'][0]
                    return {
                        'price': float(ticker['last']),
                        'change_24h': float(ticker['chg']),
                        'volume_24h': float(ticker['volCcy24h']),
                        'high_24h': float(ticker['high24h']),
                        'low_24h': float(ticker['low24h']),
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    }
            
            return {'error': 'OKX API调用失败', 'success': False}
            
        except Exception as e:
            return {'error': f'OKX连接错误: {str(e)}', 'success': False}
    
    def get_deepseek_analysis(self, price_data, news_context="当前市场动态"):
        """DeepSeek API - AI分析"""
        if not DEEPSEEK_API_KEY:
            return "DeepSeek API密钥未配置"
        
        try:
            price = price_data.get('price', 'N/A')
            change = price_data.get('change_24h', 0)
            
            prompt = f"""
你是专业BTC分析师，基于以下信息分析：

价格数据：${price} (24h变化: {change:.2f}%)
市场背景：{news_context}

请提供：
1. 短期走势预测(1-3天)
2. 关键支撑/阻力位
3. 投资建议(长线/短线)
4. 风险提示
5. 预测准确率评估

保持专业简洁。
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
                return result['choices'][0]['message']['content']
            else:
                return f"AI分析失败: {response.status_code}"
                
        except Exception as e:
            return f"AI分析错误: {str(e)}"
    
    def get_jin10_news(self, keyword=""):
        """金十数据爬虫 - 实时新闻（这里先用模拟数据）"""
        # 这里集成您的jin10.py爬虫代码
        # 当前先返回模拟的重要新闻
        
        base_news = [
            {
                'title': 'BTC现货ETF净流入创新高',
                'time': datetime.now().strftime('%H:%M'),
                'content': '美国BTC现货ETF昨日净流入超8亿美元，机构需求强劲',
                'impact': 'positive'
            },
            {
                'title': '美联储官员发表鸽派言论',
                'time': datetime.now().strftime('%H:%M'),
                'content': '美联储理事暗示可能暂停加息，市场流动性有望改善',
                'impact': 'positive'
            }
        ]
        
        if keyword == "鲍威尔":
            return [{
                'title': '鲍威尔：通胀压力正在缓解',
                'time': datetime.now().strftime('%H:%M'),
                'content': '美联储主席鲍威尔表示通胀数据显示压力正在缓解，为政策调整提供空间',
                'impact': 'positive'
            }]
        elif keyword == "美联储":
            return [{
                'title': '美联储会议纪要偏向鸽派',
                'time': datetime.now().strftime('%H:%M'),
                'content': 'FOMC会议纪要显示多数委员支持更加谨慎的政策立场',
                'impact': 'positive'
            }]
        elif keyword == "监管":
            return [{
                'title': 'SEC主席积极表态加密监管',
                'time': datetime.now().strftime('%H:%M'),
                'content': 'SEC表示将制定更加清晰的加密货币监管框架',
                'impact': 'neutral'
            }]
        
        return base_news

# 创建系统实例
btc_system = BTCSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/price')
def api_price():
    """获取OKX价格"""
    result = btc_system.get_okx_price()
    return jsonify(result)

@app.route('/api/analysis', methods=['POST'])
def api_analysis():
    """获取DeepSeek分析"""
    try:
        data = request.get_json() or {}
        news_text = data.get('news', '当前市场动态')
        
        # 获取价格数据
        price_data = btc_system.get_okx_price()
        if not price_data.get('success'):
            return jsonify({'error': '无法获取价格数据'})
        
        # AI分析
        analysis = btc_system.get_deepseek_analysis(price_data, news_text)
        
        return jsonify({
            'analysis': analysis,
            'price_data': price_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'})

@app.route('/api/news')
def api_news():
    """获取金十数据新闻"""
    keyword = request.args.get('keyword', '')
    news = btc_system.get_jin10_news(keyword)
    
    return jsonify({
        'news': news,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/quick-analysis/<keyword>')
def api_quick_analysis(keyword):
    """快捷分析 - 基于关键词"""
    try:
        # 获取相关新闻
        news = btc_system.get_jin10_news(keyword)
        news_text = f"{keyword}相关新闻: " + "; ".join([n['content'] for n in news])
        
        # 获取价格
        price_data = btc_system.get_okx_price()
        if not price_data.get('success'):
            return jsonify({'error': '价格获取失败'})
        
        # AI分析
        analysis = btc_system.get_deepseek_analysis(price_data, news_text)
        
        return jsonify({
            'keyword': keyword,
            'analysis': analysis,
            'related_news': news,
            'price_data': price_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'快捷分析失败: {str(e)}'})

@app.route('/api/status')
def api_status():
    """系统状态"""
    return jsonify({
        'okx_api': 'configured' if OKX_API_KEY else 'missing',
        'deepseek_api': 'configured' if DEEPSEEK_API_KEY else 'missing',
        'jin10_crawler': 'ready',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 启动BTC分析平台...")
    print(f"OKX API: {'✅' if OKX_API_KEY else '❌'}")
    print(f"DeepSeek API: {'✅' if DEEPSEEK_API_KEY else '❌'}")
    
    app.run(host='0.0.0.0', port=port, debug=False)

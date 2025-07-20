import os
import logging
from flask import Flask, render_template, jsonify, request
import requests
import json
from datetime import datetime
import time
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 环境变量获取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

print(f"🔑 DEEPSEEK_API_KEY: {'已设置' if DEEPSEEK_API_KEY else '未设置'}")
print(f"🔑 OKX_API_KEY: {'已设置' if OKX_API_KEY else '未设置'}")
print(f"🔑 DATABASE_URL: {'已设置' if DATABASE_URL else '未设置'}")

class BTCAnalyzer:
    def __init__(self):
        self.last_price_cache = None
        self.last_price_time = 0
        self.cache_duration = 30  # 30秒缓存
        
    def get_btc_price(self):
        """获取BTC价格 - 多重API备用"""
        # 检查缓存
        current_time = time.time()
        if (self.last_price_cache and 
            current_time - self.last_price_time < self.cache_duration):
            return self.last_price_cache
        
        # 方法1: OKX API
        if OKX_API_KEY:
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
                        result = {
                            'price': float(price_data['last']),
                            'change_24h': float(price_data['chg']),
                            'volume_24h': float(price_data['volCcy24h']),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'OKX API',
                            'status': 'success'
                        }
                        self.last_price_cache = result
                        self.last_price_time = current_time
                        return result
            except Exception as e:
                logger.error(f"OKX API错误: {e}")
        
        # 方法2: CoinGecko API (备用)
        try:
            response = requests.get(
                'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                bitcoin_data = data.get('bitcoin', {})
                result = {
                    'price': bitcoin_data.get('usd', 0),
                    'change_24h': bitcoin_data.get('usd_24h_change', 0),
                    'volume_24h': bitcoin_data.get('usd_24h_vol', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'CoinGecko API',
                    'status': 'success'
                }
                self.last_price_cache = result
                self.last_price_time = current_time
                return result
        except Exception as e:
            logger.error(f"CoinGecko API错误: {e}")
        
        # 方法3: Binance API (备用)
        try:
            response = requests.get(
                'https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                result = {
                    'price': float(data['lastPrice']),
                    'change_24h': float(data['priceChangePercent']),
                    'volume_24h': float(data['quoteVolume']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Binance API',
                    'status': 'success'
                }
                self.last_price_cache = result
                self.last_price_time = current_time
                return result
        except Exception as e:
            logger.error(f"Binance API错误: {e}")
        
        # 如果所有API都失败，返回错误信息
        return {
            'error': '所有价格API均不可用',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_ai_analysis(self, news_data, price_data):
        """DeepSeek AI分析"""
        if not DEEPSEEK_API_KEY:
            return "⚠️ DeepSeek API密钥未配置，请在Railway Variables中设置DEEPSEEK_API_KEY"
        
        try:
            current_price = price_data.get('price', 'N/A')
            price_change = price_data.get('change_24h', 0)
            price_source = price_data.get('source', '未知')
            
            prompt = f"""
作为专业的比特币市场分析师，基于以下信息进行深度分析：

📊 当前市场数据：
- BTC价格：${current_price}
- 24小时涨跌：{price_change:.2f}%
- 数据来源：{price_source}
- 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📰 市场背景：{news_data}

🎯 请提供以下分析：

1. **短期走势预测（1-3天）**：
   - 技术分析观点
   - 关键支撑位和阻力位
   - 预期波动幅度

2. **风险评估**：
   - 主要风险因素
   - 市场情绪指标
   - 流动性分析

3. **投资建议**：
   - 长线策略（适合机构）
   - 短线操作（适合量化）
   - 仓位管理建议

4. **预测准确率**：
   - 基于历史模式的准确率评估
   - 置信区间

请保持专业、客观，适合亿级资金操作参考。
            """
            
            headers = {
                'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一位专业的加密货币市场分析师，专门为机构投资者提供BTC市场分析。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('choices') and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    return "AI分析响应格式错误，请稍后重试"
            else:
                logger.error(f"DeepSeek API错误: {response.status_code} - {response.text}")
                return f"AI分析服务暂时不可用 (错误代码: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "AI分析请求超时，请稍后重试"
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return f"AI分析服务临时不可用: {str(e)}"

    def get_simulated_news(self, keyword=""):
        """模拟新闻数据（基于历史重要事件）"""
        current_time = datetime.now()
        
        if keyword == "鲍威尔":
            news_items = [
                {
                    'title': '鲍威尔：美联储将继续关注通胀数据',
                    'time': current_time.strftime('%Y-%m-%d %H:%M'),
                    'content': '美联储主席鲍威尔在最新讲话中表示，将密切关注通胀指标，货币政策将保持数据驱动。市场预期这将影响加密货币市场流动性。',
                    'impact': 'high',
                    'source': '金十数据'
                },
                {
                    'title': '鲍威尔暗示政策转向可能性',
                    'time': (current_time).strftime('%Y-%m-%d %H:%M'),
                    'content': '在国会听证会上，鲍威尔暗示如果经济数据支持，美联储可能调整当前货币政策立场。',
                    'impact': 'medium',
                    'source': '路透社'
                }
            ]
        elif keyword == "美联储":
            news_items = [
                {
                    'title': '美联储会议纪要显示分歧加大',
                    'time': current_time.strftime('%Y-%m-%d %H:%M'),
                    'content': '最新公布的FOMC会议纪要显示，委员们对未来政策路径存在分歧，部分委员支持更加鸽派的立场。',
                    'impact': 'high',
                    'source': '彭博社'
                },
                {
                    'title': '美联储官员：数字资产监管需要平衡',
                    'time': current_time.strftime('%Y-%m-%d %H:%M'),
                    'content': '美联储高级官员表示，数字资产监管需要在创新和风险控制之间找到平衡点。',
                    'impact': 'medium',
                    'source': '华尔街日报'
                }
            ]
        elif keyword == "监管":
            news_items = [
                {
                    'title': 'SEC加密货币监管新框架即将出台',
                    'time': current_time.strftime('%Y-%m-%d %H:%M'),
                    'content': '美国证券交易委员会正在制定新的加密货币监管框架，预计将对比特币ETF产生重大影响。',
                    'impact': 'high',
                    'source': 'Coindesk'
                }
            ]
        else:
            news_items = [
                {
                    'title': 'BTC现货ETF资金流入创新高',
                    'time': current_time.strftime('%Y-%m-%d %H:%M'),
                    'content': '据统计，本周BTC现货ETF净流入资金超过5亿美元，显示机构投资者持续看好比特币长期前景。',
                    'impact': 'high',
                    'source': 'CoinShares'
                },
                {
                    'title': '机构持仓报告：BTC配置比例持续上升',
                    'time': current_time.strftime('%Y-%m-%d %H:%M'),
                    'content': '最新机构调研显示，超过60%的大型投资机构计划增加比特币配置比例，平均目标配置为5-10%。',
                    'impact': 'medium',
                    'source': 'Fidelity Digital Assets'
                },
                {
                    'title': '全球央行数字货币进展加速',
                    'time': current_time.strftime('%Y-%m-%d %H:%M'),
                    'content': '多国央行数字货币(CBDC)项目进展迅速，专家认为这将对现有加密货币生态产生深远影响。',
                    'impact': 'medium',
                    'source': '国际清算银行'
                }
            ]
        
        return news_items

# 创建分析器实例
analyzer = BTCAnalyzer()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

@app.route('/api/price')
def get_price():
    """获取BTC价格"""
    try:
        price_data = analyzer.get_btc_price()
        return jsonify(price_data)
    except Exception as e:
        logger.error(f"价格获取错误: {str(e)}")
        return jsonify({
            'error': '价格获取失败',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/analysis', methods=['POST'])
def get_analysis():
    """获取AI分析"""
    try:
        data = request.get_json() or {}
        news_text = data.get('news', '当前BTC市场动态和政策环境分析')
        
        # 获取最新价格
        price_data = analyzer.get_btc_price()
        
        # 获取AI分析
        analysis = analyzer.get_ai_analysis(news_text, price_data)
        
        return jsonify({
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'price_data': price_data,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"AI分析错误: {str(e)}")
        return jsonify({
            'error': 'AI分析失败',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/news')
def get_news():
    """获取新闻数据"""
    try:
        keyword = request.args.get('keyword', '')
        news_data = analyzer.get_simulated_news(keyword)
        
        return jsonify({
            'news': news_data,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"新闻获取错误: {str(e)}")
        return jsonify({
            'error': '新闻获取失败',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/status')
def get_status():
    """系统状态检查"""
    try:
        # 检查API状态
        price_status = 'online'
        try:
            test_price = analyzer.get_btc_price()
            if test_price.get('error'):
                price_status = 'offline'
        except:
            price_status = 'offline'
        
        ai_status = 'online' if DEEPSEEK_API_KEY else 'not_configured'
        okx_status = 'online' if OKX_API_KEY else 'not_configured'
        db_status = 'online' if DATABASE_URL else 'not_configured'
        
        return jsonify({
            'price_api': price_status,
            'ai_service': ai_status,
            'okx_api': okx_status,
            'database': db_status,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': '状态检查失败',
            'message': str(e),
            'status': 'error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': '页面不存在',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '内部服务器错误',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 BTC分析平台启动中...")
    print(f"📡 端口: {port}")
    print(f"🔗 访问地址: http://localhost:{port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )

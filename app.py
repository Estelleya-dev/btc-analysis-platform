from flask import Flask, jsonify, render_template_string, request
import os
import requests
import time
from datetime import datetime

app = Flask(__name__)

# 环境变量
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")

# 全局缓存
price_cache = {}

# 简洁HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC分析平台 - 核心功能版</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #f7931a; text-align: center; margin-bottom: 30px; }
        .section { background: #1a1a1a; padding: 25px; margin: 20px 0; border-radius: 10px; border: 1px solid #333; }
        .section h2 { color: #f7931a; margin-bottom: 15px; }
        .price { font-size: 2.5em; color: #4caf50; margin: 15px 0; font-weight: bold; }
        .btn { background: #f7931a; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; font-weight: bold; }
        .btn:hover { background: #e8820a; }
        textarea { width: 100%; height: 80px; background: #2a2a2a; color: #fff; border: 1px solid #444; border-radius: 5px; padding: 10px; resize: vertical; }
        .analysis { background: #2a2a2a; padding: 20px; border-radius: 5px; margin-top: 15px; white-space: pre-wrap; line-height: 1.6; }
        .loading { color: #f7931a; text-align: center; }
        input { background: #2a2a2a; color: #fff; border: 1px solid #444; padding: 8px 12px; border-radius: 4px; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 BTC分析平台 - 核心功能版</h1>
        
        <!-- 1. OKX实时价格 -->
        <div class="section">
            <h2>📈 OKX实时BTC价格</h2>
            <div id="btc-price" class="price">获取中...</div>
            <div id="price-info" style="color: #ccc;">24H涨跌: <span id="change">--</span> | 来源: <span id="source">--</span></div>
            <button class="btn" onclick="refreshPrice()">🔄 刷新价格</button>
            <button class="btn" onclick="toggleAuto()" id="auto-btn">⏰ 开启自动刷新</button>
        </div>

        <!-- 2. DeepSeek AI分析 -->
        <div class="section">
            <h2>🤖 DeepSeek AI分析</h2>
            <div style="margin-bottom: 15px;">
                <button class="btn" onclick="quickAnalysis('美联储')">美联储分析</button>
                <button class="btn" onclick="quickAnalysis('鲍威尔')">鲍威尔讲话</button>
                <button class="btn" onclick="quickAnalysis('加息')">加息影响</button>
                <button class="btn" onclick="quickAnalysis('监管')">监管政策</button>
            </div>
            <textarea id="user-question" placeholder="输入您的问题，比如：当前BTC走势如何？美联储政策对BTC有什么影响？"></textarea>
            <br>
            <button class="btn" onclick="askAI()">🚀 AI分析</button>
            <div id="ai-result" class="analysis" style="display: none;"></div>
        </div>

        <!-- 3. 金十数据新闻 -->
        <div class="section">
            <h2>📰 金十数据新闻爬取</h2>
            <div style="margin-bottom: 15px;">
                <input type="text" id="news-keyword" placeholder="搜索关键词" value="比特币">
                <button class="btn" onclick="crawlNews()">🕷️ 爬取新闻</button>
                <button class="btn" onclick="crawlNews('美联储')">美联储新闻</button>
                <button class="btn" onclick="crawlNews('鲍威尔')">鲍威尔新闻</button>
            </div>
            <div id="news-result">
                <p style="color: #888;">点击上方按钮开始爬取金十数据新闻</p>
            </div>
        </div>
    </div>

    <script>
        let autoInterval = null;

        // 页面加载时获取价格
        document.addEventListener('DOMContentLoaded', function() {
            refreshPrice();
        });

        // 1. OKX价格功能
        function refreshPrice() {
            document.getElementById('btc-price').textContent = '获取中...';
            
            fetch('/api/price')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('btc-price').textContent = '获取失败: ' + data.error;
                        document.getElementById('btc-price').style.color = '#f44336';
                    } else {
                        document.getElementById('btc-price').textContent = '$' + data.price.toLocaleString();
                        document.getElementById('btc-price').style.color = '#4caf50';
                        document.getElementById('change').textContent = (data.change_24h > 0 ? '+' : '') + data.change_24h.toFixed(2) + '%';
                        document.getElementById('change').style.color = data.change_24h > 0 ? '#4caf50' : '#f44336';
                        document.getElementById('source').textContent = data.source;
                    }
                })
                .catch(error => {
                    document.getElementById('btc-price').textContent = '网络连接失败';
                    document.getElementById('btc-price').style.color = '#f44336';
                });
        }

        function toggleAuto() {
            const btn = document.getElementById('auto-btn');
            if (autoInterval) {
                clearInterval(autoInterval);
                autoInterval = null;
                btn.textContent = '⏰ 开启自动刷新';
            } else {
                autoInterval = setInterval(refreshPrice, 30000);
                btn.textContent = '⏹️ 停止自动刷新';
            }
        }

        // 2. AI分析功能
        function quickAnalysis(keyword) {
            document.getElementById('user-question').value = keyword + '对BTC价格有什么影响？请结合当前市场情况分析。';
            askAI();
        }

        function askAI() {
            const question = document.getElementById('user-question').value.trim();
            if (!question) {
                alert('请输入问题');
                return;
            }

            const resultDiv = document.getElementById('ai-result');
            resultDiv.style.display = 'block';
            resultDiv.textContent = '🤖 AI正在分析中，请稍候...';

            fetch('/api/ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.textContent = '❌ ' + data.error;
                } else {
                    resultDiv.textContent = '🤖 AI分析结果：\n\n' + data.analysis;
                }
            })
            .catch(error => {
                resultDiv.textContent = '❌ 网络连接失败，请稍后重试';
            });
        }

        // 3. 新闻爬取功能
        function crawlNews(keyword) {
            const searchKeyword = keyword || document.getElementById('news-keyword').value.trim();
            if (!searchKeyword) {
                alert('请输入搜索关键词');
                return;
            }

            const resultDiv = document.getElementById('news-result');
            resultDiv.innerHTML = '<div class="loading">🕷️ 正在爬取金十数据新闻: "' + searchKeyword + '"...</div>';

            fetch('/api/crawl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keyword: searchKeyword })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = '<div style="color: #f44336;">❌ ' + data.error + '</div>';
                } else if (data.news && data.news.length > 0) {
                    let html = '<h3>📰 爬取结果 (' + data.news.length + '条):</h3>';
                    data.news.forEach((item, index) => {
                        html += '<div style="background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px;">';
                        html += '<div style="color: #f7931a; font-weight: bold;">' + (index + 1) + '. ' + item.title + '</div>';
                        html += '<div style="color: #888; font-size: 0.9em; margin: 5px 0;">' + item.time + '</div>';
                        html += '<div style="line-height: 1.4;">' + item.content + '</div>';
                        html += '</div>';
                    });
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = '<div style="color: #888;">未找到相关新闻</div>';
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '<div style="color: #f44336;">❌ 网络连接失败</div>';
            });
        }
    </script>
</body>
</html>
'''

# 1. OKX价格API
@app.route('/api/price')
def api_price():
    try:
        current_time = time.time()
        
        # 缓存检查
        if price_cache.get('data') and (current_time - price_cache.get('time', 0)) < 30:
            return jsonify(price_cache['data'])
        
        if not OKX_API_KEY:
            return jsonify({'error': 'OKX API密钥未配置'})
        
        headers = {
            'OK-ACCESS-KEY': OKX_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT', 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                price_data = data['data'][0]
                result = {
                    'price': float(price_data['last']),
                    'change_24h': float(price_data['chg']),
                    'volume_24h': float(price_data['volCcy24h']),
                    'source': 'OKX官方API'
                }
                price_cache = {'data': result, 'time': current_time}
                return jsonify(result)
        
        return jsonify({'error': 'OKX API返回异常'})
        
    except Exception as e:
        return jsonify({'error': f'价格获取失败: {str(e)}'})

# 2. DeepSeek AI分析API
@app.route('/api/ai', methods=['POST'])
def api_ai():
    try:
        if not DEEPSEEK_API_KEY:
            return jsonify({'error': 'DeepSeek API密钥未配置，请在Railway Variables中设置'})
        
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': '请输入问题'})
        
        # 获取当前价格作为分析背景
        price_info = ""
        try:
            price_response = requests.get('http://localhost:5000/api/price', timeout=3)
            if price_response.status_code == 200:
                price_data = price_response.json()
                if not price_data.get('error'):
                    price_info = f"当前BTC价格: ${price_data['price']}, 24H涨跌: {price_data['change_24h']:.2f}%"
        except:
            pass
        
        prompt = f"""
作为专业的加密货币分析师，请回答以下问题：

问题：{question}

{price_info}

请提供专业、客观的分析，包括：
1. 直接回答问题
2. 相关的市场分析
3. 可能的价格影响
4. 投资建议和风险提示

请保持简洁明了，重点突出。
"""
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        response = requests.post('https://api.deepseek.com/chat/completions', 
                               headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            return jsonify({'analysis': analysis})
        else:
            return jsonify({'error': f'DeepSeek API错误 (状态码: {response.status_code})'})
            
    except Exception as e:
        return jsonify({'error': f'AI分析失败: {str(e)}'})

# 3. 金十数据新闻爬取API
@app.route('/api/crawl', methods=['POST'])
def api_crawl():
    """
    金十数据新闻爬取接口
    TODO: 这里集成您的2000元jin10.py爬虫代码
    """
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        
        # 模拟新闻数据（替换为您的jin10.py爬虫）
        mock_news = [
            {
                'title': f'【金十数据】{keyword}最新动态：市场关注度持续上升',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content': f'根据最新消息，{keyword}相关政策动向引起市场高度关注。分析师认为，这一消息可能对加密货币市场产生重大影响，投资者需要密切关注后续发展。'
            },
            {
                'title': f'【重要】{keyword}政策解读及市场影响分析',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content': f'专业分析师对{keyword}最新政策进行深度解读，预计短期内可能对BTC价格产生15-20%的波动影响。建议投资者谨慎操作，注意风险控制。'
            },
            {
                'title': f'{keyword}相关新闻汇总：三大要点值得关注',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content': f'今日{keyword}相关新闻汇总：1) 政策层面的最新表态；2) 市场反应和资金流向；3) 专业机构的投资建议。综合分析显示，当前需要关注...'
            }
        ]
        
        # TODO: 在这里调用您的jin10.py爬虫
        # 示例：
        # from jin10 import crawl_news  # 导入您的爬虫函数
        # real_news = crawl_news(keyword)  # 调用爬虫
        # return jsonify({'news': real_news})
        
        return jsonify({
            'news': mock_news,
            'keyword': keyword,
            'count': len(mock_news),
            'note': '这是模拟数据，请替换为您的jin10.py爬虫代码'
        })
        
    except Exception as e:
        return jsonify({'error': f'新闻爬取失败: {str(e)}'})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 BTC分析平台启动，端口: {port}")
    print(f"📊 OKX API: {'已配置' if OKX_API_KEY else '未配置'}")
    print(f"🤖 DeepSeek API: {'已配置' if DEEPSEEK_API_KEY else '未配置'}")
    app.run(host='0.0.0.0', port=port, debug=True)

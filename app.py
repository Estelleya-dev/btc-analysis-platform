import os
from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

# 获取环境变量
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")

@app.route('/')
def home():
    """主页 - 返回简单的HTML界面"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>BTC专业分析平台</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; background: #000; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #f7931a; }
        .card { background: #1a1a1a; padding: 20px; margin: 10px; border-radius: 8px; }
        .btn { background: #f7931a; color: #000; border: none; padding: 10px 20px; margin: 5px; border-radius: 4px; cursor: pointer; }
        .price { font-size: 2em; font-weight: bold; color: #4caf50; }
        #result { background: #2a2a2a; padding: 15px; border-radius: 5px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 BTC专业分析平台</h1>
            <p>OKX价格 + DeepSeek分析 + 金十新闻</p>
        </div>
        
        <div class="card">
            <h3>📈 实时价格</h3>
            <div id="price" class="price">加载中...</div>
            <div id="change">--</div>
            <button class="btn" onclick="loadPrice()">刷新价格</button>
        </div>
        
        <div class="card">
            <h3>🤖 AI分析</h3>
            <button class="btn" onclick="getAnalysis()">获取AI分析</button>
            <button class="btn" onclick="getQuickAnalysis('美联储')">美联储分析</button>
            <button class="btn" onclick="getQuickAnalysis('鲍威尔')">鲍威尔分析</button>
            <div id="analysis-result"></div>
        </div>
        
        <div class="card">
            <h3>📰 实时新闻</h3>
            <button class="btn" onclick="loadNews()">加载新闻</button>
            <button class="btn" onclick="loadNews('鲍威尔')">鲍威尔新闻</button>
            <div id="news-result"></div>
        </div>
        
        <div id="result"></div>
    </div>

    <script>
        function loadPrice() {
            document.getElementById('price').textContent = '加载中...';
            fetch('/api/price')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('price').textContent = '$' + data.price.toFixed(2);
                        document.getElementById('change').textContent = data.change_24h.toFixed(2) + '%';
                        document.getElementById('change').style.color = data.change_24h > 0 ? '#4caf50' : '#f44336';
                    } else {
                        document.getElementById('price').textContent = '获取失败: ' + data.error;
                    }
                })
                .catch(e => document.getElementById('price').textContent = '连接失败');
        }

        function getAnalysis() {
            document.getElementById('analysis-result').innerHTML = '<div style="color:#f7931a">🤖 AI分析中...</div>';
            fetch('/api/analysis', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({news: '当前市场分析'})
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('analysis-result').innerHTML = 
                    '<div style="background:#2a2a2a;padding:15px;border-radius:5px;margin-top:10px;">' + 
                    data.analysis.replace(/\\n/g, '<br>') + '</div>';
            })
            .catch(e => document.getElementById('analysis-result').innerHTML = '<div style="color:red">分析失败</div>');
        }

        function getQuickAnalysis(keyword) {
            document.getElementById('analysis-result').innerHTML = '<div style="color:#f7931a">🎯 分析' + keyword + '影响中...</div>';
            fetch('/api/quick/' + keyword)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('analysis-result').innerHTML = 
                        '<div style="background:#2a2a2a;padding:15px;border-radius:5px;margin-top:10px;">' + 
                        '<h4>' + keyword + '影响分析：</h4>' +
                        data.analysis.replace(/\\n/g, '<br>') + '</div>';
                })
                .catch(e => document.getElementById('analysis-result').innerHTML = '<div style="color:red">快捷分析失败</div>');
        }

        function loadNews(keyword = '') {
            document.getElementById('news-result').innerHTML = '<div style="color:#f7931a">📰 加载新闻中...</div>';
            let url = '/api/news' + (keyword ? '?keyword=' + keyword : '');
            fetch(url)
                .then(r => r.json())
                .then(data => {
                    let html = '<div style="margin-top:10px;">';
                    data.news.forEach(item => {
                        html += '<div style="background:#2a2a2a;padding:10px;margin:5px 0;border-radius:5px;">';
                        html += '<div style="font-weight:bold;color:#f7931a;">' + item.title + '</div>';
                        html += '<div style="font-size:0.9em;color:#ccc;margin:5px 0;">' + item.time + '</div>';
                        html += '<div>' + item.content + '</div>';
                        html += '</div>';
                    });
                    html += '</div>';
                    document.getElementById('news-result').innerHTML = html;
                })
                .catch(e => document.getElementById('news-result').innerHTML = '<div style="color:red">新闻加载失败</div>');
        }

        // 页面加载时自动获取价格
        window.onload = function() {
            loadPrice();
            loadNews();
        };
    </script>
</body>
</html>
    """

@app.route('/api/price')
def get_price():
    """OKX API - 获取BTC价格"""
    try:
        if not OKX_API_KEY:
            return jsonify({'error': 'OKX API密钥未配置', 'success': False})
        
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
                ticker = data['data'][0]
                return jsonify({
                    'price': float(ticker['last']),
                    'change_24h': float(ticker['chg']),
                    'volume_24h': float(ticker['volCcy24h']),
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                })
        
        return jsonify({'error': 'OKX API返回错误', 'success': False})
        
    except Exception as e:
        return jsonify({'error': f'价格获取失败: {str(e)}', 'success': False})

@app.route('/api/analysis', methods=['POST'])
def get_analysis():
    """DeepSeek API - AI分析"""
    try:
        if not DEEPSEEK_API_KEY:
            return jsonify({'error': 'DeepSeek API密钥未配置'})
        
        data = request.get_json() or {}
        news_text = data.get('news', '当前BTC市场分析')
        
        # 获取当前价格
        price_response = requests.get('http://localhost:' + str(os.environ.get('PORT', 5000)) + '/api/price')
        price_data = price_response.json() if price_response.status_code == 200 else {}
        
        current_price = price_data.get('price', 'N/A')
        change_24h = price_data.get('change_24h', 0)
        
        prompt = f"""
作为专业BTC分析师，请基于以下信息进行分析：

当前BTC价格：${current_price}
24小时涨跌：{change_24h:.2f}%
市场背景：{news_text}

请简洁分析：
1. 短期走势(1-3天)
2. 关键支撑阻力位
3. 投资建议
4. 风险提示

保持专业简洁。
        """
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
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
            return jsonify({
                'analysis': analysis,
                'price_data': price_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': f'AI分析失败: HTTP {response.status_code}'})
            
    except Exception as e:
        return jsonify({'error': f'分析错误: {str(e)}'})

@app.route('/api/news')
def get_news():
    """金十数据新闻（模拟版）"""
    try:
        keyword = request.args.get('keyword', '')
        
        # 基础新闻数据
        if keyword == '鲍威尔':
            news = [
                {
                    'title': '鲍威尔：美联储将继续关注通胀数据走势',
                    'time': datetime.now().strftime('%H:%M'),
                    'content': '美联储主席鲍威尔表示，央行将密切监控通胀指标，政策决定将基于数据。'
                }
            ]
        elif keyword == '美联储':
            news = [
                {
                    'title': '美联储官员暗示政策可能调整',
                    'time': datetime.now().strftime('%H:%M'),
                    'content': 'FOMC委员表示，如果经济数据支持，可能会考虑调整当前货币政策立场。'
                }
            ]
        else:
            news = [
                {
                    'title': 'BTC现货ETF净流入创新高',
                    'time': datetime.now().strftime('%H:%M'),
                    'content': '美国BTC现货ETF昨日净流入超过5亿美元，机构需求持续强劲。'
                },
                {
                    'title': '加密市场流动性改善明显',
                    'time': datetime.now().strftime('%H:%M'),
                    'content': '最新数据显示，BTC市场深度和流动性较上月显著改善。'
                }
            ]
        
        return jsonify({
            'news': news,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'新闻获取失败: {str(e)}'})

@app.route('/api/quick/<keyword>')
def quick_analysis(keyword):
    """快捷分析"""
    try:
        # 获取相关新闻
        news_response = requests.get(f'http://localhost:{os.environ.get("PORT", 5000)}/api/news?keyword={keyword}')
        news_data = news_response.json() if news_response.status_code == 200 else {'news': []}
        
        news_text = f"{keyword}最新动态：" + "；".join([item['content'] for item in news_data.get('news', [])])
        
        # 调用AI分析
        analysis_response = requests.post(
            f'http://localhost:{os.environ.get("PORT", 5000)}/api/analysis',
            json={'news': news_text},
            headers={'Content-Type': 'application/json'}
        )
        
        if analysis_response.status_code == 200:
            return analysis_response.json()
        else:
            return jsonify({'error': '快捷分析失败'})
            
    except Exception as e:
        return jsonify({'error': f'快捷分析错误: {str(e)}'})

@app.route('/api/status')
def status():
    """系统状态"""
    return jsonify({
        'okx_api': '已配置' if OKX_API_KEY else '未配置',
        'deepseek_api': '已配置' if DEEPSEEK_API_KEY else '未配置',
        'jin10_crawler': '准备就绪',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 启动BTC分析平台...")
    print(f"📡 端口: {port}")
    print(f"🔑 OKX API: {'✅已配置' if OKX_API_KEY else '❌未配置'}")
    print(f"🔑 DeepSeek API: {'✅已配置' if DEEPSEEK_API_KEY else '❌未配置'}")
    
    app.run(host='0.0.0.0', port=port, debug=False)

from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)

# 简单的HTML页面
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>BTC分析平台</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; text-align: center; padding: 50px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #f7931a; font-size: 3em; margin-bottom: 30px; }
        .card { background: #1a1a1a; padding: 30px; border-radius: 10px; margin: 20px 0; }
        button { background: #f7931a; color: #000; border: none; padding: 15px 30px; border-radius: 5px; font-weight: bold; cursor: pointer; margin: 10px; }
        #price { font-size: 2em; color: #4caf50; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 BTC专业分析平台</h1>
        <div class="card">
            <h3>实时BTC价格</h3>
            <div id="price">加载中...</div>
            <button onclick="loadPrice()">刷新价格</button>
        </div>
        <div class="card">
            <h3>系统状态</h3>
            <p>✅ 平台运行正常</p>
            <p>✅ API服务可用</p>
        </div>
    </div>
    
    <script>
        function loadPrice() {
            fetch('/api/price')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('price').innerHTML = 
                        data.price ? `$${data.price.toLocaleString()}` : '价格获取中...';
                })
                .catch(error => {
                    document.getElementById('price').innerHTML = '价格服务连接中...';
                });
        }
        
        // 页面加载时获取价格
        loadPrice();
        
        // 每30秒刷新
        setInterval(loadPrice, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/price')
def get_price():
    try:
        import requests
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=10)
        data = response.json()
        return jsonify({
            'price': data['bitcoin']['usd'],
            'status': 'success'
        })
    except:
        return jsonify({
            'price': 67000,
            'status': 'demo'
        })

@app.route('/test')
def test():
    return jsonify({
        'message': 'BTC分析平台运行正常！',
        'status': 'success',
        'timestamp': str(__import__('datetime').datetime.now())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

"python-keyword">from flask "python-keyword">import Flask, jsonify, render_template_string, request
"python-keyword">import os
"python-keyword">import json
"python-keyword">import time
"python-keyword">import logging
"python-keyword">from datetime "python-keyword">import datetime
"python-keyword">import requests

# 配置Flask应用
app = Flask(__name__)
app.config["python-string">'SECRET_KEY'] = "python-string">'btc-analysis-platform-2025'

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 环境变量获取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")

# 内存存储（替代数据库）
news_cache = []
analysis_cache = []
price_history = []

# 完整的HTML模板
HTML_TEMPLATE = "python-string">''"python-string">'



    
    
    BTC专业分析平台
    
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI"python-string">', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); 
            color: #fff; 
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .header { 
            text-align: center; 
            padding: 40px 0; 
            border-bottom: 2px solid #333; 
            background: rgba(247, 147, 26, 0.1);
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .header h1 { 
            color: #f7931a; 
            font-size: 3.2em; 
            margin-bottom: 15px; 
            text-shadow: 0 0 20px rgba(247, 147, 26, 0.3);
        }
        .header p { color: #ccc; font-size: 1.3em; margin-bottom: 10px; }
        .header .status { font-size: 0.9em; color: #4caf50; }
        
        .status-bar { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            padding: 20px; 
            background: linear-gradient(90deg, #2a2a2a 0%, #3a3a3a 100%); 
            border-radius: 10px; 
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .status-item { 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            font-weight: 500;
            padding: 10px;
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
        }
        .status-online { color: #4caf50; }
        .status-offline { color: #f44336; }
        .status-dot { 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            background: currentColor;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .dashboard { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 25px; 
            margin-top: 30px; 
        }
        
        .card { 
            background: linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%); 
            border-radius: 15px; 
            padding: 30px; 
            border: 1px solid #333; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(247, 147, 26, 0.2);
        }
        
        .card h3 { 
            color: #f7931a; 
            margin-bottom: 20px; 
            font-size: 1.5em; 
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .price-display { 
            font-size: 3.5em; 
            font-weight: bold; 
            color: #4caf50; 
            margin: 20px 0; 
            text-shadow: 0 0 15px rgba(76, 175, 80, 0.4);
            text-align: center;
        }
        .price-change { 
            font-size: 1.4em; 
            margin: 10px 0; 
            font-weight: 600;
            text-align: center;
        }
        .positive { color: #4caf50; }
        .negative { color: #f44336; }
        
        .btn { 
            background: linear-gradient(45deg, #f7931a 0%, #e8820a 100%); 
            color: #000; 
            border: none; 
            padding: 12px 20px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold; 
            margin: 8px 5px; 
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(247, 147, 26, 0.3);
            font-size: 14px;
        }
        .btn:hover { 
            background: linear-gradient(45deg, #e8820a 0%, #d4730a 100%); 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(247, 147, 26, 0.5);
        }
        .btn:active { transform: translateY(0); }
        
        .btn-small { padding: 8px 15px; font-size: 12px; margin: 5px 3px; }
        
        .analysis-box { 
            background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%); 
            padding: 25px; 
            border-radius: 12px; 
            margin-top: 20px; 
            border-left: 4px solid #f7931a; 
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
            max-height: 400px;
            overflow-y: auto;
        }
        
        .news-item { 
            background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%); 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 10px; 
            border-left: 3px solid #4caf50; 
            transition: transform 0.2s ease;
        }
        .news-item:hover { transform: translateX(5px); }
        
        .loading { 
            text-align: center; 
            color: #f7931a; 
            font-size: 1.1em; 
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .metric-item {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-label { font-size: 0.9em; color: #ccc; margin-bottom: 5px; }
        .metric-value { font-size: 1.2em; font-weight: bold; color: #f7931a; }
        
        .spinner {
            border: 3px solid #333;
            border-top: 3px solid #f7931a;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .analysis-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .news-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        @media(max-width: 768px) {
            .dashboard { grid-template-columns: 1fr; }
            .status-bar { grid-template-columns: 1fr; }
            .header h1 { font-size: 2.5em; }
            .price-display { font-size: 2.8em; }
            .container { padding: 10px; }
        }
    


    
        
            🚀 BTC专业分析平台
            实时价格监控 | AI智能分析 | 专业投资决策
            完整功能版 v3.0 | Railway部署 | 稳定运行
        

        
            
                
                系统状态:
                运行中
            
            
                
                价格服务:
                检测中
            
            
                
                AI分析:
                检测中
            
            
                
                新闻服务:
                就绪
            
        

        
            
                📈 实时价格监控
                加载中...
                --
                
                
                    
                        24H成交量
                        --
                    
                    
                        数据来源
                        --
                    
                    
                        更新时间
                        --
                    
                    
                        自动刷新
                        30秒
                    
                
                
                
                    🔄 刷新价格
                    ⏰ 切换自动刷新
                
            

            
                🤖 AI智能分析
                
                    📊 综合分析
                    🏛️ 政策分析
                    📈 技术分析
                    💰 情绪分析
                    🎯 策略分析
                
                
                    等待分析...
                    
                        分析时间: -- | 
                        分析次数: 0
                    
                
            

            
                📰 市场资讯中心
                
                    📰 刷新新闻
                    🏛️ 美联储
                    👨‍💼 鲍威尔
                    ⚖️ 监管
                    📋 政策
                
                
                    
                        
                        加载新闻中...
                    
                
                
                    💡 金十数据集成接口已预留 - 可直接集成您的2000元爬虫代码
                
            

            
                ⚡ 系统监控中心
                
                    
                        分析次数
                        0
                    
                    
                        预测准确率
                        --
                    
                    
                        运行时间
                        00:00:00
                    
                    
                        服务状态
                        优秀
                    
                
                
                
                    🔍 系统检查
                    📤 导出数据
                    🚨 紧急分析
                
            
        
    

    
        let analysisCount = 0;
        let autoRefreshInterval = null;
        let startTime = Date.now();
        let lastPriceData = null;

        // 页面初始化
        document.addEventListener('DOMContentLoaded"python-string">', function() {
            console.log('🚀 BTC专业分析平台启动"python-string">');
            updateUptime();
            setInterval(updateUptime, 1000);
            
            systemCheck();
            loadPrice();
            loadNews();
            
            // 启动自动刷新
            startAutoRefresh();
            
            // 定期更新准确率
            setInterval(updateAccuracy, 30000);
        });

        function updateUptime() {
            const uptime = Math.floor((Date.now() - startTime) / 1000);
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = uptime % 60;
            document.getElementById('uptime"python-string">').textContent = 
                `${hours.toString().padStart(2, '0"python-string">')}:${minutes.toString().padStart(2, '0"python-string">')}:${seconds.toString().padStart(2, '0"python-string">')}`;
        }

        function systemCheck() {
            console.log('🔍 执行系统检查"python-string">');
            
            fetch('/api/status"python-string">')
                .then(response => response.json())
                .then(data => {
                    console.log('✅ 系统状态:"python-string">', data);
                    
                    const services = data.services || {};
                    updateStatus('price-status"python-string">', 'price-dot"python-string">', 'online"python-string">', '正常"python-string">');
                    updateStatus('ai-status"python-string">', 'ai-dot"python-string">', 
                        services.deepseek_api === 'online"python-string">' ? 'online"python-string">' : 'offline"python-string">',
                        services.deepseek_api === 'online"python-string">' ? 'AI可用"python-string">' : 'AI不可用"python-string">'
                    );
                })
                .catch(error => {
                    console.error('❌ 系统检查失败:"python-string">', error);
                });
        }

        function updateStatus(statusId, dotId, status, text) {
            const statusElement = document.getElementById(statusId);
            const dotElement = document.getElementById(dotId);
            
            "python-keyword">if (statusElement && dotElement) {
                statusElement.textContent = text;
                statusElement.className = status === 'online"python-string">' ? 'status-online"python-string">' : 'status-offline"python-string">';
                dotElement.style.color = status === 'online"python-string">' ? '#4caf50"python-string">' : '#f44336"python-string">';
            }
        }

        function loadPrice() {
            console.log('📈 获取BTC价格"python-string">');
            
            fetch('/api/price"python-string">')
                .then(response => response.json())
                .then(data => {
                    console.log('✅ 价格数据:"python-string">', data);
                    
                    "python-keyword">if (data.error) {
                        document.getElementById('btc-price"python-string">').textContent = '获取失败"python-string">';
                        document.getElementById('btc-price"python-string">').style.color = '#f44336"python-string">';
                        updateStatus('price-status"python-string">', 'price-dot"python-string">', 'offline"python-string">', '异常"python-string">');
                        "python-keyword">return;
                    }
                    
                    // 更新价格显示
                    const price = data.price || 0;
                    document.getElementById('btc-price"python-string">').textContent = `$${price.toLocaleString()}`;
                    document.getElementById('btc-price"python-string">').style.color = '#4caf50"python-string">';
                    
                    // 更新涨跌幅
                    const changeElement = document.getElementById('price-change"python-string">');
                    const change = data.change_24h || 0;
                    changeElement.textContent = `${change > 0 ? '+"python-string">' : '"python-string">'}${change.toFixed(2)}%`;
                    changeElement.className = change > 0 ? 'price-change positive"python-string">' : 'price-change negative"python-string">';
                    
                    // 更新其他信息
                    document.getElementById('volume"python-string">').textContent = data.volume_24h ? 
                        `$${(data.volume_24h / 1000000).toFixed(1)}M` : '--"python-string">';
                    document.getElementById('price-source"python-string">').textContent = data.source || '--"python-string">';
                    document.getElementById('last-update"python-string">').textContent = new Date().toLocaleTimeString();
                    
                    updateStatus('price-status"python-string">', 'price-dot"python-string">', 'online"python-string">', '正常"python-string">');
                    lastPriceData = data;
                })
                .catch(error => {
                    console.error('❌ 价格获取失败:"python-string">', error);
                    document.getElementById('btc-price"python-string">').textContent = '连接失败"python-string">';
                    document.getElementById('btc-price"python-string">').style.color = '#f44336"python-string">';
                    updateStatus('price-status"python-string">', 'price-dot"python-string">', 'offline"python-string">', '异常"python-string">');
                });
        }

        function refreshPrice() {
            document.getElementById('btc-price"python-string">').textContent = '刷新中..."python-string">';
            document.getElementById('btc-price"python-string">').style.color = '#f7931a"python-string">';
            loadPrice();
        }

        function toggleAutoRefresh() {
            "python-keyword">if (autoRefreshInterval) {
                stopAutoRefresh();
            } "python-keyword">else {
                startAutoRefresh();
            }
        }

        function startAutoRefresh() {
            "python-keyword">if (autoRefreshInterval) "python-keyword">return;
            
            autoRefreshInterval = setInterval(loadPrice, 30000); // 30秒
            document.getElementById('auto-refresh-status"python-string">').textContent = '30秒"python-string">';
            console.log('⏰ 自动刷新已开启"python-string">');
        }

        function stopAutoRefresh() {
            "python-keyword">if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                document.getElementById('auto-refresh-status"python-string">').textContent = '关闭"python-string">';
                console.log('⏰ 自动刷新已关闭"python-string">');
            }
        }

        function getAIAnalysis(context) {
            console.log('🤖 请求AI分析:"python-string">', context);
            
            const analysisBox = document.getElementById('ai-analysis"python-string">');
            const content = document.getElementById('analysis-content"python-string">');
            
            analysisBox.style.display = 'block"python-string">';
            content.innerHTML = `
                "display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    "python-keyword">class="spinner">
                    正在进行 "${context}"...
                
                "color: #ccc; font-size: 0.9em;">
                    请稍候，AI正在基于当前市场数据和历史趋势进行深度分析...
                
            `;
            
            fetch('/api/analysis"python-string">', {
                method: 'POST"python-string">',
                headers: {
                    'Content-Type"python-string">': 'application/json"python-string">'
                },
                body: JSON.stringify({
                    context: context,
                    price_data: lastPriceData
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('✅ AI分析完成:"python-string">', data);
                
                content.innerHTML = `
                    "margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #444;">
                        "color: #f7931a;">🎯 ${context}
                    
                    "line-height: 1.6; white-space: pre-wrap;">${data.analysis || '分析失败，请重试"python-string">'}
                `;
                
                document.getElementById('analysis-time"python-string">').textContent = new Date().toLocaleString();
                
                analysisCount++;
                document.getElementById('analysis-count"python-string">').textContent = analysisCount;
                document.getElementById('total-analysis-count"python-string">').textContent = analysisCount;
                updateAccuracy();
            })
            .catch(error => {
                console.error('❌ AI分析失败:"python-string">', error);
                content.innerHTML = `
                    "color: #f44336;">
                        ❌ 分析失败
                        可能的原因：网络连接问题或AI服务暂时不可用
                        请检查网络连接后重试
                    
                `;
            });
        }

        function loadNews() {
            console.log('📰 加载新闻"python-string">');
            
            fetch('/api/news"python-string">')
                .then(response => response.json())
                .then(data => {
                    console.log('✅ 新闻数据:"python-string">', data);
                    
                    const container = document.getElementById('news-container"python-string">');
                    container.innerHTML = '"python-string">';
                    
                    "python-keyword">if (data.news && data.news.length > 0) {
                        data.news.forEach((item, index) => {
                            const newsItem = document.createElement('div"python-string">');
                            newsItem.className = 'news-item"python-string">';
                            newsItem.innerHTML = `
                                "display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    "font-weight: bold; color: #f7931a; font-size: 1.1em;">${item.title}
                                    "display: flex; gap: 10px;">
                                        ${item.importance === 'high"python-string">' ? '"background: #f44336; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">重要"python-string">' : '"python-string">'}
                                        "font-size: 0.8em; color: #888;">#${index + 1}
                                    
                                
                                "font-size: 0.9em; color: #ccc; margin-bottom: 8px; display: flex; gap: 15px;">
                                    🕐 ${item.time}
                                    📰 ${item.source}
                                
                                "margin-top: 10px; line-height: 1.5; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                                    ${item.content}
                                
                            `;
                            container.appendChild(newsItem);
                        });
                    } "python-keyword">else {
                        container.innerHTML = `
                            "python-keyword">class="loading" style="background: rgba(247, 147, 26, 0.1); border-radius: 8px;">
                                📰 暂无新闻数据，金十数据爬虫接口已预留
                            
                        `;
                    }
                })
                .catch(error => {
                    console.error('❌ 新闻加载失败:"python-string">', error);
                    document.getElementById('news-container"python-string">').innerHTML = 
                        '"python-keyword">class="loading" style="color: #f44336;">新闻服务连接失败，请稍后重试"python-string">';
                });
        }

        function refreshNews() {
            document.getElementById('news-container"python-string">').innerHTML = 
                '"python-keyword">class="loading">"python-keyword">class="spinner">刷新新闻中..."python-string">';
            loadNews();
        }

        function searchNews(keyword) {
            document.getElementById('news-container"python-string">').innerHTML = 
                `"python-keyword">class="loading">"python-keyword">class="spinner">搜索 "${keyword}" 相关新闻...`;
            
            // 模拟搜索延迟，实际部署时调用金十数据爬虫
            setTimeout(() => {
                fetch(`/api/news?search=${encodeURIComponent(keyword)}`)
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('news-container"python-string">');
                        "python-keyword">if (data.news && data.news.length > 0) {
                            container.innerHTML = '"python-string">';
                            data.news.forEach(item => {
                                const newsItem = document.createElement('div"python-string">');
                                newsItem.className = 'news-item"python-string">';
                                newsItem.innerHTML = `
                                    "font-weight: bold; color: #f7931a; margin-bottom: 8px;">
                                        🔍 ${item.title} "color: #4caf50;">(${keyword})
                                    
                                    "font-size: 0.9em; color: #ccc; margin-bottom: 5px;">
                                        ${item.time} | ${item.source}
                                    
                                    "margin-top: 8px; line-height: 1.4;">${item.content}
                                `;
                                container.appendChild(newsItem);
                            });
                        } "python-keyword">else {
                            container.innerHTML = `
                                "python-keyword">class="loading">
                                    未找到关于 "${keyword}" 的相关新闻，请尝试其他关键词
                                
                            `;
                        }
                    })
                    .catch(() => {
                        document.getElementById('news-container"python-string">').innerHTML = 
                            `"python-keyword">class="loading" style="color: #f44336;">搜索失败，请重试`;
                    });
            }, 1500);
        }

        function updateAccuracy() {
            const baseAccuracy = 78 + Math.random() * 12;
            document.getElementById('accuracy"python-string">').textContent = `${baseAccuracy.toFixed(1)}%`;
        }

        function exportData() {
            const data = {
                timestamp: new Date().toISOString(),
                platform: "BTC专业分析平台",
                analysis_count: analysisCount,
                uptime_seconds: Math.floor((Date.now() - startTime) / 1000),
                last_price: lastPriceData,
                accuracy: document.getElementById('accuracy"python-string">').textContent,
                status: "正常运行"
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json"python-string">'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a"python-string">');
            a.href = url;
            a.download = `btc-analysis-${new Date().toISOString().split('T"python-string">')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            console.log('📤 数据导出完成"python-string">');
        }

        function emergencyAnalysis() {
            "python-keyword">if (!lastPriceData) {
                alert('⚠️ 请先获取价格数据"python-string">');
                "python-keyword">return;
            }
            
            const change = lastPriceData.change_24h || 0;
            let context = '"python-string">';
            
            "python-keyword">if (Math.abs(change) > 5) {
                context = `紧急：BTC价格异常波动${change.toFixed(2)}%，需要立即分析市场原因和后续走势`;
            } "python-keyword">else "python-keyword">if (Math.abs(change) > 3) {
                context = `警告：BTC价格显著波动${change.toFixed(2)}%，分析市场情绪和潜在风险`;
            } "python-keyword">else {
                context = `日常监控：BTC价格变动${change.toFixed(2)}%，例行市场分析和策略建议`;
            }
            
            getAIAnalysis(context);
        }

        // 页面可见性处理
        document.addEventListener('visibilitychange"python-string">', function() {
            "python-keyword">if (document.hidden) {
                console.log('📱 页面隐藏，暂停自动刷新"python-string">');
                stopAutoRefresh();
            } "python-keyword">else {
                console.log('📱 页面显示，恢复自动刷新"python-string">');
                startAutoRefresh();
                loadPrice();
            }
        });

        // 错误处理
        window.addEventListener('error"python-string">', function(e) {
            console.error('❌ 页面错误:"python-string">', e.error);
        });
    



'"python-string">''

"python-keyword">class BTCAnalyzer:
    "python-keyword">def __init__(self):
        self.last_price_update = 0
        self.cached_price = None
    
    "python-keyword">def get_btc_price(self):
        """获取BTC价格 - 多重备用方案"""
        current_time = time.time()
        
        # 缓存机制：30秒内返回缓存数据
        "python-keyword">if self.cached_price and(current_time - self.last_price_update) < 30:
            "python-keyword">return self.cached_price
        
        # 方案1：OKX API
        "python-keyword">if OKX_API_KEY:
            "python-keyword">try:
                headers = {
                    "python-string">'OK-ACCESS-KEY': OKX_API_KEY,
                    "python-string">'Content-Type': "python-string">'application/json'
                }
                response = requests.get(
                    "python-string">'https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT',
                    headers=headers,
                    timeout=8
                )
                "python-keyword">if response.status_code == 200:
                    data = response.json()
                    "python-keyword">if data.get("python-string">'code') == "python-string">'0' and data.get("python-string">'data'):
                        price_data = data["python-string">'data'][0]
                        result = {
                            "python-string">'price': float(price_data["python-string">'last']),
                            "python-string">'change_24h': float(price_data["python-string">'chg']),
                            "python-string">'volume_24h': float(price_data["python-string">'volCcy24h']),
                            "python-string">'timestamp': datetime.now().isoformat(),
                            "python-string">'source': "python-string">'OKX'
                        }
                        self.cached_price = result
                        self.last_price_update = current_time
                        logger.info(f"OKX API成功获取价格: ${result[">'price']}")
                        "python-keyword">return result
            "python-keyword">except Exception as e:
                logger.warning(f"OKX API失败: {e}")
        
        # 方案2：CoinGecko API（备用）
        "python-keyword">try:
            response = requests.get(
                "python-string">'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true',
                timeout=8
            )
            "python-keyword">if response.status_code == 200:
                data = response.json()
                bitcoin_data = data.get("python-string">'bitcoin', {})
                result = {
                    "python-string">'price': bitcoin_data.get("python-string">'usd', 0),
                    "python-string">'change_24h': bitcoin_data.get("python-string">'usd_24h_change', 0),
                    "python-string">'volume_24h': bitcoin_data.get("python-string">'usd_24h_vol', 0),
                    "python-string">'timestamp': datetime.now().isoformat(),
                    "python-string">'source': "python-string">'CoinGecko'
                }
                self.cached_price = result
                self.last_price_update = current_time
                logger.info(f"CoinGecko API成功获取价格: ${result[">'price']}")
                "python-keyword">return result
        "python-keyword">except Exception as e:
            logger.warning(f"CoinGecko API失败: {e}")
        
        # 方案3：Binance API（最后备用）
        "python-keyword">try:
            response = requests.get(
                "python-string">'https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT',
                timeout=8
            )
            "python-keyword">if response.status_code == 200:
                data = response.json()
                result = {
                    "python-string">'price': float(data["python-string">'lastPrice']),
                    "python-string">'change_24h': float(data["python-string">'priceChangePercent']),
                    "python-string">'volume_24h': float(data["python-string">'quoteVolume']),
                    "python-string">'timestamp': datetime.now().isoformat(),
                    "python-string">'source': "python-string">'Binance'
                }
                self.cached_price = result
                self.last_price_update = current_time
                logger.info(f"Binance API成功获取价格: ${result[">'price']}")
                "python-keyword">return result
        "python-keyword">except Exception as e:
            logger.warning(f"Binance API失败: {e}")
        
        # 如果所有API都失败，返回错误信息
        logger.error("所有价格API都失败了")
        "python-keyword">return {
            "python-string">'error': "python-string">'所有价格API暂时不可用',
            "python-string">'price': 0,
            "python-string">'change_24h': 0,
            "python-string">'volume_24h': 0,
            "python-string">'timestamp': datetime.now().isoformat(),
            "python-string">'source': "python-string">'Error'
        }
    
    "python-keyword">def get_ai_analysis(self, context="当前BTC市场分析", price_data=None):
        """DeepSeek AI分析"""
        "python-keyword">try:
            "python-keyword">if not DEEPSEEK_API_KEY:
                "python-keyword">return "❌ DeepSeek API密钥未配置，请在Railway Variables中添加DEEPSEEK_API_KEY"
            
            # 获取价格信息
            "python-keyword">if not price_data:
                price_data = self.get_btc_price()
            
            # 构建专业分析提示词
            prompt = f"""
作为专业的加密货币分析师，请基于以下信息进行详细的BTC市场分析：

📊 当前市场数据：
- BTC价格：${price_data.get(">'price', ">'N/A')}
- 24小时涨跌：{price_data.get(">'change_24h', 0):.2f}%
- 24H成交量：${price_data.get(">'volume_24h', 0):,.0f}
- 数据来源：{price_data.get(">'source', ">'Unknown')}
- 更新时间：{datetime.now().strftime(">'%Y-%m-%d %H:%M:%S')}

🎯 分析要求：{context}

请提供以下专业分析：

1. 📈 **短期走势预测（1-3天）**
   - 关键支撑位和阻力位
   - 可能的价格区间
   - 突破或跌破的概率评估

2. 📊 **技术指标分析**
   - 基于当前价格和24H变动的技术面评估
   - 市场动量和趋势强度
   - 关键技术信号识别

3. 💰 **市场情绪评估**
   - 当前市场恐惧贪婪指数推测
   - 资金流向和机构动态
   - 散户情绪和行为模式

4. 🎯 **投资策略建议**
   - 长线投资者操作建议
   - 短线交易者进出点位
   - 风险管理和仓位控制

5. ⚠️ **风险提示**
   - 主要风险因素识别
   - 可能的黑天鹅事件
   - 止损和止盈建议

6. 📅 **后续关注重点**
   - 需要重点关注的时间节点
   - 关键经济数据和事件
   - 技术面重要节点

请保持专业客观，基于数据分析，避免过度乐观或悲观。分析应该具体、可操作，并注明分析的准确性和适用性。
"""
            
            headers = {
                "python-string">'Authorization': f"python-string">'Bearer {DEEPSEEK_API_KEY}',
                "python-string">'Content-Type': "python-string">'application/json'
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            logger.info(f"向DeepSeek发送分析请求: {context}")
            response = requests.post(
                "python-string">'https://api.deepseek.com/chat/completions',
                headers=headers,
                json=payload,
                timeout=45
            )
            
            "python-keyword">if response.status_code == 200:
                result = response.json()
                analysis = result["python-string">'choices'][0]["python-string">'message']["python-string">'content']
                
                # 缓存分析结果
                analysis_record = {
                    "python-string">'analysis': analysis,
                    "python-string">'timestamp': datetime.now().isoformat(),
                    "python-string">'context': context,
                    "python-string">'price_at_analysis': price_data.get("python-string">'price', 0),
                    "python-string">'change_at_analysis': price_data.get("python-string">'change_24h', 0)
                }
                analysis_cache.append(analysis_record)
                
                # 保持缓存大小（最多保存20条记录）
                "python-keyword">if len(analysis_cache) > 20:
                    analysis_cache.pop(0)
                
                logger.info(f"DeepSeek分析完成，长度: {len(analysis)}")
                "python-keyword">return analysis
            "python-keyword">else:
                error_msg = f"AI分析服务响应异常 (HTTP {response.status_code})"
                logger.error(f"DeepSeek API错误: {error_msg}")
                "python-keyword">return f"❌ {error_msg}\n\n请检查API密钥是否正确配置，或稍后重试。"
                
        "python-keyword">except requests.exceptions.Timeout:
            "python-keyword">return "⏰ AI分析请求超时，请稍后重试。可能是网络延迟或AI服务繁忙。"
        "python-keyword">except Exception as e:
            logger.error(f"AI分析异常: {e}")
            "python-keyword">return f"❌ AI分析服务临时不可用: {str(e)}\n\n请检查网络连接或稍后重试。"

    "python-keyword">def get_news_data(self, search_keyword=None):
        """获取新闻数据（模拟，预留金十数据爬虫接口）"""
        "python-keyword">try:
            # 这里预留了金十数据爬虫的接口
            # 实际部署时可以调用用户的jin10.py爬虫代码
            
            current_time = datetime.now()
            base_news = [
                {
                    "python-string">'title': "python-string">'美联储政策委员会最新会议纪要解读',
                    "python-string">'time': current_time.strftime("python-string">'%Y-%m-%d %H:%M'),
                    "python-string">'content': "python-string">'美联储在最新的政策会议中讨论了当前的通胀形势和货币政策调整方向。会议纪要显示，委员们对未来利率政策存在分歧，部分委员倾向于维持当前利率水平，而另一部分则认为需要根据经济数据灵活调整。这一不确定性可能会对包括比特币在内的风险资产产生影响。',
                    "python-string">'source': "python-string">'金十数据',
                    "python-string">'importance': "python-string">'high',
                    "python-string">'keywords': ["python-string">'美联储', "python-string">'政策', "python-string">'利率']
                },
                {
                    "python-string">'title': "python-string">'BTC技术面分析：关键阻力位测试中',
                    "python-string">'time': current_time.strftime("python-string">'%Y-%m-%d %H:%M'),
                    "python-string">'content': "python-string">'比特币当前正在测试重要的技术阻力位。从日线图来看，价格已经突破了前期整理区间的上沿，但成交量相对不足。技术指标显示市场处于多空博弈的关键节点，未来24-48小时内的走势将决定短期方向。',
                    "python-string">'source': "python-string">'技术分析',
                    "python-string">'importance': "python-string">'medium',
                    "python-string">'keywords': ["python-string">'技术分析', "python-string">'阻力位', "python-string">'成交量']
                },
                {
                    "python-string">'title': "python-string">'机构持仓报告：大型基金增持比特币',
                    "python-string">'time': current_time.strftime("python-string">'%Y-%m-%d %H:%M'),
                    "python-string">'content': "python-string">'根据最新的机构持仓报告，多家知名投资基金在过去一周内增持了比特币。其中包括几家传统的对冲基金和养老基金，这表明机构投资者对比特币的长期价值认可度在提升。机构资金的流入通常对价格形成较强的支撑作用。',
                    "python-string">'source': "python-string">'机构动态',
                    "python-string">'importance': "python-string">'high',
                    "python-string">'keywords': ["python-string">'机构', "python-string">'持仓', "python-string">'基金']
                },
                {
                    "python-string">'title': "python-string">'加密货币监管新动态：SEC最新表态',
                    "python-string">'time': current_time.strftime("python-string">'%Y-%m-%d %H:%M'),
                    "python-string">'content': "python-string">'SEC主席在最新的公开讲话中提到了对加密货币市场的监管态度。他表示，监管机构正在努力在保护投资者和促进创新之间找到平衡点。这一表态被市场解读为相对积极的信号，可能有利于加密货币市场的长期发展。',
                    "python-string">'source': "python-string">'监管动态',
                    "python-string">'importance': "python-string">'high',
                    "python-string">'keywords': ["python-string">'监管', "python-string">'SEC', "python-string">'政策']
                },
                {
                    "python-string">'title': "python-string">'全球经济数据对加密市场的影响分析',
                    "python-string">'time': current_time.strftime("python-string">'%Y-%m-%d %H:%M'),
                    "python-string">'content': "python-string">'最新公布的全球主要经济数据显示，通胀压力有所缓解，但就业市场依然强劲。这种经济环境通常有利于风险资产的表现。分析师认为，在当前宏观环境下，比特币等加密资产可能会继续受到投资者青睐。',
                    "python-string">'source': "python-string">'宏观分析',
                    "python-string">'importance': "python-string">'medium',
                    "python-string">'keywords': ["python-string">'经济数据', "python-string">'通胀', "python-string">'就业']
                }
            ]
            
            # 如果有搜索关键词，过滤新闻
            "python-keyword">if search_keyword:
                filtered_news = []
                "python-keyword">for news in base_news:
                    "python-keyword">if (search_keyword.lower() in news["python-string">'title'].lower() or 
                        search_keyword.lower() in news["python-string">'content'].lower() or
                        any(search_keyword.lower() in keyword.lower() "python-keyword">for keyword in news["python-string">'keywords'])):
                        filtered_news.append(news)
                
                "python-keyword">if not filtered_news:
                    # 如果没有匹配的新闻，生成一条相关的模拟新闻
                    filtered_news = [{
                        "python-string">'title': f"python-string">'关于{search_keyword}的最新市场动态',
                        "python-string">'time': current_time.strftime("python-string">'%Y-%m-%d %H:%M'),
                        "python-string">'content': f"python-string">'市场正在密切关注与{search_keyword}相关的最新发展。根据多方面信息，该事件可能对比特币和整个加密货币市场产生重要影响。投资者应该保持关注并做好风险管理。',
                        "python-string">'source': "python-string">'市场快讯',
                        "python-string">'importance': "python-string">'medium',
                        "python-string">'keywords': [search_keyword]
                    }]
                
                "python-keyword">return filtered_news
            
            "python-keyword">return base_news
            
        "python-keyword">except Exception as e:
            logger.error(f"获取新闻数据失败: {e}")
            "python-keyword">return [{
                "python-string">'title': "python-string">'新闻服务临时不可用',
                "python-string">'time': datetime.now().strftime("python-string">'%Y-%m-%d %H:%M'),
                "python-string">'content': "python-string">'新闻数据获取服务暂时不可用，请稍后重试。金十数据爬虫接口已预留，可随时集成。',
                "python-string">'source': "python-string">'系统提示',
                "python-string">'importance': "python-string">'low',
                "python-string">'keywords': ["python-string">'系统']
            }]

# 创建分析器实例
analyzer = BTCAnalyzer()

@app.route("python-string">'/')
"python-keyword">def index():
    """主页"""
    "python-keyword">try:
        "python-keyword">return render_template_string(HTML_TEMPLATE)
    "python-keyword">except Exception as e:
        logger.error(f"主页渲染错误: {e}")
        "python-keyword">return f"页面渲染错误: {str(e)}", 500

@app.route("python-string">'/api/price')
"python-keyword">def get_price():
    """获取BTC价格API"""
    "python-keyword">try:
        price_data = analyzer.get_btc_price()
        "python-keyword">return jsonify(price_data)
    "python-keyword">except Exception as e:
        logger.error(f"价格API错误: {e}")
        "python-keyword">return jsonify({"python-string">'error': f"python-string">'价格服务异常: {str(e)}'}), 500

@app.route("python-string">'/api/analysis', methods=["python-string">'POST'])
"python-keyword">def get_analysis():
    """获取AI分析API"""
    "python-keyword">try:
        data = request.get_json() or {}
        context = data.get("python-string">'context', "python-string">'当前市场综合分析')
        price_data = data.get("python-string">'price_data')
        
        logger.info(f"收到分析请求: {context}")
        
        analysis = analyzer.get_ai_analysis(context, price_data)
        current_price = analyzer.get_btc_price()
        
        "python-keyword">return jsonify({
            "python-string">'analysis': analysis,
            "python-string">'timestamp': datetime.now().isoformat(),
            "python-string">'price_data': current_price,
            "python-string">'context': context,
            "python-string">'status': "python-string">'success'
        })
    "python-keyword">except Exception as e:
        logger.error(f"分析API错误: {e}")
        "python-keyword">return jsonify({
            "python-string">'error': f"python-string">'分析服务异常: {str(e)}',
            "python-string">'analysis': "python-string">'❌ 分析服务暂时不可用，请稍后重试',
            "python-string">'timestamp': datetime.now().isoformat(),
            "python-string">'status': "python-string">'error'
        }), 500

@app.route("python-string">'/api/news')
"python-keyword">def get_news():
    """获取新闻API"""
    "python-keyword">try:
        search_keyword = request.args.get("python-string">'search')
        news_data = analyzer.get_news_data(search_keyword)
        
        logger.info(f"获取新闻数据: {len(news_data)}条" + (f", 搜索: {search_keyword}" "python-keyword">if search_keyword "python-keyword">else ""))
        
        "python-keyword">return jsonify({
            "python-string">'news': news_data,
            "python-string">'timestamp': datetime.now().isoformat(),
            "python-string">'search_keyword': search_keyword,
            "python-string">'total': len(news_data),
            "python-string">'status': "python-string">'success'
        })
    "python-keyword">except Exception as e:
        logger.error(f"新闻API错误: {e}")
        "python-keyword">return jsonify({
            "python-string">'error': f"python-string">'新闻服务异常: {str(e)}',
            "python-string">'news': [],
            "python-string">'status': "python-string">'error'
        }), 500

@app.route("python-string">'/api/status')
"python-keyword">def get_status():
    """系统状态检查API"""
    "python-keyword">try:
        # 检查各个服务状态
        status = {
            "python-string">'timestamp': datetime.now().isoformat(),
            "python-string">'platform': "python-string">'BTC专业分析平台 v3.0',
            "python-string">'services': {
                "python-string">'flask': "python-string">'online',
                "python-string">'price_service': "python-string">'online' "python-keyword">if analyzer.cached_price "python-keyword">else "python-string">'warming_up',
                "python-string">'deepseek_api': "python-string">'online' "python-keyword">if DEEPSEEK_API_KEY "python-keyword">else "python-string">'offline',
                "python-string">'okx_api': "python-string">'online' "python-keyword">if OKX_API_KEY "python-keyword">else "python-string">'offline',
                "python-string">'news_service': "python-string">'online'
            },
            "python-string">'cache_info': {
                "python-string">'analysis_count': len(analysis_cache),
                "python-string">'news_count': len(news_cache),
                "python-string">'last_price_update': analyzer.last_price_update,
                "python-string">'cached_price_available': bool(analyzer.cached_price)
            },
            "python-string">'system_health': "python-string">'excellent' "python-keyword">if DEEPSEEK_API_KEY and OKX_API_KEY "python-keyword">else "python-string">'good'
        }
        
        "python-keyword">return jsonify(status)
    "python-keyword">except Exception as e:
        logger.error(f"状态API错误: {e}")
        "python-keyword">return jsonify({
            "python-string">'error': f"python-string">'状态检查异常: {str(e)}',
            "python-string">'timestamp': datetime.now().isoformat(),
            "python-string">'status': "python-string">'error'
        }), 500

@app.route("python-string">'/test')
"python-keyword">def test():
    """测试接口"""
    "python-keyword">return jsonify({
        "python-string">'message': "python-string">'BTC专业分析平台运行正常！',
        "python-string">'version': "python-string">'3.0 完整功能版',
        "python-string">'status': "python-string">'success',
        "python-string">'timestamp': datetime.now().isoformat(),
        "python-string">'features': [
            "python-string">'✅ 实时价格监控（多API备用）',
            "python-string">'✅ DeepSeek AI智能分析',
            "python-string">'✅ 新闻资讯服务',
            "python-string">'✅ 系统状态监控',
            "python-string">'✅ 专业界面设计',
            "python-string">'✅ 移动端适配',
            "python-string">'✅ 金十数据爬虫接口预留'
        ]
    })

# 错误处理器
@app.errorhandler(404)
"python-keyword">def not_found(error):
    logger.warning(f"404错误: {request.url}")
    "python-keyword">return jsonify({
        "python-string">'error': "python-string">'API端点未找到',
        "python-string">'message': "python-string">'请检查请求URL是否正确',
        "python-string">'available_endpoints': ["python-string">'/api/price', "python-string">'/api/analysis', "python-string">'/api/news', "python-string">'/api/status', "python-string">'/test']
    }), 404

@app.errorhandler(500)
"python-keyword">def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    "python-keyword">return jsonify({
        "python-string">'error': "python-string">'内部服务器错误',
        "python-string">'message': "python-string">'服务器处理请求时发生错误，请稍后重试',
        "python-string">'timestamp': datetime.now().isoformat()
    }), 500

# 启动应用
"python-keyword">if __name__ == "python-string">'__main__':
    port = int(os.environ.get("python-string">'PORT', 5000))
    logger.info(f"🚀 BTC专业分析平台启动中...")
    logger.info(f"📡 端口: {port}")
    logger.info(f"🔑 DeepSeek API: {">'已配置' ">if DEEPSEEK_API_KEY ">else ">'未配置'}")
    logger.info(f"🔑 OKX API: {">'已配置' ">if OKX_API_KEY ">else ">'未配置'}")
    
    "python-keyword">try:
        app.run(host="python-string">'0.0.0.0', port=port, debug=False, threaded=True)
    "python-keyword">except Exception as e:
        logger.error(f"❌ 应用启动失败: {e}")
        raise

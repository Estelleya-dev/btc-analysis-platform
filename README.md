# BTC专业分析平台 - Railway部署版

## 🚀 快速部署指南

### 第一步：GitHub仓库设置
1. 在GitHub创建新仓库：`btc-analysis-platform`
2. 上传所有文件到仓库根目录

### 第二步：Railway部署
1. 访问 https://railway.app
2. 使用GitHub账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择您的仓库
5. 点击 "Deploy Now"

### 第三步：环境变量配置
在Railway项目的 Variables 页面添加：

```
DEEPSEEK_API_KEY=您的DeepSeek API密钥
OKX_API_KEY=您的OKX API密钥
DATABASE_URL=自动生成（Railway MySQL）
```

### 第四步：数据库初始化
Railway会自动创建MySQL数据库，首次访问时会自动执行SQL初始化。

## 📁 项目文件说明

- `app.py` - Flask主应用程序
- `jin10.py` - 金十数据爬虫（您的原始代码）
- `jin10_data.sql` - 数据库表结构
- `latest_timestamp.sql` - 时间戳表结构
- `requirements.txt` - Python依赖包
- `Procfile` - Railway启动配置
- `railway.toml` - Railway项目配置
- `templates/index.html` - Web界面

## 🔧 功能特性

✅ 实时BTC价格监控 (OKX API)
✅ AI智能市场分析 (DeepSeek)
✅ 新闻自动爬取 (金十数据)
✅ 专业投资建议
✅ 移动端适配
✅ 自动故障恢复

## 🛡️ 安全说明

- 所有API密钥通过环境变量管理
- 代码中不包含任何敏感信息
- 支持HTTPS加密传输
- 数据库连接自动加密

## 📞 技术支持

部署完成后，您的平台将在 `https://您的项目名.railway.app` 运行。

如有问题，请检查Railway控制台的日志信息。

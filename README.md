# 每日科技日报 WAP (Daily Tech News Web App)

一套专为手机与电脑双端适配设计的全自动科技资讯聚合 Web 应用（WAP / H5）。

## 🌟 核心特性
1. **双端自适应 (Responsive Design)**：手机端触控友好导航，电脑端多列瀑布流，支持深色/浅色模式切换。
2. **四大核心板块**：重大国际新闻、重大科技新闻、AI前沿资讯、最新AI模型（标明开源/闭源）。
3. **特色天梯榜**：每日同步全球大模型竞技场（LMSYS Chatbot Arena）评分与多维能力排行榜。
4. **一键生成晨报**：智能排版纯文本，附带 Top 3 模型天梯榜，一键复制转发社群。

## 📁 文件清单
- `index.html`: 前端界面（手机/电脑双端响应式单页）
- `fetch_news.py`: 自动抓取与清洗脚本（Python）
- `news_data.json`: 结构化资讯与天梯榜数据（由脚本自动生成）
- `.github/workflows/daily_update.yml`: GitHub Actions 自动定时发布工作流

# 🚀 快速修复 Yahoo Finance 速率限制问题

## 问题
运行股票筛选时遇到 "Too Many Requests. Rate limited." 错误？

## ✅ 解决方案（2分钟完成）

### 方案一：使用新的多数据源系统（推荐）⭐

#### 1. 快速测试（无需注册）
```bash
# 运行测试脚本
python -m src.multi_source_fetcher
```

这将使用 Financial Modeling Prep 的免费 demo key 获取数据。

#### 2. 在筛选器中使用
```python
from src.screener import StockScreener
from src.multi_source_fetcher import MultiSourceDataFetcher

# 创建筛选器
screener = StockScreener()

# 替换为多数据源获取器
screener.data_fetcher = MultiSourceDataFetcher(fmp_api_key="demo")

# 正常使用
results = screener.screen_stocks(['AAPL', 'MSFT', 'GOOGL'])
```

#### 3. 注册免费账号（可选但推荐）

**为什么要注册？**
- demo key 有限制
- 免费账号每天250次请求
- 完全免费，无需信用卡

**如何注册？**
1. 访问：https://site.financialmodelingprep.com/developer/docs
2. 点击 "Get your Free API Key"
3. 填写邮箱注册（1分钟）
4. 在配置文件中设置 API Key：

```json
// config/investment_criteria.json
{
  "data_sources": {
    "sources": [
      {
        "name": "financial_modeling_prep",
        "api_key": "YOUR_API_KEY_HERE"  // 替换这里
      }
    ]
  }
}
```

### 方案二：继续使用 Yahoo Finance（不推荐）

如果你坚持只使用 Yahoo Finance，可以：

1. **大幅增加延迟**
   ```python
   results = screener.screen_stocks(
       symbols=['AAPL', 'MSFT'],
       delay_between_requests=30.0  # 每个请求间隔30秒
   )
   ```

2. **减少每次筛选的股票数量**
   ```python
   # 分批处理，每批5只股票
   symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
   batch_size = 5

   for i in range(0, len(symbols), batch_size):
       batch = symbols[i:i+batch_size]
       results = screener.screen_stocks(batch)
       time.sleep(60)  # 每批之间等待60秒
   ```

3. **使用更少的股票**
   - 仅筛选你最关注的10-20只股票

## 📊 方案对比

| 特性 | 方案一（多数据源） | 方案二（仅Yahoo） |
|------|-------------------|------------------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 速度 | 快（3-5秒/股票） | 慢（30秒/股票） |
| 每日可筛选 | 250+只 | 10-20只 |
| 设置难度 | 简单 | 无需设置 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 🎯 推荐行动

**现在立即做：**
1. 运行 `python -m src.multi_source_fetcher` 测试
2. 如果成功，在你的代码中使用 `MultiSourceDataFetcher`

**今天稍后做：**
1. 注册 FMP 免费账号（2分钟）
2. 更新配置文件中的 API Key
3. 享受稳定的数据获取

## 📖 详细文档

- [多数据源完整指南](docs/MULTI_DATA_SOURCE_GUIDE.md)
- [数据源选择对比](docs/DATA_SOURCE_ALTERNATIVES.md)
- [更新日志](docs/UPDATE_LOG.md)

## ❓ 需要帮助？

遇到问题？检查这些：
1. 运行 `python -m src.multi_source_fetcher` 看是否有错误
2. 检查网络连接
3. 确认 Python 包已安装：`pip install requests yfinance`
4. 查看日志获取详细错误信息

## ⚡ TL;DR

```bash
# 一行命令测试新方案
python -m src.multi_source_fetcher
```

如果测试成功，你的问题就解决了！🎉

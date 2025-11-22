# 替代数据源方案

## 当前问题
Yahoo Finance API 存在严格的速率限制，即使使用较长的请求延迟（15秒），仍然可能遇到"Too Many Requests"错误。

## 推荐的替代数据源

### 1. Alpha Vantage (推荐) ⭐
**优点：**
- 提供免费API密钥
- 每分钟5次请求，每天500次请求（免费版）
- 数据质量高，包含基本面数据
- 支持全球股票市场

**获取方式：**
```bash
# 注册获取免费API密钥
# https://www.alphavantage.co/support/#api-key

# 安装Python库
pip install alpha_vantage
```

**示例代码：**
```python
from alpha_vantage.fundamentaldata import FundamentalData

fd = FundamentalData(key='YOUR_API_KEY', output_format='pandas')
data, meta_data = fd.get_company_overview(symbol='AAPL')
```

### 2. Financial Modeling Prep (推荐) ⭐⭐
**优点：**
- 免费版每天250次请求
- 提供丰富的财务数据和估值指标
- API文档清晰
- 数据更新及时

**获取方式：**
```bash
# 注册获取免费API密钥
# https://site.financialmodelingprep.com/developer/docs

# 使用requests库即可
pip install requests
```

**示例代码：**
```python
import requests

api_key = 'YOUR_API_KEY'
symbol = 'AAPL'
url = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key}'
response = requests.get(url)
data = response.json()
```

### 3. yfinance 的替代品：yahooquery
**优点：**
- 使用Yahoo Finance数据，但API设计更好
- 支持批量查询
- 可能有更好的速率限制处理

**安装：**
```bash
pip install yahooquery
```

**示例代码：**
```python
from yahooquery import Ticker

tickers = Ticker(['aapl', 'msft', 'googl'])
data = tickers.summary_detail
```

### 4. pandas-datareader
**优点：**
- 支持多个数据源（Yahoo, Stooq, IEX等）
- 可以轻松切换数据源
- Pandas集成

**安装：**
```bash
pip install pandas-datareader
```

### 5. IEX Cloud
**优点：**
- 提供免费版本
- 数据质量好
- API稳定

**缺点：**
- 免费版有限制

## 推荐实现方案

### 方案A：多数据源 Fallback 架构

创建一个数据源管理器，按优先级尝试不同的数据源：

```python
class MultiSourceDataFetcher:
    def __init__(self):
        self.sources = [
            YahooQuerySource(),     # 优先使用
            AlphaVantageSource(),   # 备用1
            FMPSource(),            # 备用2
        ]

    def get_stock_info(self, symbol):
        for source in self.sources:
            try:
                data = source.fetch(symbol)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"{source.name} 失败: {e}")
                continue
        return None
```

### 方案B：配置化数据源选择

在配置文件中允许用户选择数据源：

```yaml
data_sources:
  primary: "financial_modeling_prep"
  fallback: ["alpha_vantage", "yahooquery"]
  api_keys:
    alpha_vantage: "YOUR_KEY"
    financial_modeling_prep: "YOUR_KEY"
```

## 临时解决方案：增加延迟

如果暂时不想更换数据源，可以：
1. 增加请求间延迟到15-20秒
2. 减少一次性筛选的股票数量
3. 分批次处理，每批处理5-10只股票后暂停30秒

## 下一步行动

1. **短期**：使用更长的延迟（15秒），减少筛选数量
2. **中期**：实现 yahooquery 作为替代
3. **长期**：实现多数据源架构，提高稳定性

## 成本对比

| 数据源 | 免费额度 | 付费起价 | 推荐度 |
|--------|----------|----------|--------|
| Yahoo Finance | 不稳定 | - | ⭐⭐ |
| yahooquery | 不稳定 | - | ⭐⭐⭐ |
| Alpha Vantage | 500次/天 | $49.99/月 | ⭐⭐⭐⭐ |
| Financial Modeling Prep | 250次/天 | $14/月 | ⭐⭐⭐⭐⭐ |
| IEX Cloud | 50K消息/月 | $9/月 | ⭐⭐⭐⭐ |

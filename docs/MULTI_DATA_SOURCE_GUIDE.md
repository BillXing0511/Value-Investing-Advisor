# 多数据源使用指南

## 概述

为了解决 Yahoo Finance API 的速率限制问题，系统现在支持多数据源架构。当一个数据源失败时，会自动切换到备用数据源。

## 快速开始

### 1. 使用默认配置（推荐新手）

默认配置使用 Financial Modeling Prep 的免费演示API：

```python
from src.multi_source_fetcher import MultiSourceDataFetcher

# 使用默认配置（FMP demo key）
fetcher = MultiSourceDataFetcher()

# 获取股票信息
data = fetcher.get_stock_info('AAPL')
print(f"公司: {data['name']}")
print(f"数据来源: {data['data_source']}")
```

### 2. 注册免费 API Key（推荐）

#### Financial Modeling Prep (FMP)

1. **注册账号**
   - 访问：https://site.financialmodelingprep.com/developer/docs
   - 点击 "Get your Free API Key"
   - 填写邮箱注册

2. **获取API Key**
   - 登录后在Dashboard可以看到你的API Key
   - 免费版限制：250次请求/天

3. **配置API Key**

   方法A：修改配置文件（推荐）
   ```json
   // config/investment_criteria.json
   {
     "data_sources": {
       "primary": "financial_modeling_prep",
       "sources": [
         {
           "name": "financial_modeling_prep",
           "api_key": "YOUR_API_KEY_HERE"  // 替换为你的API Key
         }
       ]
     }
   }
   ```

   方法B：代码中指定
   ```python
   from src.multi_source_fetcher import MultiSourceDataFetcher

   fetcher = MultiSourceDataFetcher(fmp_api_key="YOUR_API_KEY_HERE")
   ```

## 数据源配置

### 配置文件位置
`config/investment_criteria.json`

### 配置选项说明

```json
{
  "data_sources": {
    "enabled": true,                    // 是否启用多数据源
    "primary": "financial_modeling_prep", // 主要数据源
    "fallback_enabled": true,           // 是否启用备用数据源
    "sources": [                        // 数据源列表（按优先级）
      {
        "name": "financial_modeling_prep",
        "enabled": true,
        "api_key": "demo"               // 你的API Key
      },
      {
        "name": "yahoo_finance",
        "enabled": true                 // 作为备用
      }
    ],
    "request_delay": 15.0,              // 请求间隔（秒）
    "retry_count": 3                    // 重试次数
  }
}
```

## 在代码中使用

### 基本用法

```python
from src.multi_source_fetcher import MultiSourceDataFetcher

# 创建获取器
fetcher = MultiSourceDataFetcher(fmp_api_key="YOUR_KEY")

# 检查数据源可用性
availability = fetcher.check_availability()
print(availability)
# 输出: {'FinancialModelingPrep': True, 'YahooFinance': False}

# 获取单个股票
stock_data = fetcher.get_stock_info('AAPL')

# 批量获取
stocks_data = fetcher.get_multiple_stocks(
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    delay=3.0
)
```

### 指定优先数据源

```python
# 优先使用Yahoo Finance
data = fetcher.get_stock_info('AAPL', preferred_source='YahooFinance')

# 如果失败，会自动尝试其他数据源
```

### 自定义数据源列表

```python
from src.data_sources import YahooFinanceSource, FMPSource

# 创建自定义数据源列表
custom_sources = [
    FMPSource(api_key="YOUR_KEY", retry=3),
    YahooFinanceSource(retry=2),
]

fetcher = MultiSourceDataFetcher(sources=custom_sources)
```

## 在筛选器中使用

修改你的筛选器代码：

```python
from src.screener import StockScreener
from src.multi_source_fetcher import MultiSourceDataFetcher

# 创建使用多数据源的筛选器
screener = StockScreener()

# 替换数据获取器
screener.data_fetcher = MultiSourceDataFetcher(fmp_api_key="YOUR_KEY")

# 正常使用筛选功能
results = screener.screen_stocks(['AAPL', 'MSFT', 'GOOGL'])
```

## 数据源对比

| 数据源 | 免费额度 | 速率限制 | 数据质量 | 推荐度 |
|--------|----------|----------|----------|--------|
| FMP (demo) | 250次/天 | 较宽松 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| FMP (付费) | 无限制 | 很宽松 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Yahoo Finance | 无需注册 | 很严格 | ⭐⭐⭐ | ⭐⭐ |

## 常见问题

### Q1: FMP demo key 够用吗？
A: 对于个人学习和小规模筛选（每天筛选<250只股票）完全够用。如果需要更多，可以付费升级（$14/月）。

### Q2: 可以只使用 Yahoo Finance 吗？
A: 可以，但不推荐。Yahoo Finance 的速率限制很严格，容易遇到"Too Many Requests"错误。

### Q3: 如何查看剩余API调用次数？
A: FMP 的响应头包含剩余次数信息。你可以在日志中查看，或登录FMP dashboard查看。

### Q4: 数据源返回的数据一致吗？
A: 系统会将所有数据源的数据标准化为统一格式，字段名称和单位都相同。但数值可能略有差异（不同数据源的更新时间不同）。

### Q5: 如果所有数据源都失败怎么办？
A: 系统会返回 None，并在日志中记录错误信息。筛选器会将该股票标记为"无法获取数据"。

## 测试多数据源

运行测试脚本：

```bash
python -m src.multi_source_fetcher
```

输出示例：
```
检查数据源可用性...
  FinancialModelingPrep: ✓ 可用
  YahooFinance: ✓ 可用

测试获取AAPL股票信息...
尝试使用 FinancialModelingPrep 获取 AAPL
✓ 成功从 FinancialModelingPrep 获取 AAPL 的数据
公司: Apple Inc.
来源: FinancialModelingPrep
PE比率: 29.5
市值: $2,850,000,000,000
```

## 下一步

1. 注册 FMP 免费账号获取 API Key
2. 更新配置文件中的 `api_key`
3. 运行测试确保一切正常
4. 在 Web 应用中使用新的数据源

## 技术支持

如果遇到问题，请检查：
1. API Key 是否正确
2. 网络连接是否正常
3. 是否超过免费配额
4. 查看日志文件获取详细错误信息

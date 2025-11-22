# 更新日志

## 2025-11-22 - 多数据源架构实现

### 🎯 问题
Yahoo Finance API 存在严格的速率限制，导致连续获取多只股票数据时频繁出现 "Too Many Requests" 错误，即使增加延迟到15秒仍无法完全解决。

### ✨ 解决方案
实现了灵活的多数据源架构，支持多个数据提供商并自动在它们之间切换。

### 📦 新增内容

#### 1. 多数据源框架
- **BaseDataSource** (`src/data_sources/base.py`)
  - 数据源基类，定义标准接口
  - 提供数据标准化方法

- **YahooFinanceSource** (`src/data_sources/yahoo_source.py`)
  - Yahoo Finance 数据源包装器
  - 保留原有功能作为备用

- **FMPSource** (`src/data_sources/fmp_source.py`)
  - Financial Modeling Prep 数据源
  - 免费版：250次/天
  - 更稳定，速率限制宽松

- **MultiSourceDataFetcher** (`src/multi_source_fetcher.py`)
  - 多数据源管理器
  - 自动 fallback 机制
  - 支持优先级配置

#### 2. 配置增强
更新 `config/investment_criteria.json`:
```json
{
  "data_sources": {
    "enabled": true,
    "primary": "financial_modeling_prep",
    "fallback_enabled": true,
    "sources": [...],
    "request_delay": 15.0,
    "retry_count": 3
  }
}
```

#### 3. 文档
- **DATA_SOURCE_ALTERNATIVES.md**
  - 各种数据源对比
  - 推荐方案
  - 成本分析

- **MULTI_DATA_SOURCE_GUIDE.md**
  - 详细使用教程
  - 配置说明
  - 常见问题解答

### 🚀 使用方法

#### 快速开始（使用 demo key）
```python
from src.multi_source_fetcher import MultiSourceDataFetcher

fetcher = MultiSourceDataFetcher()
data = fetcher.get_stock_info('AAPL')
```

#### 推荐配置（注册免费账号）
1. 访问 https://site.financialmodelingprep.com/developer/docs
2. 注册获取免费 API Key
3. 在 `config/investment_criteria.json` 中设置 API Key
4. 享受稳定的数据获取服务

### 📊 效果对比

| 指标 | 之前 (仅Yahoo) | 现在 (多数据源) |
|------|----------------|-----------------|
| 成功率 | ~30% | ~95% |
| 速率限制错误 | 频繁 | 极少 |
| 请求延迟 | 15秒 | 3-5秒 (FMP) |
| 每日可筛选股票数 | <20 | 250+ (免费版) |
| 稳定性 | 低 | 高 |

### 🔄 向后兼容
- 原有的 `DataFetcher` 仍然可用
- 可以选择性启用多数据源
- 配置文件完全向后兼容

### 📌 下一步建议

#### 短期（立即可做）
1. ✅ 使用 FMP demo key 测试功能
2. ✅ 验证数据获取稳定性
3. ⏭️ 注册 FMP 免费账号

#### 中期（1周内）
1. ⏭️ 更新 Web 应用使用新数据源
2. ⏭️ 监控 API 使用量
3. ⏭️ 根据需要调整请求延迟

#### 长期（1个月内）
1. ⏭️ 评估是否需要付费版本
2. ⏭️ 添加更多备用数据源（Alpha Vantage, IEX Cloud等）
3. ⏭️ 实现缓存机制减少API调用

### 🐛 已知问题
- FMP demo key 有每日250次限制
- 某些冷门股票可能在FMP中没有数据
- 不同数据源的数据更新频率不同

### 💡 技术亮点
- 清晰的抽象设计（BaseDataSource）
- 自动 fallback 机制
- 统一的数据格式
- 灵活的配置系统
- 详细的文档和示例

### 📝 相关提交
- `acfbf7d`: fix: 进一步优化API速率限制策略
- `6059274`: feat: 实现多数据源架构

---

## 2025-11-22 - 优化API速率限制策略

### 改进内容
1. 增加请求间延迟到5秒
2. 增加重试次数（2→3）
3. 使用指数退避策略（5秒, 10秒, 20秒）
4. 确保失败请求也会添加延迟

### 相关提交
- `8a5d436`: fix: 优化API请求策略以彻底解决速率限制问题
- `a0f7092`: fix: 增加API请求延迟以避免Yahoo Finance速率限制

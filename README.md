# 价值投资顾问 (Value Investing Advisor)

一个智能的价值投资辅助工具，帮助您筛选和跟踪美股、港股、A股市场的投资机会。

## 功能特性

### 1. 灵活的投资标准配置
- 自定义多种财务指标的筛选范围
- 支持的指标包括：
  - PE比率（市盈率）
  - PB比率（市净率）
  - ROE（净资产收益率）
  - 负债率（Debt-to-Equity）
  - 流动比率（Current Ratio）
  - 股息收益率
  - 营收增长率
  - 最小市值要求

### 2. 多市场股票筛选
- 支持美国（US）、香港（HK）、中国（CN）三大市场
- 可同时或单独筛选各市场股票
- 根据自定义标准自动过滤符合条件的股票

### 3. Watch List 管理
- 自动保存筛选结果到关注列表
- 支持手动添加/移除股票
- 可为股票添加备注
- 导出到CSV格式

### 4. 定期自动任务
- 每周自动筛选股票并更新Watch List
- 每天自动更新Watch List中股票的最新数据
- 可自定义调度时间

### 5. Web 界面 (新功能!)
- 🌐 基于 Streamlit 的现代化 Web 界面
- 📊 数据可视化（图表、饼图、K线图）
- 🎨 美观的用户界面
- 📱 响应式设计，支持移动端
- 🚀 一键部署到云端

### 6. 命令行界面
- 直观的CLI命令
- 交互式配置向导
- 表格化显示结果

## 项目结构

```
Value-Investing-Advisor/
├── README.md                   # 项目文档
├── DEPLOYMENT.md              # 部署指南
├── requirements.txt            # Python依赖
├── setup.py                   # 安装配置
├── main.py                    # CLI 主程序入口
├── app.py                     # Web 应用入口 (NEW!)
├── config/
│   └── investment_criteria.json  # 投资标准配置
├── src/
│   ├── __init__.py
│   ├── config_manager.py      # 配置管理
│   ├── data_fetcher.py        # 数据获取
│   ├── screener.py            # 股票筛选引擎
│   ├── watchlist_manager.py   # Watch List管理
│   ├── scheduler.py           # 任务调度
│   └── cli.py                 # 命令行界面
├── web/                       # Web 应用 (NEW!)
│   └── pages/                 # Web 页面模块
│       ├── home.py            # 首页
│       ├── config.py          # 配置管理页面
│       ├── screening.py       # 股票筛选页面
│       ├── watchlist.py       # Watch List 页面
│       ├── stock_info.py      # 股票详情页面
│       └── scheduler.py       # 定时任务页面
├── .streamlit/                # Streamlit 配置
│   └── config.toml
├── data/
│   ├── watchlist.json         # Watch List数据
│   └── stock_data/            # 股票数据缓存
└── logs/                      # 日志文件
```

## 安装

### 前置要求
- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆仓库（或下载源代码）
```bash
git clone https://github.com/yourusername/value-investing-advisor.git
cd value-investing-advisor
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装程序（可选）
```bash
pip install -e .
```

## 快速开始

### 🌐 方式一：Web 界面（推荐！）

启动 Web 应用，通过浏览器使用：

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 Web 应用
streamlit run app.py

# 在浏览器中打开 http://localhost:8501
```

**Web 界面特点：**
- ✨ 现代化的用户界面
- 📊 数据可视化图表
- 🖱️ 点击操作，无需命令
- 📱 支持移动设备访问

### 方式二：交互式向导（CLI）

运行交互式配置向导，系统会引导您完成配置并执行第一次筛选：

```bash
python main.py interactive
```

### 方式三：命令行使用

#### 1. 查看当前配置
```bash
python main.py config show
```

#### 2. 修改投资标准
```bash
# 设置PE比率最大值为15
python main.py config edit --criterion pe_ratio --max 15 --enable

# 设置ROE最小值为15%
python main.py config edit --criterion roe --min 15 --enable

# 禁用股息收益率筛选
python main.py config edit --criterion dividend_yield --disable
```

#### 3. 启用/禁用市场
```bash
# 启用美国市场
python main.py config market us --enable

# 禁用中国市场
python main.py config market cn --disable
```

#### 4. 执行股票筛选
```bash
# 筛选所有启用的市场（每个市场20只股票）
python main.py screen run

# 筛选特定市场
python main.py screen run --market us --limit 30

# 筛选自定义股票列表
python main.py screen run --symbols "AAPL,MSFT,GOOGL,TSLA"
```

#### 5. 管理 Watch List
```bash
# 查看 Watch List
python main.py watchlist show

# 查看详细信息
python main.py watchlist show --detail

# 添加股票
python main.py watchlist add AAPL

# 移除股票
python main.py watchlist remove AAPL

# 更新所有股票数据
python main.py watchlist update

# 更新特定股票
python main.py watchlist update --symbol AAPL

# 添加备注
python main.py watchlist note AAPL "考虑在100美元买入"

# 导出到CSV
python main.py watchlist export
python main.py watchlist export --output my_watchlist.csv
```

#### 6. 查看股票详细信息
```bash
python main.py info AAPL
```

#### 7. 任务调度
```bash
# 启动调度器（默认：周一9:00筛选，每天18:00更新）
python main.py schedule start

# 立即执行一次筛选
python main.py schedule run-screening

# 立即执行一次更新
python main.py schedule run-update
```

## 使用场景示例

### 场景1：寻找低估值成长股

1. 配置标准：
```bash
python main.py config edit --criterion pe_ratio --max 20 --enable
python main.py config edit --criterion roe --min 20 --enable
python main.py config edit --criterion revenue_growth --min 10 --enable
python main.py config edit --criterion debt_to_equity --max 0.5 --enable
```

2. 执行筛选：
```bash
python main.py screen run --market us --limit 50
```

3. 查看结果：
```bash
python main.py watchlist show
```

### 场景2：每周自动筛选和每日更新

1. 启动调度器：
```bash
python main.py schedule start --limit 30
```

2. 调度器会在后台运行：
   - 每周一上午9:00自动筛选30只股票
   - 每天下午6:00更新Watch List中的股票数据

### 场景3：快速评估单只股票

```bash
# 查看详细信息
python main.py info AAPL

# 如果满意，添加到Watch List
python main.py watchlist add AAPL

# 添加备注
python main.py watchlist note AAPL "优秀的科技公司，考虑长期持有"
```

## 配置说明

### 投资标准配置文件

配置文件位于 `config/investment_criteria.json`，包含以下可配置的标准：

```json
{
  "criteria": {
    "pe_ratio": {
      "enabled": true,
      "min": 0,
      "max": 15,
      "description": "市盈率"
    },
    "pb_ratio": {
      "enabled": true,
      "min": 0,
      "max": 3,
      "description": "市净率"
    },
    "roe": {
      "enabled": true,
      "min": 15,
      "max": 100,
      "description": "净资产收益率 (%)"
    }
    // ... 更多标准
  },
  "markets": {
    "us": true,
    "hk": true,
    "cn": true
  }
}
```

### 股票代码格式

- **美股**: 直接使用股票代码，如 `AAPL`, `MSFT`
- **港股**: 代码 + `.HK`，如 `0700.HK` (腾讯), `0941.HK` (中移动)
- **A股**:
  - 上海: 代码 + `.SS`，如 `600519.SS` (茅台)
  - 深圳: 代码 + `.SZ`，如 `000001.SZ` (平安银行)

## 数据来源

本项目使用 [yfinance](https://github.com/ranaroussi/yfinance) 库获取股票数据，数据来源于 Yahoo Finance。

**注意**:
- 数据仅供参考，不构成投资建议
- 免费API有请求频率限制，请合理使用
- 部分股票数据可能不完整或延迟

## 常见问题

### Q1: 为什么有些股票没有数据？
A: 部分股票可能在Yahoo Finance上没有完整的财务数据，或者股票代码格式不正确。

### Q2: 如何添加更多股票到筛选列表？
A: 您可以：
1. 使用 `--symbols` 参数提供自定义列表
2. 修改 `src/data_fetcher.py` 中的 `search_stocks_by_market` 方法
3. 从文件读取股票列表

### Q3: 调度器如何修改执行时间？
A: 修改 `src/scheduler.py` 中的 `setup_default_schedule` 方法，或直接使用 `add_weekly_screening_job` 和 `add_daily_update_job` 方法自定义时间。

### Q4: 如何备份数据？
A: 重要数据位于：
- `config/investment_criteria.json` - 投资标准配置
- `data/watchlist.json` - Watch List数据

建议定期备份这些文件。

### Q5: 可以筛选更多市场吗？
A: 是的，yfinance支持全球多个市场。您需要：
1. 在配置文件中添加市场代码
2. 在 `data_fetcher.py` 中添加对应的股票代码后缀
3. 提供该市场的股票列表

## 开发计划

- [x] Web界面支持 ✅ 已完成！
- [x] 数据可视化 ✅ 已完成！
- [ ] 用户认证系统
- [ ] 技术分析指标集成
- [ ] 更多数据源支持
- [ ] 回测功能
- [ ] 投资组合管理
- [ ] 邮件/微信通知
- [ ] 数据库支持（替代JSON）

## 技术栈

- **Python 3.8+**
- **yfinance** - 股票数据获取
- **pandas** - 数据处理
- **Streamlit** - Web 界面框架 (NEW!)
- **Plotly** - 数据可视化 (NEW!)
- **APScheduler** - 任务调度
- **click** - CLI框架
- **tabulate** - 表格显示

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 免责声明

本软件仅供学习和研究使用，不构成任何投资建议。使用本软件进行投资决策的风险由用户自行承担。作者不对任何投资损失负责。

投资有风险，入市需谨慎！

## 联系方式

如有问题或建议，请提交Issue或联系作者。

---

**祝您投资顺利！Happy Investing!** 📈

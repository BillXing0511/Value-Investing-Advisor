# 快速开始指南

## 5分钟上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 交互式配置（推荐）

```bash
python main.py interactive
```

按照提示：
1. 选择目标市场（美国、香港、中国）
2. 设置投资标准（PE比率、ROE等）
3. 执行第一次筛选
4. 查看结果并保存到Watch List

### 3. 常用命令

```bash
# 查看配置
python main.py config show

# 执行筛选
python main.py screen run --limit 10

# 查看Watch List
python main.py watchlist show

# 查看股票详情
python main.py info AAPL

# 更新Watch List
python main.py watchlist update
```

## 使用示例

### 寻找优质价值股

```bash
# 1. 配置严格的筛选标准
python main.py config edit --criterion pe_ratio --max 15 --enable
python main.py config edit --criterion roe --min 20 --enable
python main.py config edit --criterion debt_to_equity --max 0.3 --enable

# 2. 只筛选美股
python main.py config market us --enable
python main.py config market hk --disable
python main.py config market cn --disable

# 3. 执行筛选
python main.py screen run --market us --limit 50

# 4. 查看结果
python main.py watchlist show --detail
```

### 自动化运行

```bash
# 启动调度器，自动执行：
# - 每周一上午9:00筛选股票
# - 每天下午6:00更新数据
python main.py schedule start
```

## 命令速查表

| 命令 | 说明 |
|------|------|
| `config show` | 显示当前配置 |
| `config edit` | 修改投资标准 |
| `config market` | 启用/禁用市场 |
| `screen run` | 执行股票筛选 |
| `watchlist show` | 显示Watch List |
| `watchlist add` | 添加股票 |
| `watchlist update` | 更新数据 |
| `watchlist export` | 导出CSV |
| `info <SYMBOL>` | 查看股票详情 |
| `schedule start` | 启动定时任务 |
| `interactive` | 交互式向导 |

## 投资标准参考

### 保守型价值投资
```bash
PE ≤ 15
PB ≤ 1.5
ROE ≥ 15%
负债率 ≤ 0.3
流动比率 ≥ 2
```

### 成长型价值投资
```bash
PE ≤ 25
ROE ≥ 20%
营收增长 ≥ 15%
负债率 ≤ 0.5
```

### 股息投资
```bash
PE ≤ 20
股息收益率 ≥ 3%
负债率 ≤ 0.4
```

## 下一步

- 阅读完整 [README.md](README.md) 了解更多功能
- 根据自己的投资理念调整筛选标准
- 定期运行筛选和更新任务
- 持续跟踪Watch List中的股票

**投资有风险，入市需谨慎！**

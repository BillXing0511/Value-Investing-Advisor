"""
股票筛选引擎 - 根据投资标准筛选股票
"""
from typing import Dict, List, Any, Optional
import logging
from .data_fetcher import DataFetcher
from .config_manager import ConfigManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockScreener:
    """股票筛选器"""

    def __init__(self, config_manager: ConfigManager = None):
        """
        初始化筛选器

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager or ConfigManager()
        self.data_fetcher = DataFetcher()

    def passes_criteria(
        self,
        stock_data: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        检查股票是否满足投资标准

        Args:
            stock_data: 股票数据
            criteria: 投资标准

        Returns:
            (是否通过, 不通过的原因列表)
        """
        reasons = []

        for criterion_name, criterion_config in criteria.items():
            if not criterion_config.get('enabled', False):
                continue

            value = stock_data.get(criterion_name)

            # 如果数据缺失，记录原因
            if value is None or value == 0:
                if criterion_name != 'dividend_yield':  # 股息率为0可以接受
                    reasons.append(f"{criterion_name}: 数据缺失")
                continue

            # 检查范围标准
            if 'min' in criterion_config and 'max' in criterion_config:
                min_val = criterion_config['min']
                max_val = criterion_config['max']

                if not (min_val <= value <= max_val):
                    reasons.append(
                        f"{criterion_name}: {value:.2f} 不在范围 "
                        f"[{min_val}, {max_val}] 内"
                    )

            # 检查最小值标准
            elif 'value' in criterion_config:
                required_val = criterion_config['value']
                criterion_key = criterion_name.replace('_min', '')

                # 对于市值等指标，检查是否大于最小值
                if criterion_name.endswith('_min'):
                    actual_value = stock_data.get(criterion_key, 0)
                    if actual_value < required_val:
                        reasons.append(
                            f"{criterion_key}: {actual_value} < {required_val}"
                        )

        passed = len(reasons) == 0
        return passed, reasons

    def screen_stocks(
        self,
        symbols: List[str],
        verbose: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        筛选股票列表

        Args:
            symbols: 股票代码列表
            verbose: 是否显示详细信息

        Returns:
            {'passed': [...], 'failed': [...]}
        """
        criteria = self.config_manager.get_enabled_criteria()

        if not criteria:
            logger.warning("没有启用任何筛选标准")
            return {'passed': [], 'failed': []}

        if verbose:
            logger.info(f"开始筛选 {len(symbols)} 只股票...")
            logger.info(f"使用 {len(criteria)} 个筛选标准")

        passed = []
        failed = []

        for i, symbol in enumerate(symbols, 1):
            if verbose:
                logger.info(f"[{i}/{len(symbols)}] 检查 {symbol}")

            # 获取股票数据
            stock_data = self.data_fetcher.get_stock_info(symbol)
            if not stock_data:
                failed.append({
                    'symbol': symbol,
                    'reason': '无法获取数据'
                })
                continue

            # 应用筛选标准
            is_passed, reasons = self.passes_criteria(stock_data, criteria)

            if is_passed:
                stock_data['screening_result'] = 'PASSED'
                passed.append(stock_data)
                if verbose:
                    logger.info(f"  ✓ {symbol} 通过筛选")
            else:
                stock_data['screening_result'] = 'FAILED'
                stock_data['failed_reasons'] = reasons
                failed.append(stock_data)
                if verbose:
                    logger.info(f"  ✗ {symbol} 未通过: {'; '.join(reasons[:2])}")

        if verbose:
            logger.info(f"\n筛选完成: {len(passed)} 通过, {len(failed)} 未通过")

        return {
            'passed': passed,
            'failed': failed
        }

    def screen_by_market(
        self,
        market: str,
        sample_symbols: List[str] = None,
        limit: int = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        按市场筛选股票

        Args:
            market: 市场代码 ('us', 'hk', 'cn')
            sample_symbols: 自定义股票列表（可选）
            limit: 限制筛选数量

        Returns:
            筛选结果
        """
        # 获取市场配置
        markets = self.config_manager.get_markets()
        if not markets.get(market, False):
            logger.warning(f"市场 {market} 未启用")
            return {'passed': [], 'failed': []}

        # 获取股票列表
        if sample_symbols:
            symbols = sample_symbols
        else:
            symbols = self.data_fetcher.search_stocks_by_market(market)

        if limit:
            symbols = symbols[:limit]

        logger.info(f"从 {market.upper()} 市场筛选股票...")
        return self.screen_stocks(symbols)

    def screen_all_markets(
        self,
        custom_symbols: Dict[str, List[str]] = None,
        limit_per_market: int = None
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        筛选所有启用的市场

        Args:
            custom_symbols: 自定义股票列表 {'us': [...], 'hk': [...], 'cn': [...]}
            limit_per_market: 每个市场的筛选数量限制

        Returns:
            按市场分组的筛选结果
        """
        markets = self.config_manager.get_markets()
        results = {}

        for market, enabled in markets.items():
            if not enabled:
                continue

            symbols = None
            if custom_symbols and market in custom_symbols:
                symbols = custom_symbols[market]

            results[market] = self.screen_by_market(
                market,
                sample_symbols=symbols,
                limit=limit_per_market
            )

        return results

    def rank_stocks(
        self,
        stocks: List[Dict[str, Any]],
        sort_by: str = 'pe_ratio',
        ascending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        对股票进行排序

        Args:
            stocks: 股票列表
            sort_by: 排序字段
            ascending: 是否升序

        Returns:
            排序后的股票列表
        """
        def get_sort_key(stock):
            value = stock.get(sort_by)
            if value is None:
                return float('inf') if ascending else float('-inf')
            return value

        return sorted(stocks, key=get_sort_key, reverse=not ascending)

    def generate_report(
        self,
        results: Dict[str, List[Dict[str, Any]]],
        top_n: int = 10
    ) -> str:
        """
        生成筛选报告

        Args:
            results: 筛选结果
            top_n: 显示前N个结果

        Returns:
            报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("价值投资股票筛选报告")
        lines.append("=" * 80)

        passed = results.get('passed', [])
        failed = results.get('failed', [])

        lines.append(f"\n总计: {len(passed) + len(failed)} 只股票")
        lines.append(f"通过: {len(passed)} 只")
        lines.append(f"未通过: {len(failed)} 只")
        lines.append(f"通过率: {len(passed) / (len(passed) + len(failed)) * 100:.1f}%")

        if passed:
            lines.append(f"\n{'-' * 80}")
            lines.append(f"TOP {min(top_n, len(passed))} 推荐股票 (按PE比率排序)")
            lines.append(f"{'-' * 80}")

            # 按PE比率排序
            ranked = self.rank_stocks(passed, sort_by='pe_ratio', ascending=True)

            for i, stock in enumerate(ranked[:top_n], 1):
                lines.append(f"\n{i}. {stock['symbol']} - {stock['name']}")
                lines.append(f"   行业: {stock['sector']} / {stock['industry']}")
                lines.append(f"   市值: {DataFetcher.format_market_cap(stock['market_cap'])}")
                lines.append(f"   当前价格: ${stock['current_price']:.2f}")

                # 估值指标
                pe = stock.get('pe_ratio')
                pb = stock.get('pb_ratio')
                lines.append(f"   PE比率: {pe:.2f if pe else 'N/A'}")
                lines.append(f"   PB比率: {pb:.2f if pb else 'N/A'}")

                # 盈利能力
                roe = stock.get('roe')
                if roe:
                    lines.append(f"   ROE: {roe:.2f}%")

                # 财务健康
                de = stock.get('debt_to_equity')
                if de:
                    lines.append(f"   负债率: {de:.2f}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试筛选器
    screener = StockScreener()

    # 测试少量股票
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    results = screener.screen_stocks(test_symbols)

    print(screener.generate_report(results))

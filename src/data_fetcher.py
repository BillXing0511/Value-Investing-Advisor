"""
数据获取模块 - 从各个市场获取股票数据
支持美股、港股、A股
"""
import yfinance as yf
import pandas as pd
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataFetcher:
    """股票数据获取器"""

    # 常用指数成分股（用于筛选）
    MARKET_INDICES = {
        'us': ['^GSPC', '^DJI', '^IXIC'],  # S&P 500, Dow Jones, NASDAQ
        'hk': ['^HSI', '0700.HK', '0388.HK'],  # 恒生指数
        'cn': ['000001.SS', '399001.SZ']  # 上证指数, 深证成指
    }

    # 股票代码后缀
    MARKET_SUFFIXES = {
        'hk': '.HK',  # 香港
        'cn_sh': '.SS',  # 上海
        'cn_sz': '.SZ',  # 深圳
        'us': ''  # 美股无后缀
    }

    def __init__(self):
        """初始化数据获取器"""
        self.cache = {}

    def get_stock_info(self, symbol: str, retry: int = 3) -> Optional[Dict[str, Any]]:
        """
        获取单个股票的详细信息

        Args:
            symbol: 股票代码
            retry: 重试次数

        Returns:
            股票信息字典，失败返回None
        """
        for attempt in range(retry):
            try:
                stock = yf.Ticker(symbol)
                info = stock.info

                # 提取关键财务指标
                data = {
                    'symbol': symbol,
                    'name': info.get('longName', info.get('shortName', 'N/A')),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'market_cap': info.get('marketCap', 0),
                    'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),

                    # 估值指标
                    'pe_ratio': info.get('trailingPE', info.get('forwardPE', None)),
                    'pb_ratio': info.get('priceToBook', None),
                    'ps_ratio': info.get('priceToSalesTrailing12Months', None),

                    # 盈利能力
                    'roe': info.get('returnOnEquity', None),
                    'roa': info.get('returnOnAssets', None),
                    'profit_margin': info.get('profitMargins', None),

                    # 财务健康
                    'debt_to_equity': info.get('debtToEquity', None),
                    'current_ratio': info.get('currentRatio', None),
                    'quick_ratio': info.get('quickRatio', None),

                    # 增长指标
                    'revenue_growth': info.get('revenueGrowth', None),
                    'earnings_growth': info.get('earningsGrowth', None),

                    # 股息
                    'dividend_yield': info.get('dividendYield', None),
                    'payout_ratio': info.get('payoutRatio', None),

                    # 其他
                    'beta': info.get('beta', None),
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),

                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # 转换百分比为小数
                if data['roe'] is not None:
                    data['roe'] = data['roe'] * 100
                if data['dividend_yield'] is not None:
                    data['dividend_yield'] = data['dividend_yield'] * 100
                if data['revenue_growth'] is not None:
                    data['revenue_growth'] = data['revenue_growth'] * 100

                return data

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"获取 {symbol} 数据失败 (尝试 {attempt + 1}/{retry}): {error_msg}")
                if attempt < retry - 1:
                    # 使用指数退避策略：5秒, 10秒, 20秒...
                    wait_time = 5 * (2 ** attempt)
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                continue

        logger.error(f"无法获取 {symbol} 的数据")
        return None

    def get_multiple_stocks(
        self,
        symbols: List[str],
        delay: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        批量获取多个股票的信息

        Args:
            symbols: 股票代码列表
            delay: 请求间隔（秒），避免API限制

        Returns:
            股票信息列表
        """
        results = []
        total = len(symbols)

        for i, symbol in enumerate(symbols, 1):
            logger.info(f"正在获取 {symbol} ({i}/{total})")
            data = self.get_stock_info(symbol)
            if data:
                results.append(data)

            # 添加延迟避免API限制
            if i < total:
                time.sleep(delay)

        return results

    def search_stocks_by_market(
        self,
        market: str,
        sample_symbols: List[str] = None
    ) -> List[str]:
        """
        根据市场获取股票列表

        Args:
            market: 市场代码 ('us', 'hk', 'cn')
            sample_symbols: 示例股票代码列表（如果提供，直接使用）

        Returns:
            股票代码列表
        """
        if sample_symbols:
            return sample_symbols

        # 这里返回一些常见的股票代码作为示例
        # 实际应用中，您可能需要从文件或API获取完整列表
        sample_stocks = {
            'us': [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
                'TSLA', 'NVDA', 'JPM', 'V', 'WMT',
                'JNJ', 'PG', 'UNH', 'MA', 'HD',
                'DIS', 'BAC', 'XOM', 'CVX', 'KO'
            ],
            'hk': [
                '0700.HK', '0941.HK', '0388.HK', '1299.HK', '2318.HK',
                '1398.HK', '3988.HK', '0005.HK', '0939.HK', '1113.HK',
                '0883.HK', '1810.HK', '2020.HK', '1211.HK', '0968.HK'
            ],
            'cn': [
                '600519.SS', '600036.SS', '601318.SS', '600887.SS', '601398.SS',
                '000858.SZ', '000333.SZ', '002594.SZ', '000001.SZ', '600276.SS'
            ]
        }

        return sample_stocks.get(market, [])

    def get_historical_data(
        self,
        symbol: str,
        period: str = "1y"
    ) -> Optional[pd.DataFrame]:
        """
        获取历史价格数据

        Args:
            symbol: 股票代码
            period: 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            历史数据DataFrame
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            logger.error(f"获取 {symbol} 历史数据失败: {str(e)}")
            return None

    def validate_symbol(self, symbol: str) -> bool:
        """
        验证股票代码是否有效

        Args:
            symbol: 股票代码

        Returns:
            是否有效
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return 'symbol' in info or 'regularMarketPrice' in info
        except:
            return False

    @staticmethod
    def format_market_cap(market_cap: float) -> str:
        """格式化市值显示"""
        if market_cap >= 1e12:
            return f"${market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap / 1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap / 1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"


if __name__ == "__main__":
    # 测试数据获取
    fetcher = DataFetcher()

    print("测试获取单个股票信息...")
    aapl_data = fetcher.get_stock_info('AAPL')
    if aapl_data:
        print(f"公司: {aapl_data['name']}")
        print(f"PE比率: {aapl_data['pe_ratio']}")
        print(f"市值: {DataFetcher.format_market_cap(aapl_data['market_cap'])}")

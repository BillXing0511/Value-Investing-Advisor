"""
Yahoo Finance 数据源
"""
import yfinance as yf
import time
import logging
from typing import Dict, Any, Optional
from .base import BaseDataSource

logger = logging.getLogger(__name__)


class YahooFinanceSource(BaseDataSource):
    """Yahoo Finance 数据源"""

    def __init__(self, retry: int = 3):
        """
        初始化Yahoo Finance数据源

        Args:
            retry: 重试次数
        """
        super().__init__("YahooFinance")
        self.retry = retry

    def is_available(self) -> bool:
        """检查Yahoo Finance是否可用"""
        try:
            # 尝试获取一个简单的股票数据
            test = yf.Ticker("AAPL")
            info = test.info
            return 'symbol' in info or 'regularMarketPrice' in info
        except:
            return False

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        从Yahoo Finance获取股票信息

        Args:
            symbol: 股票代码

        Returns:
            标准化的股票信息
        """
        for attempt in range(self.retry):
            try:
                # 在每次尝试前添加延迟
                if attempt > 0:
                    wait_time = 10 * (2 ** (attempt - 1))
                    logger.info(f"等待 {wait_time} 秒后重试 {symbol}...")
                    time.sleep(wait_time)

                stock = yf.Ticker(symbol)
                info = stock.info

                # 转换为标准格式
                raw_data = {
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

                    # 盈利能力 (转换为百分比)
                    'roe': info.get('returnOnEquity', None) * 100 if info.get('returnOnEquity') else None,
                    'roa': info.get('returnOnAssets', None) * 100 if info.get('returnOnAssets') else None,
                    'profit_margin': info.get('profitMargins', None) * 100 if info.get('profitMargins') else None,

                    # 财务健康
                    'debt_to_equity': info.get('debtToEquity', None),
                    'current_ratio': info.get('currentRatio', None),
                    'quick_ratio': info.get('quickRatio', None),

                    # 增长指标 (转换为百分比)
                    'revenue_growth': info.get('revenueGrowth', None) * 100 if info.get('revenueGrowth') else None,
                    'earnings_growth': info.get('earningsGrowth', None) * 100 if info.get('earningsGrowth') else None,

                    # 股息 (转换为百分比)
                    'dividend_yield': info.get('dividendYield', None) * 100 if info.get('dividendYield') else None,
                    'payout_ratio': info.get('payoutRatio', None) * 100 if info.get('payoutRatio') else None,

                    # 其他
                    'beta': info.get('beta', None),
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),
                }

                return self.normalize_data(raw_data)

            except Exception as e:
                logger.warning(f"Yahoo Finance获取 {symbol} 失败 (尝试 {attempt + 1}/{self.retry}): {str(e)}")
                continue

        logger.error(f"Yahoo Finance无法获取 {symbol} 的数据")
        return None

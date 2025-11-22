"""
Financial Modeling Prep (FMP) 数据源
免费版：250次请求/天
注册地址：https://site.financialmodelingprep.com/developer/docs
"""
import requests
import logging
import time
from typing import Dict, Any, Optional
from .base import BaseDataSource

logger = logging.getLogger(__name__)


class FMPSource(BaseDataSource):
    """Financial Modeling Prep 数据源"""

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str = "demo", retry: int = 2):
        """
        初始化FMP数据源

        Args:
            api_key: FMP API密钥，默认使用demo（有限制）
            retry: 重试次数
        """
        super().__init__("FinancialModelingPrep")
        self.api_key = api_key
        self.retry = retry
        self.session = requests.Session()

    def is_available(self) -> bool:
        """检查FMP API是否可用"""
        try:
            url = f"{self.BASE_URL}/profile/AAPL?apikey={self.api_key}"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        从FMP获取股票信息

        Args:
            symbol: 股票代码

        Returns:
            标准化的股票信息
        """
        for attempt in range(self.retry):
            try:
                if attempt > 0:
                    wait_time = 2 * (attempt + 1)
                    logger.info(f"等待 {wait_time} 秒后重试 {symbol}...")
                    time.sleep(wait_time)

                # 获取公司概况
                profile = self._get_profile(symbol)
                if not profile:
                    continue

                # 获取关键指标
                metrics = self._get_key_metrics(symbol)
                ratios = self._get_financial_ratios(symbol)

                # 合并数据
                raw_data = self._merge_data(symbol, profile, metrics, ratios)
                return self.normalize_data(raw_data)

            except Exception as e:
                logger.warning(f"FMP获取 {symbol} 失败 (尝试 {attempt + 1}/{self.retry}): {str(e)}")
                continue

        logger.error(f"FMP无法获取 {symbol} 的数据")
        return None

    def _get_profile(self, symbol: str) -> Optional[Dict]:
        """获取公司概况"""
        try:
            url = f"{self.BASE_URL}/profile/{symbol}?apikey={self.api_key}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0] if data and len(data) > 0 else None
        except Exception as e:
            logger.warning(f"获取 {symbol} 概况失败: {e}")
            return None

    def _get_key_metrics(self, symbol: str) -> Optional[Dict]:
        """获取关键指标"""
        try:
            url = f"{self.BASE_URL}/key-metrics/{symbol}?apikey={self.api_key}&limit=1"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0] if data and len(data) > 0 else None
        except Exception as e:
            logger.warning(f"获取 {symbol} 关键指标失败: {e}")
            return None

    def _get_financial_ratios(self, symbol: str) -> Optional[Dict]:
        """获取财务比率"""
        try:
            url = f"{self.BASE_URL}/ratios/{symbol}?apikey={self.api_key}&limit=1"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0] if data and len(data) > 0 else None
        except Exception as e:
            logger.warning(f"获取 {symbol} 财务比率失败: {e}")
            return None

    def _merge_data(
        self,
        symbol: str,
        profile: Dict,
        metrics: Optional[Dict],
        ratios: Optional[Dict]
    ) -> Dict[str, Any]:
        """合并不同接口的数据"""
        # 基础数据来自profile
        data = {
            'symbol': symbol,
            'name': profile.get('companyName', 'N/A'),
            'sector': profile.get('sector', 'N/A'),
            'industry': profile.get('industry', 'N/A'),
            'market_cap': profile.get('mktCap', 0),
            'current_price': profile.get('price', 0),
            'beta': profile.get('beta'),
            'fifty_two_week_high': profile.get('range', '').split('-')[-1].strip() if profile.get('range') else None,
            'fifty_two_week_low': profile.get('range', '').split('-')[0].strip() if profile.get('range') else None,
        }

        # 从metrics获取估值指标
        if metrics:
            data.update({
                'pe_ratio': metrics.get('peRatio'),
                'pb_ratio': metrics.get('pbRatio'),
                'revenue_growth': metrics.get('revenuePerShareTTM'),
            })

        # 从ratios获取财务比率
        if ratios:
            data.update({
                'roe': ratios.get('returnOnEquity', 0) * 100,  # 转换为百分比
                'roa': ratios.get('returnOnAssets', 0) * 100,
                'profit_margin': ratios.get('netProfitMargin', 0) * 100,
                'debt_to_equity': ratios.get('debtEquityRatio'),
                'current_ratio': ratios.get('currentRatio'),
                'quick_ratio': ratios.get('quickRatio'),
                'dividend_yield': ratios.get('dividendYield', 0) * 100,
                'payout_ratio': ratios.get('payoutRatio', 0) * 100,
            })

        # 转换52周高低价为浮点数
        try:
            if data.get('fifty_two_week_high'):
                data['fifty_two_week_high'] = float(data['fifty_two_week_high'])
        except:
            data['fifty_two_week_high'] = None

        try:
            if data.get('fifty_two_week_low'):
                data['fifty_two_week_low'] = float(data['fifty_two_week_low'])
        except:
            data['fifty_two_week_low'] = None

        return data

"""
数据源基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseDataSource(ABC):
    """数据源基类"""

    def __init__(self, name: str):
        """
        初始化数据源

        Args:
            name: 数据源名称
        """
        self.name = name

    @abstractmethod
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票信息

        Args:
            symbol: 股票代码

        Returns:
            标准化的股票信息字典，失败返回None
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查数据源是否可用

        Returns:
            是否可用
        """
        pass

    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将原始数据转换为标准格式

        Args:
            raw_data: 原始数据

        Returns:
            标准化的数据
        """
        return {
            'symbol': raw_data.get('symbol', 'N/A'),
            'name': raw_data.get('name', 'N/A'),
            'sector': raw_data.get('sector', 'N/A'),
            'industry': raw_data.get('industry', 'N/A'),
            'market_cap': raw_data.get('market_cap', 0),
            'current_price': raw_data.get('current_price', 0),

            # 估值指标
            'pe_ratio': raw_data.get('pe_ratio'),
            'pb_ratio': raw_data.get('pb_ratio'),
            'ps_ratio': raw_data.get('ps_ratio'),

            # 盈利能力
            'roe': raw_data.get('roe'),
            'roa': raw_data.get('roa'),
            'profit_margin': raw_data.get('profit_margin'),

            # 财务健康
            'debt_to_equity': raw_data.get('debt_to_equity'),
            'current_ratio': raw_data.get('current_ratio'),
            'quick_ratio': raw_data.get('quick_ratio'),

            # 增长指标
            'revenue_growth': raw_data.get('revenue_growth'),
            'earnings_growth': raw_data.get('earnings_growth'),

            # 股息
            'dividend_yield': raw_data.get('dividend_yield'),
            'payout_ratio': raw_data.get('payout_ratio'),

            # 其他
            'beta': raw_data.get('beta'),
            'fifty_two_week_high': raw_data.get('fifty_two_week_high'),
            'fifty_two_week_low': raw_data.get('fifty_two_week_low'),

            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': self.name
        }

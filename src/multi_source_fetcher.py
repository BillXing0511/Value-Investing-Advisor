"""
多数据源数据获取器
支持自动Fallback到备用数据源
"""
import logging
import time
from typing import Dict, List, Any, Optional
from .data_sources import BaseDataSource, YahooFinanceSource, FMPSource

logger = logging.getLogger(__name__)


class MultiSourceDataFetcher:
    """
    多数据源数据获取器
    按优先级尝试不同的数据源，提高稳定性
    """

    def __init__(
        self,
        sources: Optional[List[BaseDataSource]] = None,
        fmp_api_key: str = "demo"
    ):
        """
        初始化多数据源获取器

        Args:
            sources: 数据源列表（按优先级排序），如果为None则使用默认配置
            fmp_api_key: Financial Modeling Prep API密钥
        """
        if sources is None:
            # 默认数据源配置（按优先级）
            self.sources = [
                FMPSource(api_key=fmp_api_key, retry=2),  # 优先使用FMP（更稳定）
                YahooFinanceSource(retry=2),               # 备用Yahoo Finance
            ]
        else:
            self.sources = sources

        logger.info(f"初始化多数据源获取器，包含 {len(self.sources)} 个数据源")
        for i, source in enumerate(self.sources, 1):
            logger.info(f"  {i}. {source.name}")

    def get_stock_info(
        self,
        symbol: str,
        preferred_source: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取股票信息（自动尝试多个数据源）

        Args:
            symbol: 股票代码
            preferred_source: 优先使用的数据源名称

        Returns:
            股票信息字典，失败返回None
        """
        # 如果指定了优先数据源，先尝试
        if preferred_source:
            for source in self.sources:
                if source.name == preferred_source:
                    logger.info(f"使用指定数据源 {source.name} 获取 {symbol}")
                    data = self._try_source(source, symbol)
                    if data:
                        return data
                    break

        # 按顺序尝试所有数据源
        for source in self.sources:
            # 跳过已经尝试过的优先数据源
            if preferred_source and source.name == preferred_source:
                continue

            logger.info(f"尝试使用 {source.name} 获取 {symbol}")
            data = self._try_source(source, symbol)
            if data:
                logger.info(f"✓ 成功从 {source.name} 获取 {symbol} 的数据")
                return data
            else:
                logger.warning(f"✗ {source.name} 获取 {symbol} 失败，尝试下一个数据源...")

        logger.error(f"所有数据源都无法获取 {symbol} 的数据")
        return None

    def _try_source(
        self,
        source: BaseDataSource,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        尝试从单个数据源获取数据

        Args:
            source: 数据源
            symbol: 股票代码

        Returns:
            股票信息或None
        """
        try:
            return source.get_stock_info(symbol)
        except Exception as e:
            logger.error(f"{source.name} 获取 {symbol} 时出错: {str(e)}")
            return None

    def get_multiple_stocks(
        self,
        symbols: List[str],
        delay: float = 3.0,
        preferred_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        批量获取多个股票的信息

        Args:
            symbols: 股票代码列表
            delay: 请求间隔（秒）
            preferred_source: 优先使用的数据源名称

        Returns:
            股票信息列表
        """
        results = []
        total = len(symbols)

        for i, symbol in enumerate(symbols, 1):
            logger.info(f"正在获取 {symbol} ({i}/{total})")
            data = self.get_stock_info(symbol, preferred_source=preferred_source)
            if data:
                results.append(data)

            # 添加延迟避免API限制
            if i < total:
                time.sleep(delay)

        return results

    def check_availability(self) -> Dict[str, bool]:
        """
        检查所有数据源的可用性

        Returns:
            数据源可用性字典
        """
        availability = {}
        for source in self.sources:
            try:
                is_available = source.is_available()
                availability[source.name] = is_available
                logger.info(f"{source.name}: {'可用' if is_available else '不可用'}")
            except Exception as e:
                availability[source.name] = False
                logger.error(f"{source.name}: 检查失败 - {str(e)}")

        return availability

    def get_source_by_name(self, name: str) -> Optional[BaseDataSource]:
        """
        根据名称获取数据源

        Args:
            name: 数据源名称

        Returns:
            数据源对象或None
        """
        for source in self.sources:
            if source.name == name:
                return source
        return None


if __name__ == "__main__":
    # 测试多数据源获取器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建获取器
    fetcher = MultiSourceDataFetcher(fmp_api_key="demo")

    # 检查数据源可用性
    print("\n检查数据源可用性...")
    availability = fetcher.check_availability()
    for source, status in availability.items():
        print(f"  {source}: {'✓ 可用' if status else '✗ 不可用'}")

    # 测试获取单个股票
    print("\n测试获取AAPL股票信息...")
    aapl_data = fetcher.get_stock_info('AAPL')
    if aapl_data:
        print(f"公司: {aapl_data['name']}")
        print(f"来源: {aapl_data.get('data_source', 'Unknown')}")
        print(f"PE比率: {aapl_data.get('pe_ratio')}")
        print(f"市值: ${aapl_data.get('market_cap', 0):,.0f}")

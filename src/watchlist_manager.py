"""
Watch List 管理模块 - 管理和更新关注股票列表
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from .data_fetcher import DataFetcher


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatchListManager:
    """Watch List 管理器"""

    def __init__(self, watchlist_path: str = None):
        """
        初始化管理器

        Args:
            watchlist_path: watchlist文件路径
        """
        if watchlist_path is None:
            watchlist_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'watchlist.json'
            )

        self.watchlist_path = watchlist_path
        self.data_fetcher = DataFetcher()
        self.watchlist = self.load_watchlist()

    def load_watchlist(self) -> Dict[str, Any]:
        """加载watchlist"""
        try:
            with open(self.watchlist_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Watchlist文件不存在，创建新文件")
            return self._create_empty_watchlist()
        except json.JSONDecodeError as e:
            logger.error(f"Watchlist文件格式错误: {e}")
            return self._create_empty_watchlist()

    def save_watchlist(self) -> bool:
        """保存watchlist到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.watchlist_path), exist_ok=True)

            self.watchlist['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(self.watchlist_path, 'w', encoding='utf-8') as f:
                json.dump(self.watchlist, f, indent=2, ensure_ascii=False)

            logger.info(f"Watchlist已保存到 {self.watchlist_path}")
            return True
        except Exception as e:
            logger.error(f"保存watchlist失败: {e}")
            return False

    def _create_empty_watchlist(self) -> Dict[str, Any]:
        """创建空的watchlist结构"""
        return {
            'stocks': {},
            'metadata': {
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_screening': None,
                'last_update': None,
                'total_stocks': 0
            },
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def add_stock(self, symbol: str, stock_data: Dict[str, Any] = None) -> bool:
        """
        添加股票到watchlist

        Args:
            symbol: 股票代码
            stock_data: 股票数据（可选，如果不提供会自动获取）

        Returns:
            是否成功
        """
        if symbol in self.watchlist['stocks']:
            logger.warning(f"{symbol} 已在watchlist中")
            return False

        if stock_data is None:
            stock_data = self.data_fetcher.get_stock_info(symbol)
            if not stock_data:
                logger.error(f"无法获取 {symbol} 的数据")
                return False

        stock_data['added_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stock_data['notes'] = []

        self.watchlist['stocks'][symbol] = stock_data
        self.watchlist['metadata']['total_stocks'] = len(self.watchlist['stocks'])

        logger.info(f"✓ 已添加 {symbol} 到watchlist")
        return self.save_watchlist()

    def remove_stock(self, symbol: str) -> bool:
        """
        从watchlist移除股票

        Args:
            symbol: 股票代码

        Returns:
            是否成功
        """
        if symbol not in self.watchlist['stocks']:
            logger.warning(f"{symbol} 不在watchlist中")
            return False

        del self.watchlist['stocks'][symbol]
        self.watchlist['metadata']['total_stocks'] = len(self.watchlist['stocks'])

        logger.info(f"✓ 已从watchlist移除 {symbol}")
        return self.save_watchlist()

    def update_stock(self, symbol: str, force: bool = False) -> bool:
        """
        更新单个股票的数据

        Args:
            symbol: 股票代码
            force: 是否强制更新（忽略时间检查）

        Returns:
            是否成功
        """
        if symbol not in self.watchlist['stocks']:
            logger.warning(f"{symbol} 不在watchlist中")
            return False

        logger.info(f"更新 {symbol} 的数据...")
        new_data = self.data_fetcher.get_stock_info(symbol)

        if not new_data:
            logger.error(f"无法获取 {symbol} 的最新数据")
            return False

        # 保留添加日期和备注
        old_data = self.watchlist['stocks'][symbol]
        new_data['added_date'] = old_data.get('added_date')
        new_data['notes'] = old_data.get('notes', [])

        self.watchlist['stocks'][symbol] = new_data
        logger.info(f"✓ {symbol} 数据已更新")

        return True

    def update_all_stocks(self, delay: float = 3.0) -> Dict[str, int]:
        """
        更新所有股票的数据

        Args:
            delay: 请求间隔（秒）

        Returns:
            {'success': 成功数量, 'failed': 失败数量}
        """
        import time

        symbols = list(self.watchlist['stocks'].keys())
        total = len(symbols)

        if total == 0:
            logger.warning("Watchlist为空")
            return {'success': 0, 'failed': 0}

        logger.info(f"开始更新 {total} 只股票的数据...")

        success = 0
        failed = 0

        for i, symbol in enumerate(symbols, 1):
            logger.info(f"[{i}/{total}] 更新 {symbol}")

            if self.update_stock(symbol):
                success += 1
            else:
                failed += 1

            # 添加延迟避免API限制
            if i < total:
                time.sleep(delay)

        self.watchlist['metadata']['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_watchlist()

        logger.info(f"更新完成: {success} 成功, {failed} 失败")
        return {'success': success, 'failed': failed}

    def add_note(self, symbol: str, note: str) -> bool:
        """
        为股票添加备注

        Args:
            symbol: 股票代码
            note: 备注内容

        Returns:
            是否成功
        """
        if symbol not in self.watchlist['stocks']:
            logger.warning(f"{symbol} 不在watchlist中")
            return False

        note_entry = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'content': note
        }

        if 'notes' not in self.watchlist['stocks'][symbol]:
            self.watchlist['stocks'][symbol]['notes'] = []

        self.watchlist['stocks'][symbol]['notes'].append(note_entry)

        logger.info(f"✓ 已为 {symbol} 添加备注")
        return self.save_watchlist()

    def get_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取单个股票的信息"""
        return self.watchlist['stocks'].get(symbol)

    def get_all_stocks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有股票"""
        return self.watchlist['stocks']

    def get_symbols(self) -> List[str]:
        """获取所有股票代码"""
        return list(self.watchlist['stocks'].keys())

    def bulk_add_from_screening(
        self,
        screening_results: List[Dict[str, Any]],
        replace: bool = False
    ) -> int:
        """
        从筛选结果批量添加股票

        Args:
            screening_results: 筛选结果列表
            replace: 是否替换现有watchlist

        Returns:
            添加的数量
        """
        if replace:
            self.watchlist = self._create_empty_watchlist()

        added = 0
        for stock_data in screening_results:
            symbol = stock_data.get('symbol')
            if symbol and self.add_stock(symbol, stock_data):
                added += 1

        self.watchlist['metadata']['last_screening'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_watchlist()

        logger.info(f"从筛选结果添加了 {added} 只股票")
        return added

    def generate_summary(self) -> str:
        """生成watchlist摘要"""
        lines = []
        lines.append("=" * 80)
        lines.append("Watch List 摘要")
        lines.append("=" * 80)

        metadata = self.watchlist['metadata']
        lines.append(f"\n总股票数: {metadata['total_stocks']}")
        lines.append(f"创建时间: {metadata['created']}")
        lines.append(f"最后筛选: {metadata.get('last_screening', 'N/A')}")
        lines.append(f"最后更新: {metadata.get('last_update', 'N/A')}")

        if self.watchlist['stocks']:
            lines.append(f"\n{'-' * 80}")
            lines.append("股票列表")
            lines.append(f"{'-' * 80}")

            for symbol, data in self.watchlist['stocks'].items():
                lines.append(f"\n{symbol} - {data.get('name', 'N/A')}")
                lines.append(f"  行业: {data.get('sector', 'N/A')}")
                lines.append(f"  市值: {DataFetcher.format_market_cap(data.get('market_cap', 0))}")
                lines.append(f"  当前价格: ${data.get('current_price', 0):.2f}")

                pe = data.get('pe_ratio')
                if pe:
                    lines.append(f"  PE比率: {pe:.2f}")

                roe = data.get('roe')
                if roe:
                    lines.append(f"  ROE: {roe:.2f}%")

                lines.append(f"  添加日期: {data.get('added_date', 'N/A')}")

                # 显示备注
                notes = data.get('notes', [])
                if notes:
                    lines.append(f"  备注: {len(notes)} 条")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

    def export_to_csv(self, output_path: str = None) -> bool:
        """
        导出watchlist到CSV

        Args:
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        import csv

        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(self.watchlist_path),
                f"watchlist_export_{datetime.now().strftime('%Y%m%d')}.csv"
            )

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if not self.watchlist['stocks']:
                    logger.warning("Watchlist为空，无法导出")
                    return False

                # 获取所有字段
                first_stock = next(iter(self.watchlist['stocks'].values()))
                fieldnames = [k for k in first_stock.keys() if k != 'notes']

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for stock_data in self.watchlist['stocks'].values():
                    row = {k: v for k, v in stock_data.items() if k != 'notes'}
                    writer.writerow(row)

            logger.info(f"✓ Watchlist已导出到 {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False


if __name__ == "__main__":
    # 测试watchlist管理器
    wl_manager = WatchListManager()

    # 添加测试股票
    wl_manager.add_stock('AAPL')
    wl_manager.add_note('AAPL', '这是一个测试备注')

    print(wl_manager.generate_summary())

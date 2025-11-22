"""
任务调度模块 - 定期执行筛选和更新任务
"""
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import List, Optional, Dict, Any

from .config_manager import ConfigManager
from .screener import StockScreener
from .watchlist_manager import WatchListManager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器"""

    def __init__(
        self,
        config_manager: ConfigManager = None,
        screener: StockScreener = None,
        watchlist_manager: WatchListManager = None,
        background: bool = True
    ):
        """
        初始化调度器

        Args:
            config_manager: 配置管理器
            screener: 股票筛选器
            watchlist_manager: Watchlist管理器
            background: 是否使用后台调度器（True）或阻塞调度器（False）
        """
        self.config_manager = config_manager or ConfigManager()
        self.screener = screener or StockScreener(self.config_manager)
        self.watchlist_manager = watchlist_manager or WatchListManager()

        # 选择调度器类型
        if background:
            self.scheduler = BackgroundScheduler()
        else:
            self.scheduler = BlockingScheduler()

        self.is_running = False

    def weekly_screening_task(
        self,
        custom_symbols: Dict[str, List[str]] = None,
        limit_per_market: int = 20
    ):
        """
        每周筛选任务 - 筛选所有市场并更新watchlist

        Args:
            custom_symbols: 自定义股票列表
            limit_per_market: 每个市场筛选数量限制
        """
        logger.info("=" * 80)
        logger.info("开始执行每周筛选任务")
        logger.info("=" * 80)

        try:
            # 执行多市场筛选
            all_results = self.screener.screen_all_markets(
                custom_symbols=custom_symbols,
                limit_per_market=limit_per_market
            )

            # 汇总所有通过的股票
            all_passed = []
            for market, results in all_results.items():
                passed = results.get('passed', [])
                all_passed.extend(passed)
                logger.info(f"{market.upper()} 市场: {len(passed)} 只股票通过筛选")

            # 更新watchlist
            if all_passed:
                logger.info(f"\n总共 {len(all_passed)} 只股票通过筛选")
                logger.info("更新Watch List...")

                # 替换watchlist
                added = self.watchlist_manager.bulk_add_from_screening(
                    all_passed,
                    replace=True
                )

                logger.info(f"✓ Watch List已更新，共 {added} 只股票")

                # 生成报告
                summary = self.watchlist_manager.generate_summary()
                logger.info(f"\n{summary}")

            else:
                logger.warning("没有股票通过筛选")

            logger.info("=" * 80)
            logger.info("每周筛选任务完成")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"每周筛选任务失败: {str(e)}", exc_info=True)

    def daily_update_task(self):
        """每日更新任务 - 更新watchlist中所有股票的数据"""
        logger.info("=" * 80)
        logger.info("开始执行每日更新任务")
        logger.info("=" * 80)

        try:
            # 更新所有股票数据
            result = self.watchlist_manager.update_all_stocks()

            logger.info(f"\n更新结果:")
            logger.info(f"  成功: {result['success']} 只")
            logger.info(f"  失败: {result['failed']} 只")

            # 显示更新后的摘要
            if result['success'] > 0:
                summary = self.watchlist_manager.generate_summary()
                logger.info(f"\n{summary}")

            logger.info("=" * 80)
            logger.info("每日更新任务完成")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"每日更新任务失败: {str(e)}", exc_info=True)

    def add_weekly_screening_job(
        self,
        day_of_week: str = 'mon',
        hour: int = 9,
        minute: int = 0,
        custom_symbols: Dict[str, List[str]] = None,
        limit_per_market: int = 20
    ):
        """
        添加每周筛选任务

        Args:
            day_of_week: 星期几 (mon, tue, wed, thu, fri, sat, sun)
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            custom_symbols: 自定义股票列表
            limit_per_market: 每个市场筛选数量限制
        """
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=hour,
            minute=minute
        )

        self.scheduler.add_job(
            func=self.weekly_screening_task,
            trigger=trigger,
            args=[custom_symbols, limit_per_market],
            id='weekly_screening',
            name='每周股票筛选',
            replace_existing=True
        )

        logger.info(f"✓ 已添加每周筛选任务: 每周{day_of_week.upper()} {hour:02d}:{minute:02d}")

    def add_daily_update_job(
        self,
        hour: int = 18,
        minute: int = 0
    ):
        """
        添加每日更新任务

        Args:
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
        """
        trigger = CronTrigger(
            hour=hour,
            minute=minute
        )

        self.scheduler.add_job(
            func=self.daily_update_task,
            trigger=trigger,
            id='daily_update',
            name='每日数据更新',
            replace_existing=True
        )

        logger.info(f"✓ 已添加每日更新任务: 每天 {hour:02d}:{minute:02d}")

    def run_screening_now(
        self,
        custom_symbols: Dict[str, List[str]] = None,
        limit_per_market: int = 20
    ):
        """立即执行筛选任务（不等待调度）"""
        self.weekly_screening_task(custom_symbols, limit_per_market)

    def run_update_now(self):
        """立即执行更新任务（不等待调度）"""
        self.daily_update_task()

    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已经在运行")
            return

        logger.info("启动任务调度器...")
        self.scheduler.start()
        self.is_running = True
        logger.info("✓ 调度器已启动")

        # 显示已调度的任务
        self.print_jobs()

    def stop(self):
        """停止调度器"""
        if not self.is_running:
            logger.warning("调度器未运行")
            return

        logger.info("停止任务调度器...")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("✓ 调度器已停止")

    def print_jobs(self):
        """打印所有已调度的任务"""
        jobs = self.scheduler.get_jobs()

        if not jobs:
            logger.info("没有已调度的任务")
            return

        logger.info("\n" + "=" * 80)
        logger.info("已调度的任务")
        logger.info("=" * 80)

        for job in jobs:
            logger.info(f"\n任务ID: {job.id}")
            logger.info(f"名称: {job.name}")
            logger.info(f"下次运行: {job.next_run_time}")

        logger.info("=" * 80)

    def setup_default_schedule(
        self,
        custom_symbols: Dict[str, List[str]] = None,
        limit_per_market: int = 20
    ):
        """
        设置默认调度计划

        - 每周一上午9:00执行筛选
        - 每天下午6:00执行更新
        """
        # 每周筛选 - 周一上午9:00
        self.add_weekly_screening_job(
            day_of_week='mon',
            hour=9,
            minute=0,
            custom_symbols=custom_symbols,
            limit_per_market=limit_per_market
        )

        # 每日更新 - 每天下午6:00
        self.add_daily_update_job(
            hour=18,
            minute=0
        )

        logger.info("\n✓ 已设置默认调度计划:")
        logger.info("  - 每周筛选: 周一 09:00")
        logger.info("  - 每日更新: 每天 18:00")


def run_scheduler_daemon(
    custom_symbols: Dict[str, List[str]] = None,
    limit_per_market: int = 20,
    background: bool = False
):
    """
    运行调度器守护进程

    Args:
        custom_symbols: 自定义股票列表
        limit_per_market: 每个市场筛选数量限制
        background: 是否后台运行
    """
    scheduler = TaskScheduler(background=not background)
    scheduler.setup_default_schedule(custom_symbols, limit_per_market)
    scheduler.start()

    if not background:
        try:
            # 阻塞模式 - 保持运行
            logger.info("\n调度器正在运行... (按 Ctrl+C 停止)")
            import time
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n接收到停止信号")
            scheduler.stop()


if __name__ == "__main__":
    # 测试调度器
    scheduler = TaskScheduler(background=True)

    # 设置默认调度
    scheduler.setup_default_schedule(limit_per_market=5)

    # 立即执行一次测试
    logger.info("\n执行测试筛选...")
    scheduler.run_screening_now(limit_per_market=3)

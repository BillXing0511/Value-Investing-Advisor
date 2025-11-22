#!/usr/bin/env python3
"""
命令行界面 - 价值投资顾问主程序
"""
import click
import sys
import os
from typing import List, Optional
from tabulate import tabulate
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_manager import ConfigManager
from src.data_fetcher import DataFetcher
from src.screener import StockScreener
from src.watchlist_manager import WatchListManager
from src.scheduler import TaskScheduler


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    价值投资顾问 - 帮助您筛选和跟踪价值投资机会

    支持美股、港股、A股市场
    """
    pass


@cli.group()
def config():
    """配置管理 - 查看和修改投资标准"""
    pass


@config.command('show')
def config_show():
    """显示当前投资标准配置"""
    config_mgr = ConfigManager()
    click.echo(config_mgr.display_config())


@config.command('edit')
@click.option('--criterion', '-c', required=True, help='标准名称 (如: pe_ratio)')
@click.option('--min', type=float, help='最小值')
@click.option('--max', type=float, help='最大值')
@click.option('--enable/--disable', default=None, help='启用/禁用')
def config_edit(criterion, min, max, enable):
    """修改投资标准"""
    config_mgr = ConfigManager()

    updates = {}
    if min is not None:
        updates['min'] = min
    if max is not None:
        updates['max'] = max
    if enable is not None:
        updates['enabled'] = enable

    if not updates:
        click.echo("错误: 请至少指定一个要修改的值", err=True)
        return

    if config_mgr.update_criteria(criterion, **updates):
        click.echo(f"✓ 已更新 {criterion}")
        click.echo(f"\n更新后的配置:")
        click.echo(config_mgr.display_config())
    else:
        click.echo(f"✗ 更新 {criterion} 失败", err=True)


@config.command('market')
@click.argument('market', type=click.Choice(['us', 'hk', 'cn']))
@click.option('--enable/--disable', required=True, help='启用/禁用市场')
def config_market(market, enable):
    """启用或禁用市场"""
    config_mgr = ConfigManager()

    if config_mgr.update_market(market, enable):
        status = "启用" if enable else "禁用"
        click.echo(f"✓ 已{status} {market.upper()} 市场")
    else:
        click.echo(f"✗ 更新市场配置失败", err=True)


@cli.group()
def screen():
    """股票筛选 - 根据投资标准筛选股票"""
    pass


@screen.command('run')
@click.option('--market', '-m', type=click.Choice(['us', 'hk', 'cn', 'all']),
              default='all', help='目标市场')
@click.option('--symbols', '-s', help='股票代码列表 (逗号分隔)')
@click.option('--limit', '-l', type=int, default=20, help='每个市场筛选数量限制')
@click.option('--update-watchlist/--no-update', default=True,
              help='是否更新watchlist')
def screen_run(market, symbols, limit, update_watchlist):
    """执行股票筛选"""
    screener = StockScreener()

    if symbols:
        # 使用自定义股票列表
        symbol_list = [s.strip() for s in symbols.split(',')]
        click.echo(f"筛选自定义股票列表: {', '.join(symbol_list)}")
        results = screener.screen_stocks(symbol_list)

        # 显示报告
        click.echo("\n" + screener.generate_report(results))

        # 更新watchlist
        if update_watchlist and results['passed']:
            wl_manager = WatchListManager()
            added = wl_manager.bulk_add_from_screening(results['passed'], replace=True)
            click.echo(f"\n✓ 已将 {added} 只股票添加到Watch List")

    elif market == 'all':
        # 筛选所有市场
        click.echo("筛选所有启用的市场...")
        all_results = screener.screen_all_markets(limit_per_market=limit)

        # 显示各市场结果
        for mkt, results in all_results.items():
            click.echo(f"\n{'=' * 80}")
            click.echo(f"{mkt.upper()} 市场筛选结果")
            click.echo(f"{'=' * 80}")
            click.echo(screener.generate_report(results, top_n=5))

        # 更新watchlist
        if update_watchlist:
            all_passed = []
            for results in all_results.values():
                all_passed.extend(results.get('passed', []))

            if all_passed:
                wl_manager = WatchListManager()
                added = wl_manager.bulk_add_from_screening(all_passed, replace=True)
                click.echo(f"\n✓ 已将 {added} 只股票添加到Watch List")

    else:
        # 筛选单个市场
        click.echo(f"筛选 {market.upper()} 市场...")
        results = screener.screen_by_market(market, limit=limit)

        click.echo("\n" + screener.generate_report(results))

        # 更新watchlist
        if update_watchlist and results['passed']:
            wl_manager = WatchListManager()
            added = wl_manager.bulk_add_from_screening(results['passed'], replace=True)
            click.echo(f"\n✓ 已将 {added} 只股票添加到Watch List")


@cli.group()
def watchlist():
    """Watch List管理 - 管理关注的股票列表"""
    pass


@watchlist.command('show')
@click.option('--detail/--summary', default=False, help='显示详细信息')
def watchlist_show(detail):
    """显示Watch List"""
    wl_manager = WatchListManager()

    if detail:
        click.echo(wl_manager.generate_summary())
    else:
        stocks = wl_manager.get_all_stocks()
        if not stocks:
            click.echo("Watch List为空")
            return

        # 表格显示
        table_data = []
        for symbol, data in stocks.items():
            table_data.append([
                symbol,
                data.get('name', 'N/A')[:30],
                f"${data.get('current_price', 0):.2f}",
                f"{data.get('pe_ratio', 0):.2f}" if data.get('pe_ratio') else 'N/A',
                f"{data.get('roe', 0):.2f}%" if data.get('roe') else 'N/A',
                DataFetcher.format_market_cap(data.get('market_cap', 0))
            ])

        headers = ['代码', '名称', '价格', 'PE', 'ROE', '市值']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo(f"\n总计: {len(stocks)} 只股票")


@watchlist.command('add')
@click.argument('symbol')
def watchlist_add(symbol):
    """添加股票到Watch List"""
    wl_manager = WatchListManager()

    click.echo(f"正在添加 {symbol}...")
    if wl_manager.add_stock(symbol):
        click.echo(f"✓ 已添加 {symbol}")
    else:
        click.echo(f"✗ 添加失败", err=True)


@watchlist.command('remove')
@click.argument('symbol')
def watchlist_remove(symbol):
    """从Watch List移除股票"""
    wl_manager = WatchListManager()

    if wl_manager.remove_stock(symbol):
        click.echo(f"✓ 已移除 {symbol}")
    else:
        click.echo(f"✗ 移除失败", err=True)


@watchlist.command('update')
@click.option('--symbol', '-s', help='更新指定股票（不指定则更新全部）')
def watchlist_update(symbol):
    """更新Watch List中的股票数据"""
    wl_manager = WatchListManager()

    if symbol:
        click.echo(f"正在更新 {symbol}...")
        if wl_manager.update_stock(symbol):
            click.echo(f"✓ {symbol} 已更新")

            # 显示更新后的信息
            stock = wl_manager.get_stock(symbol)
            if stock:
                click.echo(f"\n当前价格: ${stock['current_price']:.2f}")
                click.echo(f"更新时间: {stock['last_updated']}")
        else:
            click.echo(f"✗ 更新失败", err=True)
    else:
        click.echo("正在更新所有股票...")
        result = wl_manager.update_all_stocks()
        click.echo(f"\n✓ 更新完成: {result['success']} 成功, {result['failed']} 失败")


@watchlist.command('export')
@click.option('--output', '-o', help='输出文件路径')
def watchlist_export(output):
    """导出Watch List到CSV"""
    wl_manager = WatchListManager()

    if wl_manager.export_to_csv(output):
        click.echo("✓ 导出成功")
    else:
        click.echo("✗ 导出失败", err=True)


@watchlist.command('note')
@click.argument('symbol')
@click.argument('note')
def watchlist_note(symbol, note):
    """为股票添加备注"""
    wl_manager = WatchListManager()

    if wl_manager.add_note(symbol, note):
        click.echo(f"✓ 已为 {symbol} 添加备注")
    else:
        click.echo(f"✗ 添加备注失败", err=True)


@cli.group()
def schedule():
    """任务调度 - 设置定期筛选和更新任务"""
    pass


@schedule.command('start')
@click.option('--limit', '-l', type=int, default=20, help='每个市场筛选数量限制')
def schedule_start(limit):
    """
    启动调度器（守护进程）

    默认调度:
    - 每周一 09:00 执行筛选
    - 每天 18:00 执行更新
    """
    click.echo("启动任务调度器...")
    click.echo("\n默认调度:")
    click.echo("  - 每周筛选: 周一 09:00")
    click.echo("  - 每日更新: 每天 18:00")
    click.echo("\n按 Ctrl+C 停止\n")

    from src.scheduler import run_scheduler_daemon
    run_scheduler_daemon(limit_per_market=limit, background=False)


@schedule.command('run-screening')
@click.option('--limit', '-l', type=int, default=20, help='每个市场筛选数量限制')
def schedule_run_screening(limit):
    """立即执行一次筛选任务"""
    click.echo("执行筛选任务...")

    scheduler = TaskScheduler()
    scheduler.run_screening_now(limit_per_market=limit)

    click.echo("\n✓ 筛选任务完成")


@schedule.command('run-update')
def schedule_run_update():
    """立即执行一次更新任务"""
    click.echo("执行更新任务...")

    scheduler = TaskScheduler()
    scheduler.run_update_now()

    click.echo("\n✓ 更新任务完成")


@cli.command('interactive')
def interactive():
    """启动交互式配置向导"""
    click.echo("=" * 80)
    click.echo("欢迎使用价值投资顾问 - 交互式配置")
    click.echo("=" * 80)

    config_mgr = ConfigManager()

    # 1. 配置市场
    click.echo("\n1. 选择目标市场:")
    markets = {
        'us': click.confirm("  美国市场 (US)?", default=True),
        'hk': click.confirm("  香港市场 (HK)?", default=True),
        'cn': click.confirm("  中国市场 (CN)?", default=True)
    }

    for market, enabled in markets.items():
        config_mgr.update_market(market, enabled)

    # 2. 配置主要投资标准
    click.echo("\n2. 配置投资标准:")

    # PE比率
    if click.confirm("  设置PE比率限制?", default=True):
        pe_max = click.prompt("    最大PE比率", type=float, default=15.0)
        config_mgr.update_criteria('pe_ratio', enabled=True, max=pe_max)

    # ROE
    if click.confirm("  设置ROE限制?", default=True):
        roe_min = click.prompt("    最小ROE (%)", type=float, default=15.0)
        config_mgr.update_criteria('roe', enabled=True, min=roe_min)

    # 负债率
    if click.confirm("  设置负债率限制?", default=True):
        de_max = click.prompt("    最大负债率", type=float, default=0.5)
        config_mgr.update_criteria('debt_to_equity', enabled=True, max=de_max)

    click.echo("\n✓ 配置已保存")
    click.echo("\n当前配置:")
    click.echo(config_mgr.display_config())

    # 3. 执行筛选
    if click.confirm("\n是否立即执行筛选?", default=True):
        limit = click.prompt("每个市场筛选数量", type=int, default=10)

        screener = StockScreener(config_mgr)
        click.echo("\n开始筛选...")
        all_results = screener.screen_all_markets(limit_per_market=limit)

        # 显示结果并询问是否保存
        all_passed = []
        for mkt, results in all_results.items():
            passed = results.get('passed', [])
            all_passed.extend(passed)
            click.echo(f"\n{mkt.upper()}: {len(passed)} 只股票通过")

        if all_passed and click.confirm(f"\n找到 {len(all_passed)} 只股票，是否添加到Watch List?", default=True):
            wl_manager = WatchListManager()
            added = wl_manager.bulk_add_from_screening(all_passed, replace=True)
            click.echo(f"\n✓ 已添加 {added} 只股票到Watch List")

            # 显示watchlist
            click.echo("\n" + wl_manager.generate_summary())


@cli.command('info')
@click.argument('symbol')
def info(symbol):
    """查看股票详细信息"""
    fetcher = DataFetcher()

    click.echo(f"正在获取 {symbol} 的信息...")
    data = fetcher.get_stock_info(symbol)

    if not data:
        click.echo(f"✗ 无法获取 {symbol} 的数据", err=True)
        return

    click.echo("\n" + "=" * 80)
    click.echo(f"{data['symbol']} - {data['name']}")
    click.echo("=" * 80)

    click.echo(f"\n行业: {data['sector']} / {data['industry']}")
    click.echo(f"市值: {DataFetcher.format_market_cap(data['market_cap'])}")
    click.echo(f"当前价格: ${data['current_price']:.2f}")

    click.echo("\n估值指标:")
    click.echo(f"  PE比率: {data.get('pe_ratio', 'N/A')}")
    click.echo(f"  PB比率: {data.get('pb_ratio', 'N/A')}")
    click.echo(f"  PS比率: {data.get('ps_ratio', 'N/A')}")

    click.echo("\n盈利能力:")
    if data.get('roe'):
        click.echo(f"  ROE: {data['roe']:.2f}%")
    if data.get('roa'):
        click.echo(f"  ROA: {data['roa'] * 100:.2f}%")
    if data.get('profit_margin'):
        click.echo(f"  利润率: {data['profit_margin'] * 100:.2f}%")

    click.echo("\n财务健康:")
    if data.get('debt_to_equity'):
        click.echo(f"  负债率: {data['debt_to_equity']:.2f}")
    if data.get('current_ratio'):
        click.echo(f"  流动比率: {data['current_ratio']:.2f}")

    click.echo("\n其他:")
    click.echo(f"  52周最高: ${data.get('fifty_two_week_high', 'N/A')}")
    click.echo(f"  52周最低: ${data.get('fifty_two_week_low', 'N/A')}")

    click.echo("\n" + "=" * 80)


if __name__ == '__main__':
    cli()

"""股票筛选页面"""
import streamlit as st
import pandas as pd
from src.screener import StockScreener
from src.data_fetcher import DataFetcher


def show():
    """显示股票筛选页面"""
    st.title("🔍 股票筛选")

    config_mgr = st.session_state.config_manager
    wl_mgr = st.session_state.watchlist_manager

    # 检查是否有启用的标准
    enabled_criteria = config_mgr.get_enabled_criteria()
    if not enabled_criteria:
        st.warning("⚠️ 没有启用任何筛选标准。请前往「配置管理」启用筛选标准。")
        if st.button("前往配置管理"):
            st.switch_page("pages/config.py")
        return

    # 筛选选项
    st.subheader("筛选选项")

    col1, col2 = st.columns(2)

    with col1:
        # 筛选模式
        screen_mode = st.radio(
            "筛选模式",
            ["多市场筛选", "单市场筛选", "自定义股票列表"],
            horizontal=True
        )

    with col2:
        # 数量限制
        if screen_mode != "自定义股票列表":
            limit = st.number_input(
                "每个市场筛选数量",
                min_value=1,
                max_value=100,
                value=20,
                help="限制每个市场筛选的股票数量（避免API限制）"
            )

    # 根据模式显示不同选项
    if screen_mode == "单市场筛选":
        market = st.selectbox(
            "选择市场",
            ["us", "hk", "cn"],
            format_func=lambda x: {'us': '🇺🇸 美国', 'hk': '🇭🇰 香港', 'cn': '🇨🇳 中国'}[x]
        )
    elif screen_mode == "自定义股票列表":
        symbols_input = st.text_area(
            "输入股票代码（每行一个或逗号分隔）",
            placeholder="AAPL\nMSFT\nGOOGL\n或\nAAPL, MSFT, GOOGL",
            help="美股直接输入代码，港股加.HK后缀，A股加.SS或.SZ后缀"
        )

    # 是否更新Watch List
    update_watchlist = st.checkbox("自动将筛选结果添加到 Watch List", value=True)

    st.markdown("---")

    # 执行筛选按钮
    if st.button("🚀 开始筛选", type="primary", use_container_width=True):
        with st.spinner("正在筛选股票..."):
            screener = StockScreener(config_mgr)

            try:
                if screen_mode == "自定义股票列表":
                    # 解析股票代码
                    if not symbols_input:
                        st.error("请输入股票代码")
                        return

                    # 支持逗号和换行符分隔
                    symbols = []
                    for line in symbols_input.replace(',', '\n').split('\n'):
                        symbol = line.strip()
                        if symbol:
                            symbols.append(symbol)

                    if not symbols:
                        st.error("未能解析出有效的股票代码")
                        return

                    st.info(f"正在筛选 {len(symbols)} 只股票...")

                    # 执行筛选
                    results = screener.screen_stocks(symbols, verbose=False)

                elif screen_mode == "单市场筛选":
                    st.info(f"正在筛选 {market.upper()} 市场...")
                    results = screener.screen_by_market(market, limit=limit)

                else:  # 多市场筛选
                    st.info("正在筛选所有启用的市场...")
                    all_results = screener.screen_all_markets(limit_per_market=limit)

                    # 合并结果
                    all_passed = []
                    all_failed = []
                    for mkt, res in all_results.items():
                        all_passed.extend(res.get('passed', []))
                        all_failed.extend(res.get('failed', []))

                    results = {'passed': all_passed, 'failed': all_failed}

                # 显示结果
                _display_results(results, update_watchlist, wl_mgr)

            except Exception as e:
                st.error(f"筛选过程中出错: {str(e)}")

    # 显示当前筛选标准
    st.markdown("---")
    st.subheader("📋 当前筛选标准")

    with st.expander("查看详细标准", expanded=False):
        criteria_df_data = []
        for name, config in enabled_criteria.items():
            if 'min' in config and 'max' in config:
                range_str = f"{config['min']} ~ {config['max']}"
            elif 'value' in config:
                range_str = f">= {config['value']}"
            else:
                range_str = "N/A"

            criteria_df_data.append({
                '标准': config.get('description', name),
                '范围': range_str,
                '状态': '✓ 启用'
            })

        if criteria_df_data:
            df = pd.DataFrame(criteria_df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)


def _display_results(results: dict, update_watchlist: bool, wl_mgr):
    """显示筛选结果"""
    passed = results.get('passed', [])
    failed = results.get('failed', [])

    total = len(passed) + len(failed)

    if total == 0:
        st.warning("未找到任何股票")
        return

    # 统计信息
    st.success(f"筛选完成！共筛选 {total} 只股票")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总计", total)
    with col2:
        st.metric("通过", len(passed), delta=f"{len(passed)/total*100:.1f}%")
    with col3:
        st.metric("未通过", len(failed))

    # 更新Watch List
    if update_watchlist and passed:
        with st.spinner("正在更新 Watch List..."):
            added = wl_mgr.bulk_add_from_screening(passed, replace=True)
            st.success(f"✓ 已将 {added} 只股票添加到 Watch List")

    # 显示通过的股票
    if passed:
        st.subheader(f"✅ 通过筛选的股票 ({len(passed)})")

        # 转换为DataFrame
        display_data = []
        for stock in passed:
            display_data.append({
                '代码': stock['symbol'],
                '名称': stock.get('name', 'N/A')[:30],
                '行业': stock.get('sector', 'N/A')[:20],
                '价格': f"${stock.get('current_price', 0):.2f}",
                'PE': f"{stock.get('pe_ratio', 0):.2f}" if stock.get('pe_ratio') else 'N/A',
                'PB': f"{stock.get('pb_ratio', 0):.2f}" if stock.get('pb_ratio') else 'N/A',
                'ROE': f"{stock.get('roe', 0):.2f}%" if stock.get('roe') else 'N/A',
                '市值': DataFetcher.format_market_cap(stock.get('market_cap', 0))
            })

        df = pd.DataFrame(display_data)

        # 显示表格
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "代码": st.column_config.TextColumn("代码", width="small"),
                "名称": st.column_config.TextColumn("名称", width="medium"),
            }
        )

        # 下载按钮
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载结果 (CSV)",
            data=csv,
            file_name=f"screening_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    # 显示未通过的股票（可折叠）
    if failed:
        with st.expander(f"❌ 未通过筛选的股票 ({len(failed)})", expanded=False):
            failed_data = []
            for stock in failed[:20]:  # 最多显示20个
                reasons = stock.get('failed_reasons', ['未知原因'])
                failed_data.append({
                    '代码': stock['symbol'],
                    '名称': stock.get('name', 'N/A')[:30],
                    '原因': '; '.join(reasons[:2])  # 最多显示2个原因
                })

            failed_df = pd.DataFrame(failed_data)
            st.dataframe(failed_df, use_container_width=True, hide_index=True)

            if len(failed) > 20:
                st.caption(f"还有 {len(failed) - 20} 只未通过的股票...")

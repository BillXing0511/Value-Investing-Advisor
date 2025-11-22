"""Watch List 管理页面"""
import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_fetcher import DataFetcher


def show():
    """显示 Watch List 页面"""
    st.title("📋 Watch List 管理")

    wl_mgr = st.session_state.watchlist_manager
    watchlist = wl_mgr.get_all_stocks()

    if not watchlist:
        st.info("📭 Watch List 为空")
        st.markdown("""
        您还没有添加任何股票到 Watch List。

        **开始方式：**
        1. 前往"股票筛选"页面执行筛选
        2. 或在下方手动添加股票
        """)

        # 手动添加股票
        _add_stock_form(wl_mgr)
        return

    # 操作按钮行
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 更新全部", use_container_width=True):
            with st.spinner("正在更新所有股票数据..."):
                result = wl_mgr.update_all_stocks(delay=0.3)
                st.success(f"✓ 更新完成: {result['success']} 成功, {result['failed']} 失败")
                st.rerun()

    with col2:
        if st.button("📥 导出 CSV", use_container_width=True):
            if wl_mgr.export_to_csv():
                st.success("✓ 已导出到 data/ 目录")

    with col3:
        if st.button("➕ 添加股票", use_container_width=True):
            st.session_state['show_add_form'] = True

    with col4:
        if st.button("🗑️ 清空列表", use_container_width=True, type="secondary"):
            st.session_state['confirm_clear'] = True

    # 确认清空对话框
    if st.session_state.get('confirm_clear', False):
        st.warning("⚠️ 确定要清空整个 Watch List 吗？此操作不可撤销！")
        confirm_col1, confirm_col2 = st.columns(2)
        with confirm_col1:
            if st.button("确认清空", type="primary"):
                for symbol in list(watchlist.keys()):
                    wl_mgr.remove_stock(symbol)
                st.success("已清空 Watch List")
                st.session_state['confirm_clear'] = False
                st.rerun()
        with confirm_col2:
            if st.button("取消"):
                st.session_state['confirm_clear'] = False
                st.rerun()

    # 添加股票表单
    if st.session_state.get('show_add_form', False):
        _add_stock_form(wl_mgr)

    st.markdown("---")

    # 统计信息
    _display_statistics(watchlist)

    st.markdown("---")

    # Watch List 表格
    st.subheader(f"股票列表 ({len(watchlist)} 只)")

    # 排序选项
    sort_col1, sort_col2 = st.columns([3, 1])
    with sort_col1:
        sort_by = st.selectbox(
            "排序方式",
            ["symbol", "pe_ratio", "pb_ratio", "roe", "market_cap", "current_price"],
            format_func=lambda x: {
                "symbol": "代码",
                "pe_ratio": "PE比率",
                "pb_ratio": "PB比率",
                "roe": "ROE",
                "market_cap": "市值",
                "current_price": "价格"
            }[x]
        )
    with sort_col2:
        ascending = st.checkbox("升序", value=True)

    # 创建DataFrame
    display_data = []
    for symbol, stock in watchlist.items():
        display_data.append({
            '代码': symbol,
            '名称': stock.get('name', 'N/A')[:25],
            '行业': stock.get('sector', 'N/A')[:15],
            '价格': stock.get('current_price', 0),
            'PE': stock.get('pe_ratio'),
            'PB': stock.get('pb_ratio'),
            'ROE': stock.get('roe'),
            '负债率': stock.get('debt_to_equity'),
            '市值': stock.get('market_cap', 0),
            '添加日期': stock.get('added_date', 'N/A')[:10]
        })

    df = pd.DataFrame(display_data)

    # 排序
    if sort_by in df.columns:
        sort_column_map = {
            "symbol": "代码",
            "pe_ratio": "PE",
            "pb_ratio": "PB",
            "roe": "ROE",
            "market_cap": "市值",
            "current_price": "价格"
        }
        df = df.sort_values(by=sort_column_map.get(sort_by, sort_by), ascending=ascending)

    # 格式化显示
    df['价格'] = df['价格'].apply(lambda x: f"${x:.2f}" if x else 'N/A')
    df['PE'] = df['PE'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
    df['PB'] = df['PB'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
    df['ROE'] = df['ROE'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else 'N/A')
    df['负债率'] = df['负债率'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
    df['市值'] = df['市值'].apply(lambda x: DataFetcher.format_market_cap(x) if x else 'N/A')

    # 显示表格（可点击）
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row"
    )

    # 如果有选中的行，显示操作按钮
    if event.selection.rows:
        selected_indices = event.selection.rows
        selected_symbols = [list(watchlist.keys())[i] for i in selected_indices]

        st.write(f"已选中 {len(selected_symbols)} 只股票: {', '.join(selected_symbols)}")

        op_col1, op_col2, op_col3 = st.columns(3)

        with op_col1:
            if st.button("🔄 更新选中", use_container_width=True):
                with st.spinner("更新中..."):
                    success = 0
                    for symbol in selected_symbols:
                        if wl_mgr.update_stock(symbol):
                            success += 1
                    st.success(f"更新了 {success}/{len(selected_symbols)} 只股票")
                    st.rerun()

        with op_col2:
            if st.button("📝 查看详情", use_container_width=True):
                # 存储到session state并切换页面
                st.session_state['selected_symbol'] = selected_symbols[0]
                st.switch_page("pages/stock_info.py")

        with op_col3:
            if st.button("🗑️ 删除选中", use_container_width=True, type="secondary"):
                for symbol in selected_symbols:
                    wl_mgr.remove_stock(symbol)
                st.success(f"已删除 {len(selected_symbols)} 只股票")
                st.rerun()


def _add_stock_form(wl_mgr):
    """添加股票表单"""
    with st.form("add_stock_form"):
        st.subheader("➕ 添加股票")

        symbol_input = st.text_input(
            "股票代码",
            placeholder="例如: AAPL, 0700.HK, 600519.SS",
            help="美股直接输入代码，港股加.HK，A股加.SS或.SZ"
        )

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("添加", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("取消", use_container_width=True)

        if submit and symbol_input:
            symbol = symbol_input.strip().upper()
            with st.spinner(f"正在添加 {symbol}..."):
                if wl_mgr.add_stock(symbol):
                    st.success(f"✓ 已添加 {symbol}")
                    st.session_state['show_add_form'] = False
                    st.rerun()
                else:
                    st.error(f"添加失败: {symbol}")

        if cancel:
            st.session_state['show_add_form'] = False
            st.rerun()


def _display_statistics(watchlist: dict):
    """显示统计信息"""
    st.subheader("📊 统计概览")

    # 计算统计数据
    total_stocks = len(watchlist)
    if total_stocks == 0:
        return

    # 提取数据
    pe_ratios = [s.get('pe_ratio') for s in watchlist.values() if s.get('pe_ratio')]
    roe_values = [s.get('roe') for s in watchlist.values() if s.get('roe')]
    market_caps = [s.get('market_cap', 0) for s in watchlist.values() if s.get('market_cap')]

    # 行业分布
    sectors = {}
    for stock in watchlist.values():
        sector = stock.get('sector', 'Unknown')
        sectors[sector] = sectors.get(sector, 0) + 1

    # 显示指标
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("总股票数", total_stocks)

    with metric_col2:
        avg_pe = sum(pe_ratios) / len(pe_ratios) if pe_ratios else 0
        st.metric("平均 PE", f"{avg_pe:.2f}")

    with metric_col3:
        avg_roe = sum(roe_values) / len(roe_values) if roe_values else 0
        st.metric("平均 ROE", f"{avg_roe:.2f}%")

    with metric_col4:
        total_value = sum(market_caps)
        st.metric("总市值", DataFetcher.format_market_cap(total_value))

    # 可视化
    if len(sectors) > 1:
        st.subheader("行业分布")

        # 创建饼图
        sector_df = pd.DataFrame(list(sectors.items()), columns=['行业', '数量'])
        fig = px.pie(sector_df, values='数量', names='行业', hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

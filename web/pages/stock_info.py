"""股票详情页面"""
import streamlit as st
import plotly.graph_objects as go
from src.data_fetcher import DataFetcher


def show():
    """显示股票详情页面"""
    st.title("📊 股票详情")

    # 输入股票代码
    symbol_input = st.text_input(
        "输入股票代码",
        value=st.session_state.get('selected_symbol', ''),
        placeholder="例如: AAPL, 0700.HK, 600519.SS",
        help="美股直接输入代码，港股加.HK，A股加.SS或.SZ"
    )

    if not symbol_input:
        st.info("请输入股票代码查看详情")
        return

    symbol = symbol_input.strip().upper()

    # 按钮行
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("🔍 查询", type="primary", use_container_width=True):
            st.session_state['query_symbol'] = symbol

    with col2:
        wl_mgr = st.session_state.watchlist_manager
        if symbol in wl_mgr.get_symbols():
            if st.button("➖ 从Watch List移除", use_container_width=True):
                wl_mgr.remove_stock(symbol)
                st.success(f"已移除 {symbol}")
                st.rerun()
        else:
            if st.button("➕ 添加到Watch List", use_container_width=True):
                with st.spinner("添加中..."):
                    if wl_mgr.add_stock(symbol):
                        st.success(f"已添加 {symbol}")
                        st.rerun()

    with col3:
        if st.button("🔄 刷新数据", use_container_width=True):
            st.session_state['query_symbol'] = symbol
            st.session_state['force_refresh'] = True

    # 如果有查询
    if st.session_state.get('query_symbol'):
        symbol = st.session_state['query_symbol']

        with st.spinner(f"正在获取 {symbol} 的数据..."):
            fetcher = DataFetcher()
            stock_data = fetcher.get_stock_info(symbol)

            if not stock_data:
                st.error(f"无法获取 {symbol} 的数据。请检查股票代码是否正确。")
                return

            # 显示股票信息
            _display_stock_details(stock_data, fetcher)

            # 清除刷新标志
            if 'force_refresh' in st.session_state:
                del st.session_state['force_refresh']


def _display_stock_details(stock_data: dict, fetcher: DataFetcher):
    """显示股票详细信息"""
    # 标题
    st.markdown(f"## {stock_data['symbol']} - {stock_data['name']}")

    # 基本信息
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)

    with info_col1:
        st.metric("当前价格", f"${stock_data.get('current_price', 0):.2f}")

    with info_col2:
        st.metric("市值", DataFetcher.format_market_cap(stock_data.get('market_cap', 0)))

    with info_col3:
        if stock_data.get('fifty_two_week_high'):
            st.metric("52周最高", f"${stock_data['fifty_two_week_high']:.2f}")

    with info_col4:
        if stock_data.get('fifty_two_week_low'):
            st.metric("52周最低", f"${stock_data['fifty_two_week_low']:.2f}")

    st.markdown("---")

    # 行业信息
    st.subheader("📌 基本信息")
    basic_col1, basic_col2 = st.columns(2)

    with basic_col1:
        st.write(f"**行业:** {stock_data.get('sector', 'N/A')}")
        st.write(f"**子行业:** {stock_data.get('industry', 'N/A')}")

    with basic_col2:
        beta = stock_data.get('beta')
        if beta:
            st.write(f"**Beta系数:** {beta:.2f}")
        st.write(f"**更新时间:** {stock_data.get('last_updated', 'N/A')}")

    st.markdown("---")

    # 详细指标（选项卡）
    tab1, tab2, tab3, tab4 = st.tabs(["📈 估值指标", "💰 盈利能力", "🏦 财务健康", "📊 可视化"])

    with tab1:
        _display_valuation_metrics(stock_data)

    with tab2:
        _display_profitability_metrics(stock_data)

    with tab3:
        _display_financial_health(stock_data)

    with tab4:
        _display_visualizations(stock_data, fetcher)


def _display_valuation_metrics(stock_data: dict):
    """显示估值指标"""
    st.subheader("估值指标")

    val_col1, val_col2, val_col3 = st.columns(3)

    with val_col1:
        pe = stock_data.get('pe_ratio')
        st.metric("PE比率 (市盈率)", f"{pe:.2f}" if pe else "N/A")

    with val_col2:
        pb = stock_data.get('pb_ratio')
        st.metric("PB比率 (市净率)", f"{pb:.2f}" if pb else "N/A")

    with val_col3:
        ps = stock_data.get('ps_ratio')
        st.metric("PS比率 (市销率)", f"{ps:.2f}" if ps else "N/A")

    # 估值评价
    if pe:
        st.markdown("**PE 估值评价:**")
        if pe < 15:
            st.success("✅ PE < 15，估值较低")
        elif pe < 25:
            st.info("ℹ️ 15 ≤ PE < 25，估值适中")
        else:
            st.warning("⚠️ PE ≥ 25，估值较高")


def _display_profitability_metrics(stock_data: dict):
    """显示盈利能力指标"""
    st.subheader("盈利能力")

    prof_col1, prof_col2, prof_col3 = st.columns(3)

    with prof_col1:
        roe = stock_data.get('roe')
        st.metric("ROE (净资产收益率)", f"{roe:.2f}%" if roe else "N/A")

    with prof_col2:
        roa = stock_data.get('roa')
        if roa:
            st.metric("ROA (总资产收益率)", f"{roa * 100:.2f}%")

    with prof_col3:
        margin = stock_data.get('profit_margin')
        if margin:
            st.metric("利润率", f"{margin * 100:.2f}%")

    # 增长指标
    st.markdown("**增长指标:**")
    growth_col1, growth_col2 = st.columns(2)

    with growth_col1:
        rev_growth = stock_data.get('revenue_growth')
        if rev_growth:
            st.metric("营收增长率", f"{rev_growth:.2f}%")

    with growth_col2:
        earn_growth = stock_data.get('earnings_growth')
        if earn_growth:
            st.metric("盈利增长率", f"{earn_growth * 100:.2f}%")

    # ROE 评价
    if roe:
        st.markdown("**ROE 评价:**")
        if roe >= 20:
            st.success("✅ ROE ≥ 20%，盈利能力优秀")
        elif roe >= 15:
            st.info("ℹ️ 15% ≤ ROE < 20%，盈利能力良好")
        else:
            st.warning("⚠️ ROE < 15%，盈利能力一般")


def _display_financial_health(stock_data: dict):
    """显示财务健康指标"""
    st.subheader("财务健康")

    health_col1, health_col2, health_col3 = st.columns(3)

    with health_col1:
        de = stock_data.get('debt_to_equity')
        st.metric("负债率 (D/E)", f"{de:.2f}" if de else "N/A")

    with health_col2:
        cr = stock_data.get('current_ratio')
        st.metric("流动比率", f"{cr:.2f}" if cr else "N/A")

    with health_col3:
        qr = stock_data.get('quick_ratio')
        st.metric("速动比率", f"{qr:.2f}" if qr else "N/A")

    # 股息信息
    st.markdown("**股息信息:**")
    div_col1, div_col2 = st.columns(2)

    with div_col1:
        div_yield = stock_data.get('dividend_yield')
        if div_yield:
            st.metric("股息收益率", f"{div_yield:.2f}%")

    with div_col2:
        payout = stock_data.get('payout_ratio')
        if payout:
            st.metric("派息率", f"{payout * 100:.2f}%")

    # 负债率评价
    if de:
        st.markdown("**负债率评价:**")
        if de < 0.3:
            st.success("✅ D/E < 0.3，财务风险低")
        elif de < 0.5:
            st.info("ℹ️ 0.3 ≤ D/E < 0.5，财务风险适中")
        else:
            st.warning("⚠️ D/E ≥ 0.5，财务风险较高")


def _display_visualizations(stock_data: dict, fetcher: DataFetcher):
    """显示数据可视化"""
    st.subheader("数据可视化")

    # 关键指标对比图
    st.markdown("**关键指标总览**")

    metrics = {}
    if stock_data.get('pe_ratio'):
        metrics['PE比率'] = stock_data['pe_ratio']
    if stock_data.get('pb_ratio'):
        metrics['PB比率'] = stock_data['pb_ratio']
    if stock_data.get('roe'):
        metrics['ROE (%)'] = stock_data['roe']
    if stock_data.get('debt_to_equity'):
        metrics['负债率'] = stock_data['debt_to_equity']

    if metrics:
        fig = go.Figure(data=[
            go.Bar(
                x=list(metrics.keys()),
                y=list(metrics.values()),
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(metrics)]
            )
        ])

        fig.update_layout(
            title="核心财务指标",
            xaxis_title="指标",
            yaxis_title="值",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # 历史价格（如果有）
    st.markdown("**历史价格走势**")
    period = st.selectbox("时间周期", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)

    if st.button("加载历史数据"):
        with st.spinner("加载中..."):
            hist_data = fetcher.get_historical_data(stock_data['symbol'], period=period)

            if hist_data is not None and not hist_data.empty:
                fig = go.Figure()

                fig.add_trace(go.Candlestick(
                    x=hist_data.index,
                    open=hist_data['Open'],
                    high=hist_data['High'],
                    low=hist_data['Low'],
                    close=hist_data['Close'],
                    name='价格'
                ))

                fig.update_layout(
                    title=f"{stock_data['symbol']} 历史价格",
                    yaxis_title="价格 (USD)",
                    xaxis_rangeslider_visible=False,
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("无法获取历史数据")

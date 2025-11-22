"""首页"""
import streamlit as st
from datetime import datetime


def show():
    """显示首页"""
    st.title("🏠 欢迎使用价值投资顾问")

    # 欢迎信息
    st.markdown("""
    ### 智能股票筛选与投资分析工具

    本系统帮助您：
    - 🎯 根据价值投资标准自动筛选股票
    - 📊 跟踪和管理您的Watch List
    - 📈 获取实时的股票财务数据
    - ⏰ 定期自动执行筛选和更新任务

    支持市场：**美股 (US)** | **港股 (HK)** | **A股 (CN)**
    """)

    st.markdown("---")

    # 快速开始指南
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚡ 快速开始")
        st.markdown("""
        1. **配置标准** - 在"配置管理"中设置您的投资标准
        2. **执行筛选** - 在"股票筛选"中开始筛选
        3. **查看结果** - 在"Watch List"中查看筛选结果
        4. **设置定时** - 在"定时任务"中设置自动化
        """)

    with col2:
        st.subheader("📊 系统状态")

        # 获取配置信息
        config_mgr = st.session_state.config_manager
        wl_mgr = st.session_state.watchlist_manager

        # 显示统计信息
        markets = config_mgr.get_markets()
        enabled_markets = [k.upper() for k, v in markets.items() if v]

        enabled_criteria = config_mgr.get_enabled_criteria()
        watchlist = wl_mgr.get_all_stocks()

        # 创建指标卡片
        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric("启用市场", len(enabled_markets))

        with metric_col2:
            st.metric("筛选标准", len(enabled_criteria))

        with metric_col3:
            st.metric("Watch List", len(watchlist))

    st.markdown("---")

    # 当前配置概览
    st.subheader("📋 当前配置概览")

    config_mgr = st.session_state.config_manager

    col1, col2 = st.columns(2)

    with col1:
        st.write("**启用的市场:**")
        markets = config_mgr.get_markets()
        market_names = {'us': '🇺🇸 美国', 'hk': '🇭🇰 香港', 'cn': '🇨🇳 中国'}
        for code, enabled in markets.items():
            if enabled:
                st.success(f"{market_names.get(code, code)}")

    with col2:
        st.write("**启用的筛选标准:**")
        criteria = config_mgr.get_enabled_criteria()
        if criteria:
            for name, config in list(criteria.items())[:5]:
                st.info(f"{config.get('description', name)}")
            if len(criteria) > 5:
                st.caption(f"还有 {len(criteria) - 5} 项标准...")
        else:
            st.warning("未启用任何筛选标准")

    st.markdown("---")

    # Watch List 预览
    st.subheader("📋 Watch List 预览")

    wl_mgr = st.session_state.watchlist_manager
    watchlist = wl_mgr.get_all_stocks()

    if watchlist:
        # 显示前5只股票
        import pandas as pd

        preview_data = []
        for symbol, data in list(watchlist.items())[:5]:
            preview_data.append({
                '代码': symbol,
                '名称': data.get('name', 'N/A')[:20],
                '价格': f"${data.get('current_price', 0):.2f}",
                'PE': f"{data.get('pe_ratio', 0):.2f}" if data.get('pe_ratio') else 'N/A',
                'ROE': f"{data.get('roe', 0):.2f}%" if data.get('roe') else 'N/A',
            })

        df = pd.DataFrame(preview_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        if len(watchlist) > 5:
            st.caption(f"还有 {len(watchlist) - 5} 只股票... 前往 Watch List 查看全部")
    else:
        st.info("Watch List 为空。前往「股票筛选」开始筛选股票。")

    st.markdown("---")

    # 使用提示
    st.subheader("💡 使用提示")

    tips_col1, tips_col2 = st.columns(2)

    with tips_col1:
        st.markdown("""
        **保守型价值投资**
        - PE ≤ 15
        - PB ≤ 1.5
        - ROE ≥ 15%
        - 负债率 ≤ 0.3
        """)

    with tips_col2:
        st.markdown("""
        **成长型价值投资**
        - PE ≤ 25
        - ROE ≥ 20%
        - 营收增长 ≥ 15%
        - 负债率 ≤ 0.5
        """)

    # 免责声明
    st.markdown("---")
    st.warning("""
    ⚠️ **免责声明**

    本软件仅供学习和研究使用，不构成任何投资建议。
    使用本软件进行投资决策的风险由用户自行承担。
    投资有风险，入市需谨慎！
    """)

    st.caption(f"系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

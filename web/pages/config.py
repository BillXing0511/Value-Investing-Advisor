"""配置管理页面"""
import streamlit as st


def show():
    """显示配置管理页面"""
    st.title("⚙️ 投资标准配置")

    config_mgr = st.session_state.config_manager

    # 选项卡
    tab1, tab2 = st.tabs(["📊 筛选标准", "🌍 目标市场"])

    # 标准配置标签页
    with tab1:
        st.subheader("筛选标准配置")
        st.caption("设置用于筛选股票的财务指标范围")

        criteria = config_mgr.get_criteria()

        # 创建两列布局
        col1, col2 = st.columns(2)

        criteria_list = list(criteria.items())
        mid_point = (len(criteria_list) + 1) // 2

        # 左列
        with col1:
            for name, config in criteria_list[:mid_point]:
                _render_criterion(name, config, config_mgr)

        # 右列
        with col2:
            for name, config in criteria_list[mid_point:]:
                _render_criterion(name, config, config_mgr)

        st.markdown("---")

        # 批量操作
        st.subheader("批量操作")
        batch_col1, batch_col2, batch_col3 = st.columns(3)

        with batch_col1:
            if st.button("✓ 全部启用", use_container_width=True):
                for criterion_name in criteria.keys():
                    config_mgr.enable_criterion(criterion_name)
                st.success("已启用所有标准")
                st.rerun()

        with batch_col2:
            if st.button("✗ 全部禁用", use_container_width=True):
                for criterion_name in criteria.keys():
                    config_mgr.disable_criterion(criterion_name)
                st.warning("已禁用所有标准")
                st.rerun()

        with batch_col3:
            if st.button("🔄 重置默认", use_container_width=True):
                # 恢复默认配置
                config_mgr.config = config_mgr._get_default_config()
                config_mgr.save_config()
                st.info("已重置为默认配置")
                st.rerun()

    # 市场配置标签页
    with tab2:
        st.subheader("目标市场选择")
        st.caption("选择要筛选股票的市场")

        markets = config_mgr.get_markets()
        market_info = {
            'us': {'name': '🇺🇸 美国市场', 'desc': 'NASDAQ, NYSE - 全球最大的股票市场'},
            'hk': {'name': '🇭🇰 香港市场', 'desc': '港交所 - 连接中国与世界的桥梁'},
            'cn': {'name': '🇨🇳 中国市场', 'desc': '上交所、深交所 - 世界第二大股票市场'}
        }

        for market_code, info in market_info.items():
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {info['name']}")
                    st.caption(info['desc'])

                with col2:
                    current_status = markets.get(market_code, False)
                    new_status = st.toggle(
                        "启用",
                        value=current_status,
                        key=f"market_{market_code}"
                    )

                    if new_status != current_status:
                        config_mgr.update_market(market_code, new_status)
                        if new_status:
                            st.success(f"已启用{info['name']}")
                        else:
                            st.warning(f"已禁用{info['name']}")
                        st.rerun()

                st.markdown("---")

    # 显示当前配置摘要
    st.markdown("---")
    st.subheader("📋 当前配置摘要")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        enabled_criteria = config_mgr.get_enabled_criteria()
        st.metric("启用的筛选标准", f"{len(enabled_criteria)} / {len(criteria)}")

        if enabled_criteria:
            st.write("**启用的标准:**")
            for name, config in enabled_criteria.items():
                st.write(f"- {config.get('description', name)}")

    with summary_col2:
        enabled_markets = [k.upper() for k, v in markets.items() if v]
        st.metric("启用的市场", len(enabled_markets))

        if enabled_markets:
            st.write("**启用的市场:**")
            for market in enabled_markets:
                st.write(f"- {market}")

    # 最后更新时间
    last_updated = config_mgr.config.get('last_updated', 'N/A')
    st.caption(f"最后更新: {last_updated}")


def _render_criterion(name: str, config: dict, config_mgr):
    """渲染单个筛选标准"""
    with st.expander(f"{config.get('description', name)}", expanded=config.get('enabled', False)):
        # 启用/禁用开关
        enabled = st.checkbox(
            "启用此标准",
            value=config.get('enabled', False),
            key=f"enable_{name}"
        )

        if enabled != config.get('enabled', False):
            if enabled:
                config_mgr.enable_criterion(name)
            else:
                config_mgr.disable_criterion(name)

        # 范围型标准
        if 'min' in config and 'max' in config:
            col1, col2 = st.columns(2)

            with col1:
                min_val = st.number_input(
                    "最小值",
                    value=float(config['min']),
                    key=f"min_{name}",
                    disabled=not enabled
                )

            with col2:
                max_val = st.number_input(
                    "最大值",
                    value=float(config['max']),
                    key=f"max_{name}",
                    disabled=not enabled
                )

            if st.button("保存", key=f"save_{name}"):
                config_mgr.update_criteria(name, min=min_val, max=max_val, enabled=enabled)
                st.success(f"已更新 {config.get('description', name)}")

        # 单值型标准
        elif 'value' in config:
            value = st.number_input(
                "值",
                value=float(config['value']),
                key=f"value_{name}",
                disabled=not enabled
            )

            if st.button("保存", key=f"save_{name}"):
                config_mgr.update_criteria(name, value=value, enabled=enabled)
                st.success(f"已更新 {config.get('description', name)}")

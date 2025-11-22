"""定时任务管理页面"""
import streamlit as st
from src.scheduler import TaskScheduler


def show():
    """显示定时任务页面"""
    st.title("⏰ 定时任务管理")

    st.markdown("""
    设置定期自动执行的任务：
    - **每周筛选**: 根据投资标准筛选股票并更新 Watch List
    - **每日更新**: 更新 Watch List 中所有股票的最新数据
    """)

    st.markdown("---")

    # 立即执行任务
    st.subheader("⚡ 立即执行任务")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔍 立即筛选")
        st.caption("执行一次完整的股票筛选任务")

        limit = st.number_input(
            "每个市场筛选数量",
            min_value=1,
            max_value=100,
            value=20,
            key="screening_limit"
        )

        if st.button("▶️ 执行筛选任务", type="primary", use_container_width=True):
            with st.spinner("正在执行筛选任务..."):
                try:
                    config_mgr = st.session_state.config_manager
                    wl_mgr = st.session_state.watchlist_manager

                    scheduler = TaskScheduler(
                        config_manager=config_mgr,
                        watchlist_manager=wl_mgr
                    )

                    # 执行筛选
                    scheduler.run_screening_now(limit_per_market=limit)

                    st.success("✓ 筛选任务执行完成")

                    # 显示结果统计
                    watchlist = wl_mgr.get_all_stocks()
                    st.info(f"Watch List 现有 {len(watchlist)} 只股票")

                except Exception as e:
                    st.error(f"执行失败: {str(e)}")

    with col2:
        st.markdown("### 🔄 立即更新")
        st.caption("更新 Watch List 中所有股票的数据")

        wl_mgr = st.session_state.watchlist_manager
        current_stocks = len(wl_mgr.get_symbols())

        st.write(f"**当前 Watch List:** {current_stocks} 只股票")

        if current_stocks == 0:
            st.warning("Watch List 为空，无需更新")
        elif st.button("▶️ 执行更新任务", type="primary", use_container_width=True):
            with st.spinner("正在执行更新任务..."):
                try:
                    config_mgr = st.session_state.config_manager

                    scheduler = TaskScheduler(
                        config_manager=config_mgr,
                        watchlist_manager=wl_mgr
                    )

                    # 执行更新
                    scheduler.run_update_now()

                    st.success("✓ 更新任务执行完成")

                    # 重新加载 watchlist
                    st.rerun()

                except Exception as e:
                    st.error(f"执行失败: {str(e)}")

    st.markdown("---")

    # 调度器配置
    st.subheader("📅 调度器设置")

    st.info("""
    ℹ️ **注意**: Streamlit Web应用不支持后台定时任务。

    如需使用定时任务功能，请使用 CLI 版本:
    ```bash
    python main.py schedule start
    ```

    或者使用系统的 cron/计划任务功能定期调用 CLI 命令。
    """)

    # 显示推荐的调度配置
    with st.expander("📖 推荐的调度配置", expanded=True):
        st.markdown("### 方案 1: 使用 CLI 调度器")
        st.code("""
# 启动内置调度器（阻塞运行）
python main.py schedule start --limit 30

# 默认调度:
# - 每周一 09:00 执行筛选
# - 每天 18:00 执行更新
        """, language="bash")

        st.markdown("### 方案 2: 使用 Linux Cron")
        st.code("""
# 编辑 crontab
crontab -e

# 添加以下任务:
# 每周一 9:00 执行筛选
0 9 * * 1 cd /path/to/Value-Investing-Advisor && python main.py schedule run-screening --limit 30

# 每天 18:00 执行更新
0 18 * * * cd /path/to/Value-Investing-Advisor && python main.py schedule run-update
        """, language="bash")

        st.markdown("### 方案 3: 使用 Windows 任务计划程序")
        st.markdown("""
        1. 打开"任务计划程序"
        2. 创建基本任务
        3. 设置触发器（时间）
        4. 设置操作：
           - 程序: `python`
           - 参数: `main.py schedule run-screening --limit 30`
           - 起始于: 项目目录路径
        """)

    st.markdown("---")

    # 任务历史记录（模拟）
    st.subheader("📜 任务执行记录")

    st.info("任务执行记录功能将在未来版本中添加")

    # 可以添加一个简单的日志查看功能
    if st.checkbox("查看系统日志"):
        import os
        log_dir = "logs"
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            if log_files:
                selected_log = st.selectbox("选择日志文件", log_files)
                log_path = os.path.join(log_dir, selected_log)

                try:
                    with open(log_path, 'r') as f:
                        log_content = f.read()
                        st.text_area("日志内容", log_content, height=300)
                except Exception as e:
                    st.error(f"读取日志失败: {str(e)}")
            else:
                st.info("暂无日志文件")
        else:
            st.info("日志目录不存在")

    st.markdown("---")

    # 快速操作指南
    st.subheader("💡 使用建议")

    tips_col1, tips_col2 = st.columns(2)

    with tips_col1:
        st.markdown("""
        **日常使用流程:**
        1. 首次使用时，在"配置管理"中设置投资标准
        2. 点击"执行筛选任务"进行第一次筛选
        3. 在"Watch List"中查看筛选结果
        4. 每天点击"执行更新任务"更新数据
        5. 或设置系统定时任务自动执行
        """)

    with tips_col2:
        st.markdown("""
        **最佳实践:**
        - 每周筛选一次（避免频繁调用API）
        - 每天更新 Watch List（收盘后）
        - 定期调整筛选标准
        - 及时移除不再符合标准的股票
        - 为重要股票添加备注
        """)

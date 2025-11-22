"""
价值投资顾问 Web 应用
使用 Streamlit 框架
"""
import streamlit as st
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import ConfigManager
from src.watchlist_manager import WatchListManager


# 页面配置
st.set_page_config(
    page_title="价值投资顾问",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'config_manager' not in st.session_state:
    st.session_state.config_manager = ConfigManager()

if 'watchlist_manager' not in st.session_state:
    st.session_state.watchlist_manager = WatchListManager()

# 侧边栏
with st.sidebar:
    st.title("📈 价值投资顾问")
    st.markdown("---")

    # 导航菜单
    page = st.radio(
        "导航",
        ["🏠 首页", "⚙️ 配置管理", "🔍 股票筛选", "📋 Watch List", "📊 股票详情", "⏰ 定时任务"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # 快速信息
    st.subheader("快速信息")

    # 显示启用的市场
    markets = st.session_state.config_manager.get_markets()
    enabled_markets = [k.upper() for k, v in markets.items() if v]
    st.write(f"**启用市场:** {', '.join(enabled_markets) if enabled_markets else '无'}")

    # 显示启用的标准数量
    enabled_criteria = st.session_state.config_manager.get_enabled_criteria()
    st.write(f"**筛选标准:** {len(enabled_criteria)} 项")

    # 显示Watch List数量
    watchlist_count = len(st.session_state.watchlist_manager.get_symbols())
    st.write(f"**Watch List:** {watchlist_count} 只股票")

    st.markdown("---")
    st.caption("© 2025 价值投资顾问")


# 主页面路由
if page == "🏠 首页":
    from web.pages import home
    home.show()
elif page == "⚙️ 配置管理":
    from web.pages import config
    config.show()
elif page == "🔍 股票筛选":
    from web.pages import screening
    screening.show()
elif page == "📋 Watch List":
    from web.pages import watchlist
    watchlist.show()
elif page == "📊 股票详情":
    from web.pages import stock_info
    stock_info.show()
elif page == "⏰ 定时任务":
    from web.pages import scheduler
    scheduler.show()

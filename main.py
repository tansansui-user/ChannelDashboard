# -*- coding: utf-8 -*-
"""
ChannelDashboard メインアプリケーション
"""

import streamlit as st
from config import APP_TITLE, APP_ICON

def main():
    """メインアプリケーション"""
    
    # ページ設定
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide"
    )
    
    # タイトル表示
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown("---")
    
    # サイドバー
    st.sidebar.title("メニュー")
    page = st.sidebar.radio(
        "ページを選択",
        ["ダッシュボード", "目標管理", "日報作成", "設定"]
    )
    
    # ページ表示
    if page == "ダッシュボード":
        show_dashboard()
    elif page == "目標管理":
        show_goals()
    elif page == "日報作成":
        show_report()
    elif page == "設定":
        show_settings()

def show_dashboard():
    """ダッシュボードページ"""
    st.header("📊 ダッシュボード")
    st.info("ダッシュボード機能は開発中です")

def show_goals():
    """目標管理ページ"""
    st.header("🎯 目標管理")
    st.info("目標管理機能は開発中です")

def show_report():
    """日報作成ページ"""
    st.header("📝 日報作成")
    st.info("日報作成機能は開発中です")

def show_settings():
    """設定ページ"""
    st.header("⚙️ 設定")
    st.info("設定機能は開発中です")

if __name__ == "__main__":
    main()
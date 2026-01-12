# -*- coding: utf-8 -*-
"""
ChannelDashboard メインアプリケーション
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from youtube_data import YouTubeDataFetcher
from sheets_handler import SheetsHandler
from dashboard import show_dashboard
from goals import Goals
from report_generator import show_report_generator
import config

# ページ設定
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide"
)

# タイトル
st.title(f"{config.APP_ICON} {config.APP_TITLE}")

# サイドバー
st.sidebar.title("メニュー")
menu = st.sidebar.radio(
    "機能を選択",
    ["データ取得", "ダッシュボード", "目標管理", "日報作成", "設定"]
)

# セッション状態の初期化
if 'youtube_fetcher' not in st.session_state:
    st.session_state.youtube_fetcher = None
if 'sheets_handler' not in st.session_state:
    st.session_state.sheets_handler = None
if 'channel_stats' not in st.session_state:
    st.session_state.channel_stats = None
if 'recent_videos' not in st.session_state:
    st.session_state.recent_videos = None

# データ取得
if menu == "データ取得":
    st.header("📺 データ取得")
    
    # データ取得セクション
    st.subheader("🔄 データ取得")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📺 チャンネルデータ取得", use_container_width=True):
            try:
                with st.spinner("YouTube APIに接続中..."):
                    # YouTube Data Fetcher初期化
                    if st.session_state.youtube_fetcher is None:
                        st.session_state.youtube_fetcher = YouTubeDataFetcher()
                    
                    # チャンネル統計取得
                    channel_stats = st.session_state.youtube_fetcher.get_channel_stats()
                    st.session_state.channel_stats = channel_stats
                    
                    st.success("✅ チャンネルデータの取得に成功しました！")
                    
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
    
    with col2:
        if st.button("🎬 最新動画データ取得", use_container_width=True):
            try:
                with st.spinner("YouTube APIに接続中..."):
                    # YouTube Data Fetcher初期化
                    if st.session_state.youtube_fetcher is None:
                        st.session_state.youtube_fetcher = YouTubeDataFetcher()
                    
                    # 最新動画取得
                    recent_videos = st.session_state.youtube_fetcher.get_recent_videos(max_results=10)
                    st.session_state.recent_videos = recent_videos
                    
                    st.success("✅ 最新動画データの取得に成功しました！")
                    
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
    
    # Google Sheetsに保存ボタン
    if st.session_state.channel_stats or st.session_state.recent_videos:
        st.markdown("---")
        if st.button("💾 Google Sheetsに保存", use_container_width=True, type="primary"):
            try:
                with st.spinner("Google Sheetsに保存中..."):
                    # Sheets Handler初期化
                    if st.session_state.sheets_handler is None:
                        st.session_state.sheets_handler = SheetsHandler()
                    
                    # 日次データ保存
                    if st.session_state.channel_stats:
                        # 3日前の日付（データ集計の確実性向上）
                        target_date = datetime.now() - timedelta(days=3)
                        
                        daily_data = {
                            "date": target_date.strftime("%Y-%m-%d"),
                            "subscribers": st.session_state.channel_stats.get("subscribers", 0),
                            "total_views": st.session_state.channel_stats.get("total_views", 0),
                            "video_count": st.session_state.channel_stats.get("video_count", 0),
                            "revenue": 0,  # YouTube Analytics API保留中
                            "cpm": 0,  # YouTube Analytics API保留中
                            "rpm": 0,  # YouTube Analytics API保留中
                            "new_subscribers": 0,  # YouTube Analytics API保留中
                            "impressions_ctr": 0.0,  # YouTube Analytics API保留中
                            "avg_view_duration": 0,  # YouTube Analytics API保留中
                            "avg_view_percentage": 0.0  # YouTube Analytics API保留中
                        }
                        
                        st.session_state.sheets_handler.save_daily_data(daily_data)
                        st.success("✅ 日次データの保存に成功しました！")
                    
                    # 動画別データ保存
                    if st.session_state.recent_videos:
                        saved_count = 0
                        error_count = 0
                        
                        for video in st.session_state.recent_videos:
                            try:
                                # 動画データの型を確認
                                if not isinstance(video, dict):
                                    st.warning(f"⚠️ スキップ: 動画データが辞書型ではありません（型: {type(video)}）")
                                    error_count += 1
                                    continue
                                
                                video_data = {
                                    "video_id": video.get("video_id", ""),
                                    "title": video.get("title", ""),
                                    "published_at": video.get("published_at", ""),
                                    "views": video.get("views", 0),
                                    "likes": video.get("likes", 0),
                                    "comments": video.get("comments", 0),
                                    "duration": video.get("duration", ""),
                                    "thumbnail_url": video.get("thumbnail_url", "")
                                }
                                
                                st.session_state.sheets_handler.save_video_data(video_data)
                                saved_count += 1
                                
                            except Exception as e:
                                error_count += 1
                                video_id = video.get('video_id', 'Unknown') if isinstance(video, dict) else 'Unknown'
                                st.error(f"❌ 動画 {video_id} の保存エラー: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                        
                        if saved_count > 0:
                            st.success(f"✅ {saved_count}件の動画データの保存に成功しました！")
                        if error_count > 0:
                            st.warning(f"⚠️ {error_count}件の動画データの保存に失敗しました")
                    
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
    
    # データ表示セクション
    st.markdown("---")
    st.subheader("📈 取得データ")
    
    # チャンネル統計表示
    if st.session_state.channel_stats:
        st.markdown("### 📺 チャンネル統計")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="チャンネル名",
                value=st.session_state.channel_stats.get("channel_name", "N/A")
            )
        
        with col2:
            subscribers = st.session_state.channel_stats.get("subscribers", 0)
            st.metric(
                label="登録者数",
                value=f"{subscribers:,}人"
            )
        
        with col3:
            total_views = st.session_state.channel_stats.get("total_views", 0)
            st.metric(
                label="総再生回数",
                value=f"{total_views:,}回"
            )
        
        with col4:
            video_count = st.session_state.channel_stats.get("video_count", 0)
            st.metric(
                label="動画数",
                value=f"{video_count:,}本"
            )
    
    # 最新動画一覧表示
    if st.session_state.recent_videos:
        st.markdown("### 🎬 最新動画一覧")
        
        # データフレーム作成
        video_list = []
        for video in st.session_state.recent_videos:
            video_list.append({
                "タイトル": video.get("title", ""),
                "公開日": video.get("published_at", ""),
                "再生回数": f"{video.get('views', 0):,}",
                "高評価数": f"{video.get('likes', 0):,}",
                "コメント数": f"{video.get('comments', 0):,}",
                "動画ID": video.get("video_id", "")
            })
        
        df = pd.DataFrame(video_list)
        st.dataframe(df, use_container_width=True)
    
    # データ未取得時のメッセージ
    if not st.session_state.channel_stats and not st.session_state.recent_videos:
        st.info("👆 上のボタンをクリックしてデータを取得してください")
    
    # YouTube Analytics API保留中の注意事項
    st.markdown("---")
    st.warning("""
    ⚠️ **YouTube Analytics APIについて**
    
    現在、YouTube Analytics API（収益データ、CPM、RPM、詳細な視聴維持率など）は403 Forbiddenエラーのため一時的に無効化しています。
    
    **取得可能なデータ（YouTube Data API v3）**:
    - チャンネル登録者数
    - 総再生回数
    - 動画数
    - 動画ごとの再生回数、高評価数、コメント数
    
    **現在保留中のデータ（YouTube Analytics API）**:
    - 収益額、CPM、RPM
    - 1日の登録者増加数
    - 詳細な視聴維持率
    - インプレッションクリック率
    - 総再生時間、平均視聴時間
    
    この問題は Week 2後半〜Week 3 で調査・解決予定です。
    """)

# ダッシュボード
elif menu == "ダッシュボード":
    try:
        # Sheets Handler初期化
        if st.session_state.sheets_handler is None:
            st.session_state.sheets_handler = SheetsHandler()
        
        # ダッシュボード表示
        show_dashboard(st.session_state.sheets_handler)
        
    except Exception as e:
        st.error(f"❌ ダッシュボードの表示に失敗しました: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# 目標管理
elif menu == "目標管理":
    try:
        # Sheets Handler初期化
        if st.session_state.sheets_handler is None:
            st.session_state.sheets_handler = SheetsHandler()
        
        # Goalsクラスのインスタンス作成
        goals = Goals(st.session_state.sheets_handler)
        
        # 目標管理画面を表示
        goals.show()
        
    except Exception as e:
        st.error(f"❌ 目標管理の表示に失敗しました: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# 日報作成
elif menu == "日報作成":
    try:
        # Sheets Handler初期化
        if st.session_state.sheets_handler is None:
            st.session_state.sheets_handler = SheetsHandler()
        
        # Goalsクラスのインスタンス作成
        goals = Goals(st.session_state.sheets_handler)
        
        # 日報作成画面を表示
        show_report_generator(st.session_state.sheets_handler, goals)
        
    except Exception as e:
        st.error(f"❌ 日報作成の表示に失敗しました: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# 設定
elif menu == "設定":
    st.header("⚙️ 設定")
    st.info("設定機能は Week 4〜5 で実装予定です")
    
    # プロジェクト情報表示
    st.markdown("---")
    st.subheader("📋 プロジェクト情報")
    
    st.markdown(f"""
    - **チャンネルID**: `{config.CHANNEL_ID}`
    - **スプレッドシートID**: `{config.SPREADSHEET_ID}`
    - **プロジェクト**: Phase 1 - Week 3（ダッシュボード作成）
    """)
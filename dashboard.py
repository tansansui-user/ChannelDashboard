# -*- coding: utf-8 -*-
"""
ChannelDashboard ダッシュボード表示モジュール
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from goals import Goals
from sheets_handler import SheetsHandler


class Dashboard:
    """ダッシュボード表示クラス"""
    
    def __init__(self, sheets_handler):
        """
        初期化
        
        Args:
            sheets_handler: SheetsHandlerインスタンス
        """
        self.sheets = sheets_handler
        self.goals = Goals(sheets_handler)
    
    def show(self):
        """ダッシュボードを表示"""
        st.header("📊 ダッシュボード")
        
        # 目標達成状況セクション
        self._show_goal_progress()
        
        st.markdown("---")
        
        # データ読み込み
        try:
            daily_data = self.sheets.get_daily_data()
            video_data = self.sheets.get_video_data()
            
            if daily_data.empty and video_data.empty:
                st.warning("⚠️ データがありません。まずはデータを取得してください。")
                return
            
            # フィルタセクション
            self._show_filters()
            
            # サマリーセクション
            self._show_summary(daily_data, video_data)
            
            # グラフセクション
            self._show_charts(daily_data, video_data)
            
            # 動画パフォーマンステーブル
            self._show_video_performance(video_data)
            
        except Exception as e:
            st.error(f"❌ データの読み込みに失敗しました: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    def _show_goal_progress(self):
        """
        目標達成状況セクションを表示
        """
        try:
            # 現在の目標を取得
            current_goals = self.goals._get_current_goals()
            
            # 目標が設定されていない場合
            if current_goals is None:
                st.info("💡 目標が設定されていません。「目標管理」タブで目標を設定してください。")
                return
            
            # 実績データを取得
            actual_data = self.goals._get_latest_actual_data()
            
            st.subheader("🎯 目標達成状況")
            
            # 2列レイアウト
            col1, col2 = st.columns(2)
            
            # 目標項目のリスト
            goal_items = [
                {
                    "label": "新規動画24時間再生回数",
                    "goal_key": "goal_24h_views",
                    "actual_key": "新規動画24時間再生回数",
                    "unit": "回"
                },
                {
                    "label": "1日総再生回数",
                    "goal_key": "goal_daily_views",
                    "actual_key": "1日総再生回数",
                    "unit": "回"
                }
            ]
            
            # 各目標の進捗を表示
            for i, item in enumerate(goal_items):
                col = col1 if i % 2 == 0 else col2
                
                with col:
                    goal_value = current_goals.get(item["goal_key"], 0)
                    actual_value = actual_data.get(item["actual_key"], 0)
                    
                    if goal_value > 0:
                        progress = (actual_value / goal_value) * 100
                    else:
                        progress = 0
                    
                    # 達成状況に応じたメッセージとアイコン
                    if progress >= 100:
                        status = "🎉 目標達成！"
                        color = "green"
                    elif progress >= 80:
                        status = "🔥 あと少し！"
                        color = "orange"
                    elif progress >= 50:
                        status = "📈 順調"
                        color = "blue"
                    else:
                        status = "⚠️ 要改善"
                        color = "red"
                    
                    # カード形式で表示
                    st.markdown(f"**{item['label']}**")
                    st.progress(min(progress / 100, 1.0))
                    st.markdown(f"**{progress:.1f}%** ({actual_value:,}{item['unit']} / {goal_value:,}{item['unit']})")
                    st.markdown(f"<span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                    st.markdown("")  # 空行
            
        except Exception as e:
            st.error(f"目標達成状況の表示でエラーが発生しました: {str(e)}")
            import traceback
            st.text(traceback.format_exc())
    
    def _show_filters(self):
        """フィルタ表示"""
        st.subheader("🔍 フィルタ")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 期間フィルタ
            filter_period = st.selectbox(
                "期間",
                ["全期間", "過去7日間", "過去30日間", "過去90日間", "カスタム"],
                key="filter_period"
            )
            
            if filter_period == "カスタム":
                start_date = st.date_input("開始日", key="start_date")
                end_date = st.date_input("終了日", key="end_date")
        
        with col2:
            # 動画検索
            search_query = st.text_input("動画タイトル検索", key="search_query")
        
        with col3:
            # 並び替え
            sort_by = st.selectbox(
                "並び替え",
                ["公開日（新しい順）", "公開日（古い順）", "再生回数（多い順）", "再生回数（少ない順）", "高評価数（多い順）"],
                key="sort_by"
            )
        
        # セッションステートに保存
        st.session_state.filter_settings = {
            "period": filter_period,
            "search": search_query,
            "sort": sort_by
        }
        
        if filter_period == "カスタム":
            st.session_state.filter_settings["start_date"] = start_date
            st.session_state.filter_settings["end_date"] = end_date
    
    def _show_summary(self, daily_data, video_data):
        """サマリー表示"""
        st.subheader("📈 サマリー")
        
        # フィルタ適用
        filtered_videos = self._apply_filters(video_data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # 動画数
            video_count = len(filtered_videos)
            st.metric("動画数", f"{video_count:,}本")
        
        with col2:
            # 平均再生回数
            if not filtered_videos.empty and "再生回数" in filtered_videos.columns:
                avg_views = filtered_videos["再生回数"].mean()
                st.metric("平均再生回数", f"{int(avg_views):,}回")
            else:
                st.metric("平均再生回数", "N/A")
        
        with col3:
            # 平均高評価数
            if not filtered_videos.empty and "高評価数" in filtered_videos.columns:
                avg_likes = filtered_videos["高評価数"].mean()
                st.metric("平均高評価数", f"{int(avg_likes):,}")
            else:
                st.metric("平均高評価数", "N/A")
        
        with col4:
            # 平均高評価率
            if not filtered_videos.empty and "再生回数" in filtered_videos.columns and "高評価数" in filtered_videos.columns:
                # 再生回数が0の動画を除外
                valid_videos = filtered_videos[filtered_videos["再生回数"] > 0].copy()
                if not valid_videos.empty:
                    valid_videos["高評価率"] = (valid_videos["高評価数"] / valid_videos["再生回数"]) * 100
                    avg_like_rate = valid_videos["高評価率"].mean()
                    st.metric("平均高評価率", f"{avg_like_rate:.2f}%")
                else:
                    st.metric("平均高評価率", "N/A")
            else:
                st.metric("平均高評価率", "N/A")
    
    def _show_charts(self, daily_data, video_data):
        """グラフ表示"""
        st.subheader("📊 グラフ")
        
        # フィルタ適用
        filtered_videos = self._apply_filters(video_data)
        
        # タブで切り替え
        tab1, tab2, tab3 = st.tabs(["📈 トレンド", "📊 パフォーマンス", "🎯 高評価率"])
        
        with tab1:
            self._show_trend_charts(daily_data, filtered_videos)
        
        with tab2:
            self._show_performance_charts(filtered_videos)
        
        with tab3:
            self._show_like_rate_charts(filtered_videos)
    
    def _show_trend_charts(self, daily_data, video_data):
        """トレンドグラフ表示"""
        
        # 日次データがある場合
        if not daily_data.empty and "日付" in daily_data.columns:
            st.write("#### 日次トレンド")
            
            # 日付をdatetime型に変換
            daily_data_copy = daily_data.copy()
            daily_data_copy["日付"] = pd.to_datetime(daily_data_copy["日付"])
            daily_data_copy = daily_data_copy.sort_values("日付")
            
            # 再生回数の推移
            if "再生回数" in daily_data_copy.columns:
                fig = px.line(
                    daily_data_copy,
                    x="日付",
                    y="再生回数",
                    title="日次再生回数の推移",
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="日付",
                    yaxis_title="再生回数",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 動画データがある場合
        if not video_data.empty and "公開日時" in video_data.columns:
            st.write("#### 動画公開数の推移")
            
            # 公開日時をdatetime型に変換
            video_data_copy = video_data.copy()
            video_data_copy["公開日"] = pd.to_datetime(video_data_copy["公開日時"]).dt.date
            
            # 日ごとの公開数を集計
            video_counts = video_data_copy.groupby("公開日").size().reset_index(name="公開数")
            video_counts["公開日"] = pd.to_datetime(video_counts["公開日"])
            video_counts = video_counts.sort_values("公開日")
            
            fig = px.bar(
                video_counts,
                x="公開日",
                y="公開数",
                title="日別動画公開数",
            )
            fig.update_layout(
                xaxis_title="公開日",
                yaxis_title="公開数",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_performance_charts(self, video_data):
        """パフォーマンスグラフ表示"""
        
        if video_data.empty:
            st.info("データがありません")
            return
        
        # 再生回数トップ10
        if "再生回数" in video_data.columns and "動画タイトル" in video_data.columns:
            top_videos = video_data.nlargest(10, "再生回数")
            
            # タイトルを短縮（長すぎる場合）
            top_videos_copy = top_videos.copy()
            top_videos_copy["短縮タイトル"] = top_videos_copy["動画タイトル"].apply(
                lambda x: x[:30] + "..." if len(x) > 30 else x
            )
            
            fig = px.bar(
                top_videos_copy,
                y="短縮タイトル",
                x="再生回数",
                title="再生回数トップ10",
                orientation="h",
                text="再生回数"
            )
            fig.update_layout(
                yaxis_title="",
                xaxis_title="再生回数",
                yaxis={'categoryorder': 'total ascending'}
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        # 高評価数トップ10
        if "高評価数" in video_data.columns and "動画タイトル" in video_data.columns:
            top_liked_videos = video_data.nlargest(10, "高評価数")
            
            # タイトルを短縮
            top_liked_videos_copy = top_liked_videos.copy()
            top_liked_videos_copy["短縮タイトル"] = top_liked_videos_copy["動画タイトル"].apply(
                lambda x: x[:30] + "..." if len(x) > 30 else x
            )
            
            fig = px.bar(
                top_liked_videos_copy,
                y="短縮タイトル",
                x="高評価数",
                title="高評価数トップ10",
                orientation="h",
                text="高評価数"
            )
            fig.update_layout(
                yaxis_title="",
                xaxis_title="高評価数",
                yaxis={'categoryorder': 'total ascending'}
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_like_rate_charts(self, video_data):
        """高評価率グラフ表示"""
        
        if video_data.empty:
            st.info("データがありません")
            return
        
        if "再生回数" in video_data.columns and "高評価数" in video_data.columns:
            # 再生回数が0より大きい動画のみ
            valid_videos = video_data[video_data["再生回数"] > 0].copy()
            
            if valid_videos.empty:
                st.info("有効なデータがありません")
                return
            
            # 高評価率を計算
            valid_videos["高評価率"] = (valid_videos["高評価数"] / valid_videos["再生回数"]) * 100
            
            # 高評価率トップ10
            if "動画タイトル" in valid_videos.columns:
                top_rate_videos = valid_videos.nlargest(10, "高評価率")
                
                # タイトルを短縮
                top_rate_videos_copy = top_rate_videos.copy()
                top_rate_videos_copy["短縮タイトル"] = top_rate_videos_copy["動画タイトル"].apply(
                    lambda x: x[:30] + "..." if len(x) > 30 else x
                )
                
                fig = px.bar(
                    top_rate_videos_copy,
                    y="短縮タイトル",
                    x="高評価率",
                    title="高評価率トップ10",
                    orientation="h",
                    text="高評価率"
                )
                fig.update_layout(
                    yaxis_title="",
                    xaxis_title="高評価率 (%)",
                    yaxis={'categoryorder': 'total ascending'}
                )
                fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            # 散布図: 再生回数 vs 高評価率
            if "動画タイトル" in valid_videos.columns:
                fig = px.scatter(
                    valid_videos,
                    x="再生回数",
                    y="高評価率",
                    hover_data=["動画タイトル"],
                    title="再生回数 vs 高評価率",
                    size="高評価数",
                    color="高評価率",
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(
                    xaxis_title="再生回数",
                    yaxis_title="高評価率 (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _show_video_performance(self, video_data):
        """動画パフォーマンステーブル表示"""
        st.subheader("🎬 動画パフォーマンス")
        
        # フィルタ適用
        filtered_videos = self._apply_filters(video_data)
        
        if filtered_videos.empty:
            st.info("表示するデータがありません")
            return
        
        # 高評価率を計算
        display_data = filtered_videos.copy()
        if "再生回数" in display_data.columns and "高評価数" in display_data.columns:
            # 再生回数が0より大きい動画のみ高評価率を計算
            display_data["高評価率(%)"] = display_data.apply(
                lambda row: (row["高評価数"] / row["再生回数"] * 100) if row["再生回数"] > 0 else 0,
                axis=1
            )
            display_data["高評価率(%)"] = display_data["高評価率(%)"].round(2)
        
        # 表示する列を選択
        display_columns = ["動画タイトル", "公開日時", "再生回数", "高評価数", "コメント数"]
        if "高評価率(%)" in display_data.columns:
            display_columns.append("高評価率(%)")
        
        # 存在する列のみフィルタ
        existing_columns = [col for col in display_columns if col in display_data.columns]
        
        # データフレームを表示
        st.dataframe(
            display_data[existing_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # CSVダウンロードボタン
        csv = display_data[existing_columns].to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 CSVダウンロード",
            data=csv,
            file_name=f"video_performance_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def _apply_filters(self, video_data):
        """フィルタを適用"""
        if video_data.empty:
            return video_data
        
        filtered = video_data.copy()
        
        # セッションステートからフィルタ設定を取得
        if "filter_settings" not in st.session_state:
            return filtered
        
        settings = st.session_state.filter_settings
        
        # フィルタ設定を取得
        
        # 期間フィルタ
        if "公開日時" in filtered.columns:
            filtered["公開日時_dt"] = pd.to_datetime(filtered["公開日時"])
            
            if settings.get("period") == "過去7日間":
                cutoff_date = datetime.now() - timedelta(days=7)
                # タイムゾーンを揃える
                cutoff_date = pd.to_datetime(cutoff_date)
                if filtered["公開日時_dt"].dt.tz is not None:
                    cutoff_date = cutoff_date.tz_localize('UTC')
                filtered = filtered[filtered["公開日時_dt"] >= cutoff_date]
            elif settings.get("period") == "過去30日間":
                cutoff_date = datetime.now() - timedelta(days=30)
                # タイムゾーンを揃える
                cutoff_date = pd.to_datetime(cutoff_date)
                if filtered["公開日時_dt"].dt.tz is not None:
                    cutoff_date = cutoff_date.tz_localize('UTC')
                filtered = filtered[filtered["公開日時_dt"] >= cutoff_date]
            elif settings.get("period") == "過去90日間":
                cutoff_date = datetime.now() - timedelta(days=90)
                # タイムゾーンを揃える
                cutoff_date = pd.to_datetime(cutoff_date)
                if filtered["公開日時_dt"].dt.tz is not None:
                    cutoff_date = cutoff_date.tz_localize('UTC')
                filtered = filtered[filtered["公開日時_dt"] >= cutoff_date]
            elif settings.get("period") == "カスタム":
                if "start_date" in settings and "end_date" in settings:
                    start = pd.to_datetime(settings["start_date"])
                    end = pd.to_datetime(settings["end_date"]) + timedelta(days=1)
                    # タイムゾーンを揃える
                    if filtered["公開日時_dt"].dt.tz is not None:
                        start = start.tz_localize('UTC')
                        end = end.tz_localize('UTC')
                    filtered = filtered[(filtered["公開日時_dt"] >= start) & (filtered["公開日時_dt"] < end)]
            
            filtered = filtered.drop(columns=["公開日時_dt"])
        
        # 検索フィルタ
        search_term = settings.get("search", "")
        
        if search_term and search_term.strip() and "動画タイトル" in filtered.columns:
            search_term = search_term.strip()
            filtered = filtered[filtered["動画タイトル"].astype(str).str.contains(search_term, case=False, na=False)]
        
        # 並び替え
        sort_option = settings.get("sort")
        if sort_option:
            if sort_option == "公開日（新しい順）" and "公開日時" in filtered.columns:
                filtered = filtered.sort_values("公開日時", ascending=False)
            elif sort_option == "公開日（古い順）" and "公開日時" in filtered.columns:
                filtered = filtered.sort_values("公開日時", ascending=True)
            elif sort_option == "再生回数（多い順）" and "再生回数" in filtered.columns:
                filtered = filtered.sort_values("再生回数", ascending=False)
            elif sort_option == "再生回数（少ない順）" and "再生回数" in filtered.columns:
                filtered = filtered.sort_values("再生回数", ascending=True)
            elif sort_option == "高評価数（多い順）" and "高評価数" in filtered.columns:
                filtered = filtered.sort_values("高評価数", ascending=False)
        
        return filtered


def show_dashboard(sheets_handler):
    """
    ダッシュボードを表示（関数インターフェース）
    
    Args:
        sheets_handler: SheetsHandlerインスタンス
    """
    dashboard = Dashboard(sheets_handler)
    dashboard.show()
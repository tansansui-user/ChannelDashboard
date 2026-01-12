# -*- coding: utf-8 -*-
"""
目標管理機能
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sheets_handler import SheetsHandler

class Goals:
    """目標管理クラス"""
    
    def __init__(self, sheets_handler):
        """
        初期化
        
        Args:
            sheets_handler: SheetsHandlerインスタンス
        """
        self.sheets = sheets_handler
        
    def show(self):
        """目標管理画面のメイン表示"""
        st.header("🎯 目標管理")
        
        # タブ作成
        tab1, tab2, tab3 = st.tabs(["目標設定", "AI目標提案", "進捗確認"])
        
        with tab1:
            self._show_goal_settings()
            
        with tab2:
            self._show_ai_suggestions()
            
        with tab3:
            self._show_progress()
    
    def _show_goal_settings(self):
        """目標設定タブの表示"""
        st.subheader("📝 目標を設定")
        
        # 現在の目標を取得
        current_goals = self._get_current_goals()
               
        # 目標設定フォーム
        with st.form("goal_settings_form"):
            st.write("### 目標値を入力してください")
            
            # 1. 新規動画24時間再生回数
            goal_24h_views = st.number_input(
                "新規投稿動画の投稿後24時間の再生回数目標",
                min_value=0,
                value=current_goals.get("goal_24h_views", 5000),
                step=100,
                help="新しく投稿した動画が24時間で何回再生されることを目標にしますか？"
            )
            
            # 2. 1日総再生回数
            goal_daily_views = st.number_input(
                "チャンネル内1日の総再生回数目標",
                min_value=0,
                value=current_goals.get("goal_daily_views", 50000),
                step=1000,
                help="チャンネル全体で1日に何回再生されることを目標にしますか？"
            )
            
            # 3. 月間収益（円）
            goal_monthly_revenue = st.number_input(
                "1ヶ月の収益目標額（円）",
                min_value=0,
                value=current_goals.get("goal_monthly_revenue", 100000),
                step=10000,
                help="1ヶ月でいくらの収益を目標にしますか？"
            )
            
            # 4. 1日収益（円）
            goal_daily_revenue = st.number_input(
                "1日の収益目標額（円）",
                min_value=0,
                value=current_goals.get("goal_daily_revenue", 3000),
                step=100,
                help="1日でいくらの収益を目標にしますか？"
            )
            
            # 保存ボタン
            submitted = st.form_submit_button("💾 目標を保存", type="primary")
            
            if submitted:
                # 目標を保存
                goals_data = {
                    "goal_24h_views": goal_24h_views,
                    "goal_daily_views": goal_daily_views,
                    "goal_monthly_revenue": goal_monthly_revenue,
                    "goal_daily_revenue": goal_daily_revenue
                }
                
                success = self._save_goals(goals_data)
                
                if success:
                    st.success("✅ 目標を保存しました！")
                else:
                    st.error("❌ 目標の保存に失敗しました")
        
        # 現在の目標を表示
        if current_goals:
            st.write("---")
            st.write("### 📊 現在の目標")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("新規動画24時間再生回数", f"{current_goals.get('goal_24h_views', 0):,} 回")
                st.metric("1日総再生回数", f"{current_goals.get('goal_daily_views', 0):,} 回")
            
            with col2:
                st.metric("月間収益目標", f"¥{current_goals.get('goal_monthly_revenue', 0):,}")
                st.metric("1日収益目標", f"¥{current_goals.get('goal_daily_revenue', 0):,}")
    
    def _show_ai_suggestions(self):
        """AI目標提案タブの表示"""
        st.subheader("🤖 AI目標提案")
        
        st.info("過去30日間のデータを分析して、達成可能な目標を提案します")
        
        if st.button("📊 AI目標を生成", type="primary"):
            with st.spinner("データを分析中..."):
                suggestions = self._generate_ai_suggestions()
                
                if suggestions:
                    st.write("---")
                    st.write("### 💡 提案された目標")
                    
                    # 新規動画24時間再生回数
                    st.write("#### 1️⃣ 新規動画24時間再生回数")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("過去30日平均", f"{suggestions['avg_24h_views']:,} 回")
                    with col2:
                        st.metric("過去30日最高", f"{suggestions['max_24h_views']:,} 回")
                    with col3:
                        st.metric("🎯 推奨目標", f"{suggestions['recommended_24h_views']:,} 回", 
                                 delta=f"+{suggestions['recommended_24h_views'] - suggestions['avg_24h_views']:,}")
                    
                    st.write(f"**分析**: {suggestions['analysis_24h']}")
                    
                    st.write("---")
                    
                    # 1日総再生回数
                    st.write("#### 2️⃣ 1日総再生回数")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("過去30日平均", f"{suggestions['avg_daily_views']:,} 回")
                    with col2:
                        st.metric("過去30日最高", f"{suggestions['max_daily_views']:,} 回")
                    with col3:
                        st.metric("🎯 推奨目標", f"{suggestions['recommended_daily_views']:,} 回",
                                 delta=f"+{suggestions['recommended_daily_views'] - suggestions['avg_daily_views']:,}")
                    
                    st.write(f"**分析**: {suggestions['analysis_daily']}")
                    
                    st.write("---")
                    
                    # 収益目標（現在はダミーデータ）
                    st.write("#### 3️⃣ 収益目標")
                    st.warning("⚠️ YouTube Analytics API問題により、現在収益データは取得できません。手動で設定してください。")
                    
                    # 提案を目標として設定するボタン
                    st.write("---")
                    if st.button("✅ この提案を目標として設定", type="primary"):
                        goals_data = {
                            "goal_24h_views": suggestions['recommended_24h_views'],
                            "goal_daily_views": suggestions['recommended_daily_views'],
                            "goal_monthly_revenue": 0,  # 手動設定が必要
                            "goal_daily_revenue": 0  # 手動設定が必要
                        }
                        
                        success = self._save_goals(goals_data)
                        
                        if success:
                            st.success("✅ AI提案を目標として設定しました！「目標設定」タブで収益目標を追加してください。")
                        else:
                            st.error("❌ 目標の保存に失敗しました")
                else:
                    st.error("❌ データ分析に失敗しました。動画データが不足している可能性があります。")
    
    def _show_progress(self):
        """進捗確認タブの表示"""
        st.subheader("📈 進捗状況")
        
        # 現在の目標を取得
        current_goals = self._get_current_goals()
        
        if not current_goals or all(v == 0 for v in current_goals.values()):
            st.warning("⚠️ 目標が設定されていません。「目標設定」タブで目標を設定してください。")
            return
        
        # 最新の実績データを取得
        actual_data = self._get_latest_actual_data()
        
        if not actual_data:
            st.warning("⚠️ 実績データがありません。「データ取得」タブでデータを取得してください。")
            return
        
        st.write("### 🎯 目標達成状況")
        
        # 新規動画24時間再生回数
        if current_goals.get("goal_24h_views", 0) > 0:
            st.write("#### 新規動画24時間再生回数")
            actual_24h = actual_data.get("新規動画24時間再生回数", 0)
            goal_24h = current_goals["goal_24h_views"]
            progress_24h = (actual_24h / goal_24h * 100) if goal_24h > 0 else 0
            
            self._show_progress_bar("新規動画24時間再生回数", actual_24h, goal_24h, progress_24h, "回")
        
        st.write("---")
        
        # 1日総再生回数
        if current_goals.get("goal_daily_views", 0) > 0:
            st.write("#### 1日総再生回数")
            actual_daily = actual_data.get("1日総再生回数", 0)
            goal_daily = current_goals["goal_daily_views"]
            progress_daily = (actual_daily / goal_daily * 100) if goal_daily > 0 else 0
            
            self._show_progress_bar("1日総再生回数", actual_daily, goal_daily, progress_daily, "回")

# デバッグ: current_goals の内容を確認
        
        st.write("---")
        
        # 収益目標（現在は非表示）
        st.info("💡 収益データの進捗状況は、YouTube Analytics API問題解決後に実装予定です")
    
    def _show_progress_bar(self, title, actual, goal, progress, unit):
        """進捗バーの表示"""
        # 進捗率に応じて色とメッセージを変更
        if progress >= 100:
            color = "green"
            message = "🎉 目標達成！"
        elif progress >= 80:
            color = "orange"
            message = "🔥 あと少し！"
        elif progress >= 50:
            color = "blue"
            message = "📈 順調です"
        else:
            color = "red"
            message = "⚠️ 要改善"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 進捗バー
            if color == "green":
                st.progress(min(progress / 100, 1.0))
            elif color == "orange":
                st.progress(min(progress / 100, 1.0))
            elif color == "blue":
                st.progress(min(progress / 100, 1.0))
            else:
                st.progress(min(progress / 100, 1.0))
            
            # 実績と目標
            st.write(f"**実績**: {actual:,} {unit} / **目標**: {goal:,} {unit}")
        
        with col2:
            # 進捗率とメッセージ
            st.metric("進捗率", f"{progress:.1f}%")
            st.write(message)
    
    def _get_current_goals(self):
        """現在の目標を取得"""
        try:
            goals_df = self.sheets.get_goals()
            
            if goals_df.empty:
                return {}
            
            # 最新の目標を取得（最後の行）
            latest_goal = goals_df.iloc[-1]
            
            return {
                "goal_24h_views": int(latest_goal.get("新規動画24時間再生回数", 0)),
                "goal_daily_views": int(latest_goal.get("1日総再生回数", 0)),
                "goal_monthly_revenue": int(latest_goal.get("月間収益", 0)),
                "goal_daily_revenue": int(latest_goal.get("1日収益", 0))
            }
        except Exception as e:
            st.error(f"目標データの取得エラー: {str(e)}")
            return {}
    
    def _save_goals(self, goals_data):
        """目標を保存"""
        try:
            # Google Sheetsに保存するデータを作成
            save_data = {
                "設定日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "新規動画24時間再生回数": goals_data["goal_24h_views"],
                "1日総再生回数": goals_data["goal_daily_views"],
                "月間収益": goals_data["goal_monthly_revenue"],
                "1日収益": goals_data["goal_daily_revenue"]
            }
            
            # sheets_handler.pyのsave_goals()を使用
            self.sheets.save_goals(save_data)
            
            return True
        except Exception as e:
            st.error(f"目標保存エラー: {str(e)}")
            return False
    
    def _generate_ai_suggestions(self):
        """AI目標提案を生成"""
        try:
            # 動画データを取得
            video_df = self.sheets.get_video_data()
            
            if video_df.empty:
                return None
            
            # 過去30日間のデータをフィルタ
            video_df["公開日時_dt"] = pd.to_datetime(video_df["公開日時"])
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # タイムゾーン調整
            if video_df["公開日時_dt"].dt.tz is not None:
                cutoff_date = cutoff_date.replace(tzinfo=video_df["公開日時_dt"].dt.tz)
            
            recent_videos = video_df[video_df["公開日時_dt"] >= cutoff_date]
            
            if recent_videos.empty:
                return None
            
            # 1. 新規動画24時間再生回数の分析（ダミー計算）
            # 本来は投稿後24時間のデータが必要だが、現在は平均再生回数で代用
            avg_views = int(recent_videos["再生回数"].mean())
            max_views = int(recent_videos["再生回数"].max())
            
            # 推奨目標: 平均の120%（達成可能性を考慮）
            recommended_24h = int(avg_views * 1.2)
            
            # トレンド分析（簡易版）
            if len(recent_videos) >= 5:
                recent_5 = recent_videos.nlargest(5, "公開日時_dt")["再生回数"].mean()
                older_5 = recent_videos.nsmallest(5, "公開日時_dt")["再生回数"].mean()
                
                if recent_5 > older_5 * 1.1:
                    trend_24h = "上昇傾向です。やや高めの目標でも達成可能でしょう。"
                elif recent_5 < older_5 * 0.9:
                    trend_24h = "下降傾向です。現実的な目標設定を推奨します。"
                else:
                    trend_24h = "安定しています。平均より少し高めの目標が適切です。"
            else:
                trend_24h = "データが少ないため、平均値ベースの目標を推奨します。"
            
            # 2. 1日総再生回数の分析
            # 現在は1動画あたりの平均 × 動画数で概算
            daily_videos = len(recent_videos) / 30  # 1日あたりの投稿数
            avg_daily_views = int(avg_views * daily_videos * 10)  # 概算（既存動画からの再生も含む）
            max_daily_views = int(max_views * daily_videos * 15)  # 最高値の概算
            
            recommended_daily = int(avg_daily_views * 1.15)
            
            if len(recent_videos) >= 5:
                if recent_5 > older_5 * 1.1:
                    trend_daily = "チャンネル全体の再生回数が増加傾向です。"
                elif recent_5 < older_5 * 0.9:
                    trend_daily = "チャンネル全体の再生回数が減少傾向です。"
                else:
                    trend_daily = "チャンネル全体の再生回数は安定しています。"
            else:
                trend_daily = "データが少ないため、控えめな目標を推奨します。"
            
            return {
                "avg_24h_views": avg_views,
                "max_24h_views": max_views,
                "recommended_24h_views": recommended_24h,
                "analysis_24h": trend_24h,
                "avg_daily_views": avg_daily_views,
                "max_daily_views": max_daily_views,
                "recommended_daily_views": recommended_daily,
                "analysis_daily": trend_daily
            }
            
        except Exception as e:
            st.error(f"AI分析エラー: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None
    
    def _get_latest_actual_data(self):
        """最新の実績データを取得"""
        try:
            # 動画データを取得
            video_df = self.sheets.get_video_data()
            
            
            actual_data = {
                "新規動画24時間再生回数": 0,
                "1日総再生回数": 0,
                "月間収益": 0,  # YouTube Analytics API保留中のため0
                "1日収益": 0     # YouTube Analytics API保留中のため0
            }
            
            if not video_df.empty:
                # 再生回数列を数値型に変換
                if '再生回数' in video_df.columns:
                    video_df['再生回数'] = pd.to_numeric(video_df['再生回数'], errors='coerce')
                
                # 公開日時でソート（最新が先頭）
                if '公開日時' in video_df.columns:
                    video_df['公開日時_dt'] = pd.to_datetime(video_df['公開日時'], errors='coerce')
                    video_df = video_df.sort_values('公開日時_dt', ascending=False)
                    latest_video = video_df.iloc[0]
                    
                    # 最新動画の現在の再生回数を24時間再生回数として使用
                    if pd.notna(latest_video['再生回数']):
                        actual_data["新規動画24時間再生回数"] = int(latest_video['再生回数'])
                
                # 全動画の再生回数合計を1日総再生回数として使用（簡易版）
                if '再生回数' in video_df.columns:
                    total_views = video_df['再生回数'].sum()
                    if pd.notna(total_views) and total_views > 0:
                        actual_data["1日総再生回数"] = int(total_views)
            
            return actual_data
            
        except Exception as e:
            st.error(f"実績データ取得エラー: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return {
                "新規動画24時間再生回数": 0,
                "1日総再生回数": 0,
                "月間収益": 0,
                "1日収益": 0
            }
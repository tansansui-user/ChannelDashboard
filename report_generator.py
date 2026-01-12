# -*- coding: utf-8 -*-
"""
ChannelDashboard 日報作成モジュール
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from goals import Goals


class ReportGenerator:
    """日報作成クラス"""
    
    def __init__(self, sheets_handler, goals):
        """
        初期化
        
        Args:
            sheets_handler: SheetsHandlerインスタンス
            goals: Goalsインスタンス
        """
        self.sheets = sheets_handler
        self.goals = goals
    
    def show(self):
        """日報作成画面を表示"""
        st.header("📝 日報作成")
        
        # タブで機能を分ける
        tab1, tab2 = st.tabs(["✏️ 日報作成", "⚙️ 設定"])
        
        with tab1:
            self._show_report_creation()
        
        with tab2:
            self._show_settings()
    
    def _show_report_creation(self):
        """日報作成タブの表示"""
        st.subheader("✏️ 日報を作成")
        
        # 日報設定をロード
        settings = self._load_settings()
        
        # 設定がある場合は「前回の設定で作成」ボタンを表示
        if settings:
            if st.button("🔄 前回の設定で日報を作成", type="primary"):
                report = self._generate_report(settings)
                self._display_report(report)
                return
        
        st.write("---")
        
        # 日報カスタマイズUI
        st.write("#### 📋 日報に含める項目を選択")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_new_video = st.checkbox("🎬 新規投稿動画について", value=True)
            include_revenue = st.checkbox("💰 収益について", value=True)
        
        with col2:
            include_channel_stats = st.checkbox("📊 チャンネル統計", value=False)
            include_top_videos = st.checkbox("🏆 トップ5動画", value=False)
        
        st.write("---")
        
        # 手動入力項目（YouTube Studioで確認した値を入力）
        st.write("#### ✏️ 手動入力項目")
        st.caption("※YouTube Studioで確認した値を入力してください")
        
        col1, col2 = st.columns(2)
        
        with col1:
            manual_like_rate = st.number_input(
                "24時間高評価率（%）",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                help="YouTube Studio → コンテンツ → アナリティクス → エンゲージメント → 高評価率（低評価比）"
            )
        
        with col2:
            manual_like_rate_goal = st.number_input(
                "高評価率の目標（%）",
                min_value=0.0,
                max_value=100.0,
                value=90.0,
                step=0.1,
                help="高評価率の目標値"
            )
        
        st.write("---")
        
        # 日報生成ボタン
        if st.button("📝 日報を生成", type="primary"):
            settings = {
                "include_new_video": include_new_video,
                "include_revenue": include_revenue,
                "include_channel_stats": include_channel_stats,
                "include_top_videos": include_top_videos,
                "manual_like_rate": manual_like_rate,
                "manual_like_rate_goal": manual_like_rate_goal
            }
            
            # 設定を保存
            self._save_settings(settings)
            
            # 日報を生成
            report = self._generate_report(settings)
            
            # 日報を表示
            self._display_report(report)
    
    def _show_settings(self):
        """設定タブの表示"""
        st.subheader("⚙️ 日報設定")
        
        # 現在の設定を表示
        settings = self._load_settings()
        
        if settings:
            st.write("#### 📊 現在の設定")
            st.write(f"- 新規投稿動画について: {'✅' if settings.get('include_new_video') else '❌'}")
            st.write(f"- 収益について: {'✅' if settings.get('include_revenue') else '❌'}")
            st.write(f"- チャンネル統計: {'✅' if settings.get('include_channel_stats') else '❌'}")
            st.write(f"- トップ5動画: {'✅' if settings.get('include_top_videos') else '❌'}")
            
            st.write("---")
            
            if st.button("🗑️ 設定をリセット"):
                self._clear_settings()
                st.success("設定をリセットしました")
                st.rerun()
        else:
            st.info("まだ設定が保存されていません。日報作成タブで日報を生成すると設定が保存されます。")
    
    def _generate_report(self, settings):
        """
        日報を生成
        
        Args:
            settings: 日報設定
        
        Returns:
            str: Chatwork形式の日報
        """
        # データを取得
        try:
            video_data = self.sheets.get_video_data()
            current_goals = self.goals._get_current_goals()
            actual_data = self.goals._get_latest_actual_data()
        except Exception as e:
            return f"[info]\n❌ データ取得エラー: {str(e)}\n[/info]"
        
        # 日付
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        today_str = f"{today.year}年{today.month}月{today.day}日"
        yesterday_str = f"{yesterday.month}月{yesterday.day}日"
        
        # 日報の開始
        report_lines = []
        report_lines.append("[info]")
        report_lines.append(f"📊 YouTubeチャンネル日報（{today_str}）")
        report_lines.append("")
        
        # ■新規投稿動画について
        if settings.get("include_new_video") and not video_data.empty:
            report_lines.append("■新規投稿動画について")
            
            # 最新動画を取得
            video_data_sorted = video_data.copy()
            video_data_sorted["公開日時"] = pd.to_datetime(video_data_sorted["公開日時"], errors='coerce')
            video_data_sorted = video_data_sorted.sort_values("公開日時", ascending=False)
            
            if not video_data_sorted.empty:
                latest_video = video_data_sorted.iloc[0]
                
                # 公開日時を取得
                pub_date = latest_video.get("公開日時")
                if pd.notna(pub_date):
                    pub_date_str = f"{pub_date.month}月{pub_date.day}日分　{pub_date.hour}時公開"
                else:
                    pub_date_str = "不明"
                
                report_lines.append(pub_date_str)
                
                # 24時間視聴回数
                views = int(latest_video.get("再生回数", 0))
                goal_24h = current_goals.get("goal_24h_views", 0)
                
                if goal_24h > 0:
                    achievement = "達成" if views >= goal_24h else "未達"
                    report_lines.append(f"　◇24時間視聴回数")
                    report_lines.append(f"　　目標：{goal_24h:,}回　結果：{views:,}回（{achievement}）")
                else:
                    report_lines.append(f"　◇24時間視聴回数")
                    report_lines.append(f"　　結果：{views:,}回")
                
                report_lines.append("")
                
                # 24時間高評価率（手動入力値を使用）
                manual_like_rate = settings.get("manual_like_rate", 0.0)
                manual_like_rate_goal = settings.get("manual_like_rate_goal", 90.0)
                
                if manual_like_rate > 0:
                    achievement_like = "達成" if manual_like_rate >= manual_like_rate_goal else "未達"
                    report_lines.append(f"　◇24時間高評価率")
                    report_lines.append(f"　　目標：{manual_like_rate_goal:.0f}％　結果：{manual_like_rate:.1f}%（{achievement_like}）")
                else:
                    report_lines.append(f"　◇24時間高評価率")
                    report_lines.append(f"　　※YouTube Studioで確認して入力してください")
                report_lines.append("")
                
                # インプレッションのクリック率（YouTube Analytics API必要 - 現在保留中）
                report_lines.append("　◇投稿後1時間のインプレッションのクリック率")
                report_lines.append("　　※YouTube Analytics API実装後に取得可能")
                report_lines.append("")
                
                # チャンネル登録者の視聴回数（YouTube Analytics API必要 - 現在保留中）
                report_lines.append("　◇チャンネル登録者の視聴回数")
                report_lines.append("　　※YouTube Analytics API実装後に取得可能")
                report_lines.append("")
                
                # 24時間チャンネル登録者数（YouTube Analytics API必要 - 現在保留中）
                report_lines.append("　◇24時間チャンネル登録者数")
                report_lines.append("　　※YouTube Analytics API実装後に取得可能")
                report_lines.append("")
            
            report_lines.append("")
        
        # ■収益について
        if settings.get("include_revenue"):
            report_lines.append("■収益について")
            report_lines.append(f"{yesterday_str}分")
            report_lines.append("※YouTube Analytics API実装後に取得可能")
            report_lines.append("")
            
            # 月間収益（仮データ）
            report_lines.append(f"{today.month}月合計（目標利益：250,000円）")
            report_lines.append("※YouTube Analytics API実装後に取得可能")
            report_lines.append("")
        
        # チャンネル統計（オプション）
        if settings.get("include_channel_stats") and not video_data.empty:
            report_lines.append("■チャンネル統計")
            
            # 総再生回数
            total_views = video_data["再生回数"].sum() if "再生回数" in video_data.columns else 0
            report_lines.append(f"・総再生回数: {int(total_views):,}回")
            
            # 総高評価数
            total_likes = video_data["高評価数"].sum() if "高評価数" in video_data.columns else 0
            report_lines.append(f"・総高評価数: {int(total_likes):,}件")
            
            # 動画数
            video_count = len(video_data)
            report_lines.append(f"・動画数: {video_count}本")
            
            report_lines.append("")
        
        # トップ5動画（オプション）
        if settings.get("include_top_videos") and not video_data.empty:
            report_lines.append("■再生回数トップ5")
            
            # 再生回数でソート
            if "再生回数" in video_data.columns:
                video_data["再生回数_num"] = pd.to_numeric(video_data["再生回数"], errors='coerce')
                top_videos = video_data.nlargest(5, "再生回数_num")
                
                for idx, (_, video) in enumerate(top_videos.iterrows(), 1):
                    title = video.get("動画タイトル", "不明")
                    views = int(video.get("再生回数", 0))
                    report_lines.append(f"{idx}. {title}: {views:,}回")
            
            report_lines.append("")
        
        # 日報の終了
        report_lines.append("[/info]")
        
        return "\n".join(report_lines)
    
    def _display_report(self, report):
        """
        日報を表示
        
        Args:
            report: Chatwork形式の日報
        """
        st.write("---")
        st.write("#### 📄 生成された日報")
        
        # プレビュー表示
        st.info("**プレビュー**")
        st.code(report, language="")
        
        st.write("---")
        
        # コピー用テキストエリア
        st.text_area(
            "👇 Chatworkにコピー&ペーストしてください",
            value=report,
            height=400,
            key="report_textarea"
        )
        
        # クリップボードにコピーボタンの説明
        st.write("💡 **コピー方法**: 上のテキストエリアをクリック → 全選択（Ctrl+A） → コピー（Ctrl+C）")
    
    def _save_settings(self, settings):
        """
        設定を保存
        
        Args:
            settings: 日報設定
        """
        st.session_state.report_settings = settings
    
    def _load_settings(self):
        """
        設定を読み込み
        
        Returns:
            dict: 日報設定（存在しない場合はNone）
        """
        return st.session_state.get("report_settings")
    
    def _clear_settings(self):
        """設定をクリア"""
        if "report_settings" in st.session_state:
            del st.session_state.report_settings


def show_report_generator(sheets_handler, goals):
    """
    日報作成画面を表示（関数インターフェース）
    
    Args:
        sheets_handler: SheetsHandlerインスタンス
        goals: Goalsインスタンス
    """
    report_gen = ReportGenerator(sheets_handler, goals)
    report_gen.show()
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
        
        # 動画データを取得
        video_data = self.sheets.get_video_data()
        
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
        
        # 新規投稿動画の選択
        selected_video = None
        if include_new_video:
            st.write("#### 🎬 報告する動画を選択")
            
            if not video_data.empty and "公開日時" in video_data.columns:
                # 公開日時をdatetime型に変換
                video_data["公開日時_dt"] = pd.to_datetime(video_data["公開日時"], errors='coerce')
                video_data["公開日"] = video_data["公開日時_dt"].dt.date
                
                # 公開日の一覧を取得（新しい順）
                available_dates = video_data["公開日"].dropna().unique()
                available_dates = sorted(available_dates, reverse=True)
                
                if len(available_dates) > 0:
                    # 日付選択（デフォルトは前日）
                    default_video_date = datetime.now().date() - timedelta(days=1)
                    selected_date = st.date_input(
                        "動画の公開日を選択",
                        value=default_video_date,
                        help="報告したい動画の公開日を選択してください"
                    )
                    
                    # 選択した日付の動画をフィルタ
                    videos_on_date = video_data[video_data["公開日"] == selected_date]
                    
                    if not videos_on_date.empty:
                        # 動画の選択肢を作成
                        video_options = []
                        for _, row in videos_on_date.iterrows():
                            pub_time = row["公開日時_dt"]
                            if pd.notna(pub_time):
                                # UTC→JST変換（+9時間）
                                pub_time_jst = pub_time + timedelta(hours=9)
                                time_str = pub_time_jst.strftime("%H:%M")
                            else:
                                time_str = "不明"
                            title = row.get("動画タイトル", "タイトル不明")[:30]
                            video_options.append(f"{time_str} 公開 - {title}")
                        
                        # 動画を選択
                        selected_video_idx = st.selectbox(
                            "報告する動画を選択",
                            range(len(video_options)),
                            format_func=lambda x: video_options[x],
                            help="複数の動画がある場合は選択してください"
                        )
                        
                        selected_video = videos_on_date.iloc[selected_video_idx]
                        
                        # 選択した動画の情報を表示
                        st.success(f"✅ 選択中: {selected_video.get('動画タイトル', '不明')}")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**再生回数**: {int(selected_video.get('再生回数', 0)):,} 回")
                        with col2:
                            st.write(f"**高評価数**: {int(selected_video.get('高評価数', 0)):,} 件")
                    else:
                        st.warning(f"⚠️ {selected_date} に公開された動画はありません")
                else:
                    st.warning("⚠️ 動画データがありません。「データ取得」タブでデータを取得してください。")
            else:
                st.warning("⚠️ 動画データがありません。「データ取得」タブでデータを取得してください。")
        
        st.write("---")
        
        # 収益の日付選択
        selected_revenue_date = None
        if include_revenue:
            st.write("#### 💰 収益の日付を選択")
            
            selected_revenue_date = st.date_input(
                "収益の日付を選択",
                value=datetime.now().date() - timedelta(days=2),
                help="報告したい収益の日付を選択してください（通常は前々日の収益が確定）"
            )
            
            st.info("💡 収益データはYouTube Analytics API実装後に自動取得されます。現在は日付のみ選択可能です。")
        
        st.write("---")
        
        # 手動入力項目（YouTube Studioで確認した値を入力）
        st.write("#### ✏️ 手動入力項目")
        st.caption("※YouTube Studioで確認した値を入力してください")
        
        # 高評価率の目標は「目標管理」メニューで設定
        current_goals = self.goals._get_current_goals()
        like_rate_goal = current_goals.get("goal_like_rate", 90.0)
        
        st.info(f"💡 高評価率の目標: **{like_rate_goal:.1f}%**（「目標管理」メニューで変更可能）")
        
        manual_like_rate = st.number_input(
            "24時間高評価率（%）※実績値を入力",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            help="YouTube Studio → コンテンツ → アナリティクス → エンゲージメント → 高評価率（低評価比）"
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
                "selected_video": selected_video.to_dict() if selected_video is not None else None,
                "selected_revenue_date": selected_revenue_date
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
        today_str = f"{today.year}年{today.month}月{today.day}日"
        
        # 日報の開始
        report_lines = []
        report_lines.append("日報をお送りいたします")
        report_lines.append("")
        
        # ■新規投稿動画について
        if settings.get("include_new_video"):
            report_lines.append("■新規投稿動画について")
            
            # 選択した動画を使用（なければ最新動画）
            selected_video_dict = settings.get("selected_video")
            
            if selected_video_dict:
                # 選択した動画を使用
                pub_date = pd.to_datetime(selected_video_dict.get("公開日時"), errors='coerce')
                views = int(selected_video_dict.get("再生回数", 0))
            elif not video_data.empty:
                # 最新動画を使用（フォールバック）
                video_data_sorted = video_data.copy()
                video_data_sorted["公開日時"] = pd.to_datetime(video_data_sorted["公開日時"], errors='coerce')
                video_data_sorted = video_data_sorted.sort_values("公開日時", ascending=False)
                latest_video = video_data_sorted.iloc[0]
                pub_date = latest_video.get("公開日時")
                views = int(latest_video.get("再生回数", 0))
            else:
                pub_date = None
                views = 0
            
            # 公開日時を表示（UTC→JST変換 +9時間）
            if pd.notna(pub_date):
                pub_date_jst = pub_date + timedelta(hours=9)
                pub_date_str = f"{pub_date_jst.month}月{pub_date_jst.day}日分　{pub_date_jst.hour}時公開"
            else:
                pub_date_str = "不明"
            
            report_lines.append(pub_date_str)
            
            # 24時間視聴回数
            goal_24h = current_goals.get("goal_24h_views", 0)
            
            if goal_24h > 0:
                achievement = "達成" if views >= goal_24h else "未達"
                report_lines.append(f"　◇24時間視聴回数")
                report_lines.append(f"　　目標：{goal_24h:,}回　結果：{views:,}回（{achievement}）")
            else:
                report_lines.append(f"　◇24時間視聴回数")
                report_lines.append(f"　　結果：{views:,}回")
            
            report_lines.append("")
            
            # 24時間高評価率（実績は手動入力、目標は目標管理から取得）
            manual_like_rate = settings.get("manual_like_rate", 0.0)
            like_rate_goal = current_goals.get("goal_like_rate", 90.0)
            
            if manual_like_rate > 0:
                achievement_like = "達成" if manual_like_rate >= like_rate_goal else "未達"
                report_lines.append(f"　◇24時間高評価率")
                report_lines.append(f"　　目標：{like_rate_goal:.0f}％　結果：{manual_like_rate:.1f}%（{achievement_like}）")
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
            
            # 選択した収益日を使用
            selected_revenue_date = settings.get("selected_revenue_date")
            if selected_revenue_date:
                revenue_date_str = f"{selected_revenue_date.month}月{selected_revenue_date.day}日"
            else:
                yesterday = today - timedelta(days=1)
                revenue_date_str = f"{yesterday.month}月{yesterday.day}日"
            
            report_lines.append(f"{revenue_date_str}分")
            report_lines.append("※YouTube Analytics API実装後に取得可能")
            report_lines.append("")
            
            # 月間収益目標を取得
            monthly_revenue_goal = current_goals.get("goal_monthly_revenue", 0)
            if monthly_revenue_goal > 0:
                report_lines.append(f"{today.month}月合計（目標利益：{monthly_revenue_goal:,}円）")
            else:
                report_lines.append(f"{today.month}月合計")
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
        
        # 日報の終了（タグなし）
        
        return "\n".join(report_lines)
    
    def _display_report(self, report):
        """
        日報を表示
        
        Args:
            report: Chatwork形式の日報
        """
        st.write("---")
        st.write("#### 📄 生成された日報")
        
        # コピー用テキストエリア
        st.text_area(
            "👇 Chatworkにコピー&ペーストしてください",
            value=report,
            height=400,
            key="report_textarea"
        )
        
        # ワンクリックコピーボタン（JavaScript使用）
        import streamlit.components.v1 as components
        
        # レポートのエスケープ処理
        escaped_report = report.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        
        copy_button_html = f"""
        <button onclick="copyToClipboard()" style="
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 0;
        ">📋 ワンクリックでコピー</button>
        <span id="copy-status" style="margin-left: 10px; color: green;"></span>
        <script>
        function copyToClipboard() {{
            const text = `{escaped_report}`;
            navigator.clipboard.writeText(text).then(function() {{
                document.getElementById('copy-status').innerText = '✅ コピーしました！';
                setTimeout(function() {{
                    document.getElementById('copy-status').innerText = '';
                }}, 2000);
            }}, function(err) {{
                document.getElementById('copy-status').innerText = '❌ コピーに失敗しました';
            }});
        }}
        </script>
        """
        
        components.html(copy_button_html, height=60)
    
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
# -*- coding: utf-8 -*-
"""
ChannelDashboard 設定ファイル
"""

# YouTubeチャンネル設定
CHANNEL_ID = "UCQz3h3FKeQ2u0L4dPnebbyg"  # YouTubeチャンネルID

# Google Sheets設定
SPREADSHEET_ID = "15IBx7Z6xTVZCYIrGk5vVd2yKPYkCkWIid7jKPFWslmk"  # GoogleスプレッドシートID
SHEET_NAMES = {
    "daily": "日次データ",
    "videos": "動画別データ",
    "goals": "目標設定",
    "monthly": "月次集計"
}

# YouTube API スコープ
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]

# Google Sheets API スコープ
SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]

# アプリケーション設定
APP_TITLE = "ChannelDashboard"
APP_ICON = "📊"
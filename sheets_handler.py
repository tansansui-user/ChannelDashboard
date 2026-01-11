# -*- coding: utf-8 -*-
"""
Google Sheets 連携モジュール
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEETS_SCOPES

class SheetsHandler:
    """Google Sheets操作クラス"""
    
    def __init__(self, spreadsheet_id):
        """初期化"""
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
    
    def authenticate(self):
        """Google Sheets認証"""
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'service_account.json',
            SHEETS_SCOPES
        )
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        return True
    
    def get_worksheet(self, sheet_name):
        """ワークシート取得"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            return worksheet
        except gspread.WorksheetNotFound:
            # シートが存在しない場合は作成
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=1000,
                cols=20
            )
            return worksheet
    
    def save_daily_data(self, data):
        """日次データ保存"""
        # 開発中
        pass
    
    def save_video_data(self, data):
        """動画別データ保存"""
        # 開発中
        pass
    
    def load_data(self, sheet_name):
        """データ読み込み"""
        # 開発中
        pass
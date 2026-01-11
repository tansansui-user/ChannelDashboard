# -*- coding: utf-8 -*-
"""
YouTube Data API 連携モジュール
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

class YouTubeDataFetcher:
    """YouTubeデータ取得クラス"""
    
    def __init__(self, scopes):
        """初期化"""
        self.scopes = scopes
        self.credentials = None
        self.youtube = None
        self.youtube_analytics = None
    
    def authenticate(self):
        """YouTube API認証"""
        # トークンファイルが存在する場合は読み込み
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.credentials = pickle.load(token)
        
        # 認証情報が無効または存在しない場合は再認証
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                self.credentials = flow.run_local_server(port=0)
            
            # トークンを保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # APIクライアント構築
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        self.youtube_analytics = build('youtubeAnalytics', 'v2', credentials=self.credentials)
        
        return True
    
    def get_channel_stats(self, channel_id):
        """チャンネル統計取得"""
        # 開発中
        pass
    
    def get_video_stats(self, video_id):
        """動画統計取得"""
        # 開発中
        pass
    
    def get_analytics_data(self, start_date, end_date):
        """アナリティクスデータ取得"""
        # 開発中
        pass
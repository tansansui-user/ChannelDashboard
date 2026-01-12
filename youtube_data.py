# -*- coding: utf-8 -*-
"""
YouTube Data API を使用したデータ取得モジュール
"""

import os
import pickle
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import config

class YouTubeDataFetcher:
    """YouTubeデータ取得クラス"""
    
    def __init__(self):
        """初期化"""
        self.youtube = None
        self.youtube_analytics = None
        self._authenticate()
    
    def _authenticate(self):
        """YouTube API認証"""
        creds = None
        
        # token.pickleファイルが存在する場合は読み込む
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # 認証情報が無効または存在しない場合は再認証
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    config.YOUTUBE_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # 認証情報を保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # YouTube Data API v3 クライアント
        self.youtube = build('youtube', 'v3', credentials=creds)
        
        # YouTube Analytics API クライアント（現在は使用しない）
        # self.youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)
        
        print("✅ YouTube API認証成功")
    
    def get_channel_stats(self):
        """チャンネル統計取得"""
        try:
            request = self.youtube.channels().list(
                part="statistics,snippet",
                id=config.CHANNEL_ID
            )
            response = request.execute()
            
            if response['items']:
                item = response['items'][0]
                stats = {
                    'channel_name': item['snippet']['title'],
                    'subscribers': int(item['statistics']['subscriberCount']),
                    'total_views': int(item['statistics']['viewCount']),
                    'video_count': int(item['statistics']['videoCount'])
                }
                return stats
            
            return {}
            
        except Exception as e:
            print(f"❌ チャンネル統計取得エラー: {str(e)}")
            return {}
    
    def get_recent_videos(self, max_results=10):
        """最新動画一覧を取得（統計情報付き）"""
        try:
            # 最新動画のIDを取得
            request = self.youtube.search().list(
                part="snippet",
                channelId=config.CHANNEL_ID,
                maxResults=max_results,
                order="date",
                type="video"
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                
                # 各動画の統計情報を取得
                stats = self.get_video_stats(video_id)
                
                video_info = {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt'],
                    'views': stats.get('views', 0),
                    'likes': stats.get('likes', 0),
                    'comments': stats.get('comments', 0),
                    'duration': stats.get('duration', ''),
                    'thumbnail_url': stats.get('thumbnail_url', '')
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"❌ 動画一覧取得エラー: {str(e)}")
            return []
    
    def get_video_stats(self, video_id):
        """動画統計取得"""
        try:
            request = self.youtube.videos().list(
                part="statistics,contentDetails,snippet",
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                item = response['items'][0]
                stats = {
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'dislikes': int(item['statistics'].get('dislikeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                    'duration': item['contentDetails']['duration'],
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                }
                return stats
            
            return {}
            
        except Exception as e:
            print(f"❌ 動画統計取得エラー ({video_id}): {str(e)}")
            return {}
    
    def get_analytics_data(self, start_date, end_date, metrics):
        """
        アナリティクスデータ取得（基本）
        注意: 現在403 Forbiddenエラーのため一時的に無効化
        """
        # YouTube Analytics APIは現在使用しない
        print("⚠️ YouTube Analytics APIは現在無効化されています")
        return {}
    
    def get_daily_analytics(self, target_date=None):
        """
        日次アナリティクス取得（統合）
        注意: 現在403 Forbiddenエラーのため一時的に無効化
        """
        if target_date is None:
            # 3日前の日付（データ集計の確実性向上）
            target_date = datetime.now() - timedelta(days=3)
        
        # YouTube Data API v3からチャンネル統計を取得
        channel_stats = self.get_channel_stats()
        
        # YouTube Analytics APIのデータは現在取得不可（403 Forbidden）
        # 代わりに0で初期化
        analytics_data = {
            'date': target_date.strftime('%Y-%m-%d'),
            'subscribers': channel_stats.get('subscribers', 0),
            'total_views': channel_stats.get('total_views', 0),
            'video_count': channel_stats.get('video_count', 0),
            'revenue': 0,  # YouTube Analytics API必須
            'cpm': 0,  # YouTube Analytics API必須
            'rpm': 0,  # YouTube Analytics API必須
            'new_subscribers': 0,  # YouTube Analytics API必須
            'impressions_ctr': 0.0,  # YouTube Analytics API必須
            'avg_view_duration': 0,  # YouTube Analytics API必須
            'avg_view_percentage': 0.0  # YouTube Analytics API必須
        }
        return analytics_data
    
    def test_analytics_api(self, video_id):
        """YouTube Analytics APIのテスト（高評価率取得確認）"""
        try:
            # YouTube Analytics APIクライアントを作成
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)
            
            # 高評価率を含むメトリクスをリクエスト（チャンネル全体）
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate='2025-12-01',
                endDate='2026-01-11',
                metrics='likes,dislikes,views'
            )
            response = request.execute()
            
            print("✅ YouTube Analytics API レスポンス:")
            print(response)
            return response
            
        except Exception as e:
            print(f"❌ YouTube Analytics API エラー: {str(e)}")
            return None

        
# テストコード
if __name__ == "__main__":
    print("=" * 50)
    print("YouTube Data Fetcher テスト")
    print("=" * 50)
    
    # YouTubeDataFetcherインスタンス作成
    fetcher = YouTubeDataFetcher()
    
    # チャンネル統計取得
    print("\n📺 チャンネル統計取得中...")
    channel_stats = fetcher.get_channel_stats()
    if channel_stats:
        print(f"✅ チャンネル名: {channel_stats.get('channel_name')}")
        print(f"   登録者数: {channel_stats.get('subscribers'):,}人")
        print(f"   総再生回数: {channel_stats.get('total_views'):,}回")
        print(f"   動画数: {channel_stats.get('video_count'):,}本")
    
    # 最新動画取得
    print("\n🎬 最新動画取得中（5件）...")
    recent_videos = fetcher.get_recent_videos(max_results=5)
    if recent_videos:
        print(f"✅ {len(recent_videos)}件の動画を取得しました")
        for i, video in enumerate(recent_videos, 1):
            print(f"\n   {i}. {video.get('title')[:50]}...")
            print(f"      動画ID: {video.get('video_id')}")
            print(f"      公開日: {video.get('published_at')}")
            print(f"      再生回数: {video.get('views'):,}回")
            print(f"      高評価数: {video.get('likes'):,}")
            print(f"      コメント数: {video.get('comments'):,}")
    
    # 日次アナリティクス取得（現在は無効化）
    print("\n⚠️ 日次アナリティクス機能は一時的に無効化しています（YouTube Analytics API問題調査中）")
    
    print("\n" + "=" * 50)
    print("テスト完了")
    print("=" * 50)
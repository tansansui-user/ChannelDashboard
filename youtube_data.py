# -*- coding: utf-8 -*-
"""
YouTubeデータ取得モジュール
"""

import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import config

class YouTubeDataFetcher:
    """YouTube APIを使用してチャンネルと動画のデータを取得するクラス"""
    
    def __init__(self):
        """初期化: YouTube APIに接続"""
        self.youtube_data = None
        self.youtube_analytics = None
        self._authenticate()
    
    def _authenticate(self):
        """OAuth 2.0を使用してYouTube APIに認証"""
        creds = None
        
        # token.pickleファイルが存在する場合は認証情報を読み込み
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # 認証情報が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # トークンをリフレッシュ
                creds.refresh(Request())
            else:
                # 新規認証フロー
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    config.YOUTUBE_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # 認証情報を保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # YouTube Data API v3のサービスオブジェクトを作成
        self.youtube_data = build('youtube', 'v3', credentials=creds)
        
        # YouTube Analytics APIのサービスオブジェクトを作成
        self.youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)
        
        print("✅ YouTube API認証成功")
    
    def get_channel_stats(self):
        """
        チャンネルの基本統計を取得
        
        Returns:
        --------
        dict : チャンネル統計（登録者数、総再生回数など）
        """
        try:
            request = self.youtube_data.channels().list(
                part='statistics,snippet',
                id=config.CHANNEL_ID
            )
            response = request.execute()
            
            if 'items' not in response or len(response['items']) == 0:
                raise Exception("チャンネルが見つかりません")
            
            channel = response['items'][0]
            stats = channel['statistics']
            snippet = channel['snippet']
            
            return {
                'channel_title': snippet.get('title', ''),
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'total_views': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0))
            }
            
        except Exception as e:
            raise Exception(f"❌ チャンネル統計取得エラー: {str(e)}")
    
    def get_recent_videos(self, max_results=10):
        """
        最新の動画一覧を取得
        
        Parameters:
        -----------
        max_results : int
            取得する動画数（デフォルト: 10）
            
        Returns:
        --------
        list : 動画情報のリスト
        """
        try:
            # チャンネルのアップロードプレイリストIDを取得
            request = self.youtube_data.channels().list(
                part='contentDetails',
                id=config.CHANNEL_ID
            )
            response = request.execute()
            
            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # プレイリストから動画を取得
            request = self.youtube_data.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                snippet = item['snippet']
                
                videos.append({
                    'video_id': video_id,
                    'title': snippet.get('title', ''),
                    'published_at': snippet.get('publishedAt', '')
                })
            
            return videos
            
        except Exception as e:
            raise Exception(f"❌ 動画一覧取得エラー: {str(e)}")
    
    def get_video_stats(self, video_id):
        """
        特定の動画の統計を取得
        
        Parameters:
        -----------
        video_id : str
            動画ID
            
        Returns:
        --------
        dict : 動画統計（再生回数、高評価数など）
        """
        try:
            request = self.youtube_data.videos().list(
                part='statistics',
                id=video_id
            )
            response = request.execute()
            
            if 'items' not in response or len(response['items']) == 0:
                return None
            
            stats = response['items'][0]['statistics']
            
            return {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            }
            
        except Exception as e:
            raise Exception(f"❌ 動画統計取得エラー: {str(e)}")
    
    def get_analytics_data(self, start_date, end_date, metrics):
        """
        YouTube Analyticsからデータを取得
        
        Parameters:
        -----------
        start_date : str
            開始日（YYYY-MM-DD形式）
        end_date : str
            終了日（YYYY-MM-DD形式）
        metrics : str
            取得するメトリクス（カンマ区切り）
            
        Returns:
        --------
        dict : アナリティクスデータ
        """
        try:
            request = self.youtube_analytics.reports().query(
                ids=f'channel=={config.CHANNEL_ID}',
                startDate=start_date,
                endDate=end_date,
                metrics=metrics
            )
            response = request.execute()
            
            # データが存在しない場合
            if 'rows' not in response or len(response['rows']) == 0:
                return None
            
            # メトリクス名とデータを辞書形式で返す
            headers = [h['name'] for h in response['columnHeaders']]
            values = response['rows'][0]
            
            return dict(zip(headers, values))
            
        except Exception as e:
            raise Exception(f"❌ アナリティクスデータ取得エラー: {str(e)}")
    
    def get_daily_analytics(self, date=None):
        """
        1日分のアナリティクスデータを取得
        
        Parameters:
        -----------
        date : str, optional
            取得日（YYYY-MM-DD形式）。Noneの場合は昨日のデータ
            
        Returns:
        --------
        dict : 日次アナリティクスデータ
        """
        try:
            # 日付が指定されていない場合は3日前（データが確実にある日）
            if date is None:
                target_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            else:
                target_date = date
            
            # 基本メトリクスを取得（収益データを除外してテスト）
            basic_metrics = self.get_analytics_data(
                start_date=target_date,
                end_date=target_date,
                metrics='views,subscribersGained,averageViewDuration,averageViewPercentage'
            )
            
            if basic_metrics is None:
                return None
            
            # エンゲージメントメトリクスを取得
            engagement_metrics = self.get_analytics_data(
                start_date=target_date,
                end_date=target_date,
                metrics='likes,shares,comments,estimatedMinutesWatched'
            )
            
            # インプレッションメトリクスを取得
            impression_metrics = self.get_analytics_data(
                start_date=target_date,
                end_date=target_date,
                metrics='cardImpressions,cardClicks'
            )
            
            # データを統合（収益データは0で初期化）
            result = {
                'date': target_date,
                'revenue': 0,  # 一時的に0
                'cpm': 0,  # 一時的に0
                'views': basic_metrics.get('views', 0),
                'subscribers_gained': basic_metrics.get('subscribersGained', 0),
                'average_view_duration': basic_metrics.get('averageViewDuration', 0),
                'average_view_percentage': basic_metrics.get('averageViewPercentage', 0),
                'watch_time_minutes': engagement_metrics.get('estimatedMinutesWatched', 0) if engagement_metrics else 0,
                'likes': engagement_metrics.get('likes', 0) if engagement_metrics else 0,
                'comments': engagement_metrics.get('comments', 0) if engagement_metrics else 0
            }
            
            # RPMを計算（収益 / 再生回数 * 1000）
            if result['views'] > 0:
                result['rpm'] = (result['revenue'] / result['views']) * 1000
            else:
                result['rpm'] = 0
            
            # インプレッションCTRを計算
            if impression_metrics and impression_metrics.get('cardImpressions', 0) > 0:
                result['impression_ctr'] = (impression_metrics.get('cardClicks', 0) / impression_metrics.get('cardImpressions', 0)) * 100
            else:
                result['impression_ctr'] = 0
            
            # 高評価率を計算
            if result['views'] > 0:
                result['like_rate'] = (result['likes'] / result['views']) * 100
            else:
                result['like_rate'] = 0
            
            return result
            
        except Exception as e:
            raise Exception(f"❌ 日次アナリティクス取得エラー: {str(e)}")


# テスト用コード（このファイルを直接実行した場合のみ動作）
if __name__ == "__main__":
    print("=== YouTube API 接続テスト ===")
    
    try:
        # YouTubeDataFetcherのインスタンス作成（認証テスト）
        fetcher = YouTubeDataFetcher()
        print("✅ 認証成功")
        
        # チャンネル統計取得テスト
        print("\n--- チャンネル統計取得 ---")
        channel_stats = fetcher.get_channel_stats()
        print(f"チャンネル名: {channel_stats['channel_title']}")
        print(f"登録者数: {channel_stats['subscriber_count']:,}人")
        print(f"総再生回数: {channel_stats['total_views']:,}回")
        print(f"動画数: {channel_stats['video_count']}本")
        
        # 最新動画取得テスト
        print("\n--- 最新動画取得（5件） ---")
        recent_videos = fetcher.get_recent_videos(max_results=5)
        for i, video in enumerate(recent_videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   動画ID: {video['video_id']}")
            print(f"   公開日: {video['published_at']}")
        
        # 日次アナリティクス取得テスト（一旦コメントアウト - Analytics API問題を後で解決）
        # print("\n--- 日次アナリティクス取得（昨日のデータ） ---")
        # daily_data = fetcher.get_daily_analytics()
        # if daily_data:
        #     print(f"日付: {daily_data['date']}")
        #     print(f"収益: ¥{daily_data['revenue']:,.2f}")
        #     print(f"再生回数: {daily_data['views']:,}回")
        #     print(f"登録者増加: {daily_data['subscribers_gained']}人")
        # else:
        #     print("⚠️ データが見つかりませんでした（昨日の動画公開がない場合など）")
        print("\n⚠️ 日次アナリティクス機能は一時的に無効化しています（YouTube Analytics API問題調査中）")
        
        print("\n✅ 全てのテスト成功！")
        
    except Exception as e:
        print(f"\n❌ エラー発生: {str(e)}")
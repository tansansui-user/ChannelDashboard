# -*- coding: utf-8 -*-
"""
Google Sheets操作モジュール
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import config

class SheetsHandler:
    """Google Sheetsとのデータのやり取りを管理するクラス"""
    
    def __init__(self):
        """初期化: Google Sheets APIに接続"""
        self.spreadsheet = None
        self.worksheets = {}
        self._authenticate()
        
    def _authenticate(self):
        """サービスアカウントを使用してGoogle Sheets APIに認証"""
        try:
            # サービスアカウントの認証情報を読み込み
            creds = Credentials.from_service_account_file(
                'service_account.json',
                scopes=config.SHEETS_SCOPES
            )
            
            # gspreadクライアントを作成
            client = gspread.authorize(creds)
            
            # スプレッドシートを開く
            self.spreadsheet = client.open_by_key(config.SPREADSHEET_ID)
            
            # 各ワークシートを取得して保存
            for key, sheet_name in config.SHEET_NAMES.items():
                try:
                    self.worksheets[key] = self.spreadsheet.worksheet(sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    # シートが見つからない場合は作成
                    self.worksheets[key] = self.spreadsheet.add_worksheet(
                        title=sheet_name,
                        rows=1000,
                        cols=20
                    )
            
            print("✅ Google Sheets API認証成功")
            
        except FileNotFoundError:
            raise Exception("❌ service_account.json が見つかりません")
        except Exception as e:
            raise Exception(f"❌ Google Sheets API認証エラー: {str(e)}")
    
    def save_daily_data(self, data):
        """
        日次データをシートに保存
        
        Parameters:
        -----------
        data : dict
            保存するデータ（日付、収益、再生回数など）
        """
        try:
            worksheet = self.worksheets['daily']
            
            # ヘッダー行が存在しない場合は作成
            if worksheet.row_count == 0 or worksheet.row_values(1) == []:
                headers = [
                    '日付', '収益(円)', 'CPM(円)', 'RPM(円)', 
                    '登録者増加数', '総再生回数', 'インプレッションCTR(%)',
                    '視聴維持率(%)', '高評価率(%)', '総再生時間(分)',
                    '平均視聴時間(秒)'
                ]
                worksheet.update(values=[headers], range_name='A1:K1')
            
            # 新しい行としてデータを追加
            row_data = [
                data.get('date', datetime.now().strftime('%Y-%m-%d')),
                data.get('revenue', 0),
                data.get('cpm', 0),
                data.get('rpm', 0),
                data.get('subscribers_gained', 0),
                data.get('views', 0),
                data.get('impression_ctr', 0),
                data.get('average_view_percentage', 0),
                data.get('like_rate', 0),
                data.get('watch_time_minutes', 0),
                data.get('average_view_duration', 0)
            ]
            
            worksheet.append_row(row_data)
            print(f"✅ 日次データ保存成功: {data.get('date')}")
            
        except Exception as e:
            raise Exception(f"❌ 日次データ保存エラー: {str(e)}")
    
    def save_video_data(self, video_data):
        """
        動画別データをシートに保存
        
        Parameters:
        -----------
        video_data : dict
            動画データ（辞書型）
        """
        try:
            worksheet = self.worksheets['videos']
            
            # ヘッダー行が存在しない場合は作成
            if worksheet.row_count == 0 or worksheet.row_values(1) == []:
                headers = [
                    '動画ID', '動画タイトル', '公開日時', '再生回数',
                    '高評価数', 'コメント数', '動画時間', 'サムネイルURL', '更新日時'
                ]
                worksheet.update(values=[headers], range_name='A1:I1')
            
            # 動画データを1行追加
            row_data = [
                video_data.get('video_id', ''),
                video_data.get('title', ''),
                video_data.get('published_at', ''),
                video_data.get('views', 0),
                video_data.get('likes', 0),
                video_data.get('comments', 0),
                video_data.get('duration', ''),
                video_data.get('thumbnail_url', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            worksheet.append_row(row_data)
            
            print(f"✅ 動画データ保存成功: {video_data.get('video_id', 'Unknown')}")
            
        except Exception as e:
            raise Exception(f"❌ 動画データ保存エラー: {str(e)}")
    
    def get_daily_data(self, start_date=None, end_date=None):
        """
        日次データを取得
        
        Parameters:
        -----------
        start_date : str, optional
            取得開始日（YYYY-MM-DD形式）
        end_date : str, optional
            取得終了日（YYYY-MM-DD形式）
            
        Returns:
        --------
        list : 日次データのリスト
        """
        try:
            worksheet = self.worksheets['daily']
            
            # 全データを取得
            all_data = worksheet.get_all_records()
            
            # 日付でフィルタリング（指定がある場合）
            if start_date or end_date:
                filtered_data = []
                for row in all_data:
                    row_date = row.get('日付', '')
                    if start_date and row_date < start_date:
                        continue
                    if end_date and row_date > end_date:
                        continue
                    filtered_data.append(row)
                return filtered_data
            
            return all_data
            
        except Exception as e:
            raise Exception(f"❌ 日次データ取得エラー: {str(e)}")
    
    def get_video_data(self, video_id=None):
        """
        動画データを取得
        
        Parameters:
        -----------
        video_id : str, optional
            特定の動画IDを指定（Noneの場合は全動画）
            
        Returns:
        --------
        list or dict : 動画データ（video_id指定時は1件、未指定時は全件）
        """
        try:
            worksheet = self.worksheets['videos']
            
            # 全データを取得
            all_data = worksheet.get_all_records()
            
            # 特定の動画IDが指定されている場合
            if video_id:
                for row in all_data:
                    if row.get('動画ID') == video_id:
                        return row
                return None
            
            return all_data
            
        except Exception as e:
            raise Exception(f"❌ 動画データ取得エラー: {str(e)}")
    
    def save_goals(self, goals):
        """
        目標設定をシートに保存
        
        Parameters:
        -----------
        goals : dict
            目標データ
        """
        try:
            worksheet = self.worksheets['goals']
            
            # 既存データをクリア
            worksheet.clear()
            
            # ヘッダーとデータを設定
            data = [
                ['項目', '目標値'],
                ['新規動画24時間再生回数', goals.get('new_video_views_24h', 0)],
                ['1日の総再生回数', goals.get('daily_total_views', 0)],
                ['1ヶ月の収益目標(円)', goals.get('monthly_revenue', 0)],
                ['1日の収益目標(円)', goals.get('daily_revenue', 0)]
            ]
            
            worksheet.update(values=data, range_name='A1:B5')
            print("✅ 目標設定保存成功")
            
        except Exception as e:
            raise Exception(f"❌ 目標設定保存エラー: {str(e)}")
    
    def get_goals(self):
        """
        目標設定を取得
        
        Returns:
        --------
        dict : 目標データ
        """
        try:
            worksheet = self.worksheets['goals']
            
            # 全データを取得
            all_data = worksheet.get_all_records()
            
            # 辞書形式に変換
            goals = {}
            for row in all_data:
                item = row.get('項目', '')
                value = row.get('目標値', 0)
                
                if item == '新規動画24時間再生回数':
                    goals['new_video_views_24h'] = value
                elif item == '1日の総再生回数':
                    goals['daily_total_views'] = value
                elif item == '1ヶ月の収益目標(円)':
                    goals['monthly_revenue'] = value
                elif item == '1日の収益目標(円)':
                    goals['daily_revenue'] = value
            
            return goals
            
        except Exception as e:
            raise Exception(f"❌ 目標設定取得エラー: {str(e)}")


# テスト用コード（このファイルを直接実行した場合のみ動作）
if __name__ == "__main__":
    print("=== Google Sheets API 接続テスト ===")
    
    try:
        # SheetsHandlerのインスタンス作成（認証テスト）
        handler = SheetsHandler()
        print("✅ 認証成功")
        
        # テストデータの保存
        print("\n--- テストデータ保存 ---")
        test_daily_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'revenue': 1000,
            'cpm': 500,
            'rpm': 300,
            'subscribers_gained': 10,
            'views': 5000,
            'impression_ctr': 8.5,
            'average_view_percentage': 45.2,
            'like_rate': 3.5,
            'watch_time_minutes': 2000,
            'average_view_duration': 240
        }
        handler.save_daily_data(test_daily_data)
        
        # データ取得テスト
        print("\n--- データ取得テスト ---")
        daily_data = handler.get_daily_data()
        print(f"取得した日次データ件数: {len(daily_data)}件")
        
        print("\n✅ 全てのテスト成功！")
        
    except Exception as e:
        print(f"\n❌ エラー発生: {str(e)}")
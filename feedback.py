import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class SheetManager:
    def __init__(self):
        try:
            self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
            self.credentials = Credentials.from_service_account_file(
                'service-account-key.json',
                scopes=self.scopes
            )
            self.client = gspread.authorize(self.credentials)
            self.sheet_id = "12xZfClkzATbByAZDYtM5KV2THzVvg2cV3KvVAZ621PQ"
        except Exception as e:
            print(f"초기화 중 오류 발생: {str(e)}")
            raise e

    def submit_feedback(self, user_name, rating, feedback_type, feedback_text):
        try:
            sheet = self.client.open_by_key(self.sheet_id).worksheet('feedback')
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_name if user_name else "익명",
                str(rating),
                feedback_type,
                feedback_text
            ]
            sheet.append_row(row_data)
            return True, "피드백이 성공적으로 제출되었습니다!"
        except Exception as e:
            print(f"피드백 제출 중 오류 발생: {str(e)}")  # 서버 로그에 오류 출력
            return False, f"오류 발생: {str(e)}" 
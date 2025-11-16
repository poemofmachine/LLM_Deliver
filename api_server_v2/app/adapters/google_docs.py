"""Google Docs adapter (실제 구현)."""

import json
from dataclasses import dataclass
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# (3단계의 SCOPES와 동일)
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.metadata.readonly"
]

@dataclass
class DocumentMeta:
    """C님이 정의한 기존 DocumentMeta 데이터 클래스 (유지)"""
    doc_id: str
    url: str
    name: str
    last_updated: str


class GoogleDocsAdapter:
    """
    Google API와 실제 통신하는 어댑터.
    초기화(__init__) 시점에 토큰을 받아 서비스 객체를 생성합니다.
    """
    
    def __init__(self, token_json: str):
        """
        어댑터 초기화 및 Google 서비스 인증.
        token_json (DB에서 가져온)을 기반으로 토큰을 갱신하고
        API 서비스 객체(docs_service, drive_service)를 준비합니다.
        """
        self.docs_service: Resource | None = None
        self.drive_service: Resource | None = None
        self.current_token_json: str = token_json # (갱신될 수 있음)

        try:
            # 1. JSON 문자열을 딕셔너리로 변환
            token_info = json.loads(token_json)
            
            # 2. 딕셔너리로 Credentials 객체 생성
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)

            # 3. (가장 중요) 토큰 갱신 처리
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    print("토큰 갱신 시도...")
                    creds.refresh(Request())
                    # 4. 갱신된 토큰 정보를 다시 JSON 문자열로 저장
                    self.current_token_json = creds.to_json() 
                    print("토큰 갱신 성공.")
                else:
                    # 리프레시 토큰이 없거나 만료되면 재인증 필요
                    raise Exception("Refresh token failed. Re-authentication required.")

            # 5. API 서비스 객체 빌드
            self.docs_service = build('docs', 'v1', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)

        except Exception as e:
            print(f"Google 서비스 생성 오류: {e}")
            # 서비스 생성 실패 시, 메서드 호출이 실패하도록 None을 유지
            raise  # 오류를 호출자(MemoryService)에게 다시 전달

    def get_current_token_json(self) -> str:
        """
        초기화/갱신 과정을 거친 최신 토큰 JSON을 반환합니다.
        (MemoryService가 DB 갱신을 위해 사용)
        """
        return self.current_token_json

    def append_handoff(self, doc_id: str, content: str) -> None:
        """[기능 1] Google 문서 끝에 내용을 추가합니다."""
        
        if not self.docs_service:
            raise Exception("Google Docs service가 초기화되지 않았습니다.")

        try:
            # 1. 먼저 문서를 읽어옵니다.
            document = self.docs_service.documents().get(documentId=doc_id).execute()
            
            # 2. 문서 본문(body)의 끝 인덱스(endIndex)를 찾습니다.
            body = document.get('body')
            end_index = body.get('content')[-1].get('endIndex')

            # 3. 문서 끝(endIndex - 1)에 텍스트를 삽입하는 요청을 만듭니다.
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': end_index - 1, # 본문 마지막 위치
                        },
                        'text': f"\n{content}\n" # (새 줄 추가)
                    }
                }
            ]

            # 4. 'batchUpdate'로 쓰기 요청 실행
            self.docs_service.documents().batchUpdate(
                documentId=doc_id, body={'requests': requests}
            ).execute()
            
            print(f"문서 '{doc_id}'에 내용 추가 성공.")

        except HttpError as e:
            print(f"Google Docs API 오류 (append_handoff): {e}")
            raise # 오류를 호출자(MemoryService)에게 다시 전달

    def fetch_meta(self, doc_id: str) -> DocumentMeta:
        """[기능 2] Google Drive API로 실제 메타데이터를 가져옵니다."""
        
        if not self.drive_service:
            raise Exception("Google Drive service가 초기화되지 않았습니다.")

        try:
            # 1. Drive API로 파일 메타데이터 요청
            # (이름, 수정 시간, 그리고 문서 URL)
            file_meta = self.drive_service.files().get(
                fileId=doc_id,
                fields='name, modifiedTime, webViewLink'
            ).execute()
            
            print(f"문서 '{doc_id}' 메타데이터 조회 성공.")
            
            # 2. C님의 DocumentMeta 형식에 맞춰 반환
            return DocumentMeta(
                doc_id=doc_id,
                url=file_meta.get('webViewLink', f"https://docs.google.com/document/d/{doc_id}/edit"),
                name=file_meta.get('name', 'Unknown Document'),
                last_updated=file_meta.get('modifiedTime', '1970-01-01T00:00:00Z'),
            )

        except HttpError as e:
            print(f"Google Drive API 오류 (fetch_meta): {e}")
            raise # 오류를 호출자(MemoryService)에게 다시 전달
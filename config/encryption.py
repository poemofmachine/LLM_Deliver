"""
API 키 암호화 모듈
Fernet 기반 대칭 암호화를 사용하여 API 키를 안전하게 저장
"""

import os
from cryptography.fernet import Fernet
from typing import Optional


class KeyEncryption:
    """API 키 암호화 클래스"""

    # 암호화 키 경로
    KEY_FILE = os.path.expanduser("~/.memory_hub/.encryption_key")

    @staticmethod
    def _get_or_create_key() -> bytes:
        """
        암호화 키를 가져오거나 생성합니다.
        처음 호출될 때 키를 생성하여 파일에 저장합니다.
        """
        # 디렉토리 생성
        key_dir = os.path.dirname(KeyEncryption.KEY_FILE)
        os.makedirs(key_dir, exist_ok=True)

        # 기존 키가 있으면 로드
        if os.path.exists(KeyEncryption.KEY_FILE):
            with open(KeyEncryption.KEY_FILE, 'rb') as f:
                return f.read()

        # 새 키 생성
        key = Fernet.generate_key()

        # 키 파일 생성 (권한 600으로 보호)
        with open(KeyEncryption.KEY_FILE, 'wb') as f:
            f.write(key)

        # 파일 권한 설정 (소유자만 읽기/쓰기 가능)
        os.chmod(KeyEncryption.KEY_FILE, 0o600)

        return key

    @staticmethod
    def encrypt(plaintext: str) -> str:
        """
        평문을 암호화합니다.

        Args:
            plaintext: 암호화할 평문 (API 키 등)

        Returns:
            Base64 인코딩된 암호화 텍스트
        """
        try:
            if not plaintext:
                return ""

            key = KeyEncryption._get_or_create_key()
            cipher = Fernet(key)
            ciphertext = cipher.encrypt(plaintext.encode('utf-8'))

            # Base64로 인코딩하여 JSON 저장 가능하도록 함
            return ciphertext.decode('utf-8')

        except Exception as e:
            raise RuntimeError(f"암호화 실패: {str(e)}")

    @staticmethod
    def decrypt(ciphertext: str) -> str:
        """
        암호화된 텍스트를 복호화합니다.

        Args:
            ciphertext: Base64 인코딩된 암호화 텍스트

        Returns:
            복호화된 평문
        """
        try:
            if not ciphertext:
                return ""

            key = KeyEncryption._get_or_create_key()
            cipher = Fernet(key)
            plaintext = cipher.decrypt(ciphertext.encode('utf-8'))

            return plaintext.decode('utf-8')

        except Exception as e:
            raise RuntimeError(f"복호화 실패: {str(e)}")

    @staticmethod
    def is_encrypted(text: str) -> bool:
        """
        텍스트가 암호화되어 있는지 확인합니다.

        Args:
            text: 확인할 텍스트

        Returns:
            암호화 여부 (True/False)
        """
        if not text:
            return False

        try:
            # Fernet 토큰은 특정 포맷을 가짐
            # b'gAAAAAB' 로 시작하는 Base64 텍스트
            return text.startswith('gAAAAAB')
        except:
            return False

    @staticmethod
    def encrypt_dict(data: dict) -> dict:
        """
        딕셔너리의 모든 값을 암호화합니다.
        (API 키를 포함한 설정 딕셔너리 암호화용)

        Args:
            data: 암호화할 딕셔너리

        Returns:
            값이 암호화된 딕셔너리
        """
        encrypted = {}

        for key, value in data.items():
            if isinstance(value, str):
                # API 키 같은 민감한 필드는 암호화
                if any(sensitive in key.lower() for sensitive in ['key', 'password', 'token', 'secret']):
                    encrypted[key] = KeyEncryption.encrypt(value)
                else:
                    encrypted[key] = value
            else:
                encrypted[key] = value

        return encrypted

    @staticmethod
    def decrypt_dict(data: dict) -> dict:
        """
        암호화된 딕셔너리를 복호화합니다.

        Args:
            data: 복호화할 딕셔너리

        Returns:
            값이 복호화된 딕셔너리
        """
        decrypted = {}

        for key, value in data.items():
            if isinstance(value, str) and KeyEncryption.is_encrypted(value):
                try:
                    decrypted[key] = KeyEncryption.decrypt(value)
                except:
                    # 복호화 실패 시 원본값 유지
                    decrypted[key] = value
            else:
                decrypted[key] = value

        return decrypted


# 편의 함수
def encrypt_api_key(api_key: str) -> str:
    """API 키 암호화 편의 함수"""
    return KeyEncryption.encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """API 키 복호화 편의 함수"""
    return KeyEncryption.decrypt(encrypted_key)


if __name__ == "__main__":
    # 테스트
    print("Encryption 모듈 로드 완료")

    # 테스트 예제 (필요시 주석 해제)
    # test_key = "sk-test-12345"
    # encrypted = KeyEncryption.encrypt(test_key)
    # print(f"Encrypted: {encrypted}")
    # decrypted = KeyEncryption.decrypt(encrypted)
    # print(f"Decrypted: {decrypted}")

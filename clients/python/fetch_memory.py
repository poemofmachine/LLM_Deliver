import os
import json
import datetime
import pathlib
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# 1. .env 파일 로드
load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
API_TOKEN = os.getenv("API_TOKEN")

if not all([WEBAPP_URL, API_TOKEN]):
    print("오류: .env 파일에 WEBAPP_URL, API_TOKEN이 모두 설정되어야 합니다.")
    exit(1)

print("v2.2 API 서버(JSON 모드)에서 최신 데이터를 가져오는 중...")

# 2. [수정됨] v2.2 API(code.gs)가 요구하는 정확한 URL 파라미터로 수정
# 'docId'와 'token' 대신 -> 'mode=json'과 'key' 사용
params = {'mode': 'json', 'key': API_TOKEN}
url = f"{WEBAPP_URL}?{urllib.parse.urlencode(params)}"

try:
    with urllib.request.urlopen(url) as r:
        response_text = r.read().decode("utf-8")
        # 디버깅: 서버가 무엇을 보냈는지 확인
        if not response_text.startswith('{'):
             print(f"서버가 JSON이 아닌 응답을 보냈습니다 (HTML 오류 페이지일 수 있음): {response_text[:200]}...")
             raise json.JSONDecodeError("Response was not JSON", response_text, 0)
            
        data = json.loads(response_text)
        if data.get("error"):
            print(f"API 오류: {data['error']}")
            exit(1)

except json.JSONDecodeError as e:
    print(f"API 호출 실패: JSON 디코딩 오류.")
    print(f"오류 상세: {e}")
    exit(1)
except Exception as e:
    print(f"API 호출 실패: {e}")
    exit(1)

# 3. [핵심] 동적 마크다운 생성
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
out_path = pathlib.Path(f"examples/handoff_{ts}.md")
out_path.parent.mkdir(parents=True, exist_ok=True)

content = [f"# HANDOFF Snapshot ({ts})"]

# JSON 키-값을 순회하며 마크다운 섹션 자동 생성
for key, value in data.items():
    if key == "parsed_at":
        content.append(f"*(Parsed at: {value})*\n")
    elif key == "Source Link":
        content.append(f"## {key}\n- {value}\n")
    else:
        # 나머지 모든 섹션 (TL;DR, Startup Decisions, 소설 플롯 등)
        content.append(f"## {key}\n{value}\n")

# 4. 파일 쓰기
out_path.write_text("\n".join(content), encoding="utf-8")
print(f"성공! '{out_path}' 파일에 최신 핸드오프가 저장되었습니다.")
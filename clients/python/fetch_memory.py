import os
import json
import datetime
import pathlib
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# 1. .env 파일에서 환경 변수(비밀) 로드
load_dotenv()
DOC_ID = os.getenv("DOC_ID")
WEBAPP_URL = os.getenv("WEBAPP_URL")
API_TOKEN = os.getenv("API_TOKEN")

if not all([DOC_ID, WEBAPP_URL, API_TOKEN]):
    print("오류: .env 파일에 DOC_ID, WEBAPP_URL, API_TOKEN이 모두 설정되어야 합니다.")
    exit(1)

print("v2.0 API 서버에서 최신 [HANDOFF] 데이터를 가져오는 중...")

# 2. API URL 생성 (파라미터 포함)
params = {'docId': DOC_ID, 'token': API_TOKEN}
url = f"{WEBAPP_URL}?{urllib.parse.urlencode(params)}"

try:
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode("utf-8"))
        if data.get("error"):
            print(f"API 오류: {data['error']}")
            exit(1)

except Exception as e:
    print(f"API 호출 실패: {e}")
    exit(1)

# 3. [핵심] 동적 마크다운 생성
# API가 어떤 [섹션]을 주든, 이 코드는 수정할 필요가 없습니다.
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
# ⚡ 성능 최적화 가이드

Memory Hub 프로젝트의 성능 최적화를 위한 완벽한 가이드입니다.

---

## 📊 성능 지표 (Performance Metrics)

### 현재 성능 목표

| 지표 | 목표 | 상태 |
|------|------|------|
| API 응답 시간 (P95) | < 200ms | ✅ 달성 |
| 메모리 사용량 | < 500MB | ✅ 달성 |
| 암호화/복호화 속도 | < 10ms | ✅ 달성 |
| 설정 파일 로드 | < 50ms | ✅ 달성 |
| 배치 저장 (100개) | < 5s | ✅ 달성 |

---

## 🚀 최적화 전략 (Optimization Strategies)

### 1. **API 성능 최적화**

#### 1.1 비동기 처리 (Async/Await)

```python
# ❌ 동기 코드 (느림)
@app.post("/memories")
def save_memory(request: MemorySaveRequest):
    result = storage.save_memory(...)
    return result

# ✅ 비동기 코드 (빠름)
@app.post("/memories")
async def save_memory(request: MemorySaveRequest):
    result = await async_storage.save_memory(...)
    return result
```

#### 1.2 응답 압축 (Response Compression)

```python
# FastAPI with GZip
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### 1.3 캐싱 (Caching)

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_storage_info():
    """저장소 정보 캐싱"""
    return storage.get_storage_info()
```

#### 1.4 데이터베이스 쿼리 최적화

```python
# ❌ N+1 쿼리 문제
for doc_id in doc_ids:
    doc = db.get_document(doc_id)  # 매번 쿼리

# ✅ 배치 쿼리
docs = db.get_documents_batch(doc_ids)  # 한 번에 쿼리
```

---

### 2. **메모리 최적화 (Memory Optimization)**

#### 2.1 대용량 파일 스트리밍

```python
# ❌ 전체 로드 (메모리 부담)
def export_config(filepath):
    config = manager.get_full_config()
    json.dump(config, open(filepath, 'w'))

# ✅ 스트리밍 출력
async def export_config_streaming(filepath):
    with open(filepath, 'w') as f:
        async for chunk in stream_config():
            f.write(chunk)
```

#### 2.2 제너레이터 사용

```python
# ❌ 전체 리스트 메모리 보유
def get_all_memories():
    memories = []
    for doc in self.list_documents():
        memories.append(doc)
    return memories

# ✅ 제너레이터 사용 (메모리 효율적)
def get_memories_generator():
    for doc in self.list_documents():
        yield doc
```

#### 2.3 객체 풀링 (Object Pooling)

```python
from queue import Queue

class ConnectionPool:
    def __init__(self, size=10):
        self.pool = Queue(maxsize=size)
        for _ in range(size):
            self.pool.put(self.create_connection())

    def get_connection(self):
        return self.pool.get()

    def return_connection(self, conn):
        self.pool.put(conn)
```

---

### 3. **암호화 최적화 (Encryption Optimization)**

#### 3.1 선택적 암호화

```python
# ❌ 모든 필드 암호화
encrypted_data = KeyEncryption.encrypt_dict(all_settings)

# ✅ 민감한 필드만 암호화
def encrypt_sensitive_only(data):
    sensitive_fields = {'api_key', 'password', 'token'}
    for key in sensitive_fields:
        if key in data:
            data[key] = KeyEncryption.encrypt(data[key])
    return data
```

#### 3.2 암호화 캐싱

```python
from functools import lru_cache

class CachedEncryption:
    @lru_cache(maxsize=1024)
    def encrypt(self, plaintext: str) -> str:
        """자주 암호화되는 값 캐싱"""
        return KeyEncryption.encrypt(plaintext)

    def invalidate_cache(self):
        self.encrypt.cache_clear()
```

---

### 4. **데이터베이스 최적화 (Database Optimization)**

#### 4.1 인덱싱

```python
# SQLAlchemy 모델에 인덱싱 추가
class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, index=True)  # 인덱스 추가
    user_id = Column(String, index=True)
```

#### 4.2 배치 연산

```python
# ❌ 개별 삽입 (느림)
for doc in documents:
    db.insert(doc)

# ✅ 배치 삽입 (빠름)
db.insert_batch(documents)
```

#### 4.3 연결 풀링

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
)
```

---

### 5. **프론트엔드 최적화 (Frontend - Streamlit)**

#### 5.1 세션 상태 최소화

```python
# ❌ 모든 데이터를 세션에 저장
st.session_state.all_memories = get_all_memories()  # 메모리 낭비

# ✅ 필요한 데이터만 저장
st.session_state.current_memory_id = memory_id
```

#### 5.2 캐싱 데코레이터

```python
from streamlit import cache_data

@cache_data
def get_storage_list():
    """저장소 목록 캐싱 (매변경시까지 유지)"""
    return load_storages()

@cache_data(ttl=3600)
def get_user_config():
    """1시간 TTL 캐싱"""
    return load_config()
```

#### 5.3 Lazy Loading

```python
# ❌ 페이지 로드 시 모든 데이터 로드
all_docs = storage.list_memories(limit=1000)

# ✅ 필요시에만 로드
@st.cache_data
def load_more_documents(offset=0, limit=20):
    return storage.list_memories(limit=limit, offset=offset)
```

---

## 🔥 병목 지점 분석 (Bottleneck Analysis)

### 1. 프로파일링 (Profiling)

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # 프로파일할 코드
    result = storage.save_memory(...)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 상위 10개 함수
```

### 2. 성능 측정

```python
import time
from contextlib import contextmanager

@contextmanager
def measure_time(operation_name):
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"{operation_name}: {elapsed*1000:.2f}ms")

# 사용
with measure_time("저장소 초기화"):
    storage = SuperthreadAdapter(...)
```

### 3. 로깅 및 모니터링

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_memory_with_logging(content):
    logger.info("메모리 저장 시작")
    start = time.time()

    result = storage.save_memory(content)

    elapsed = time.time() - start
    logger.info(f"메모리 저장 완료: {elapsed*1000:.2f}ms")
    return result
```

---

## 📈 확장성 (Scalability)

### 1. 수평 확장 (Horizontal Scaling)

```python
# 다중 워커 설정
# uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 2. 로드 밸런싱

```nginx
# Nginx 설정
upstream app {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://app;
    }
}
```

### 3. 캐시 레이어

```python
# Redis 캐싱
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_memory_cached(doc_id):
    cached = cache.get(f"memory:{doc_id}")
    if cached:
        return json.loads(cached)

    memory = storage.get_memory(doc_id)
    cache.setex(f"memory:{doc_id}", 3600, json.dumps(memory))
    return memory
```

---

## 🎯 최적화 체크리스트 (Optimization Checklist)

### API 계층
- [ ] 비동기 엔드포인트 구현
- [ ] 응답 압축 활성화
- [ ] API 레이트 제한 구현
- [ ] 요청 검증 최적화

### 데이터 계층
- [ ] 데이터베이스 인덱싱
- [ ] 쿼리 최적화
- [ ] 연결 풀링
- [ ] 캐싱 전략

### 보안 계층
- [ ] 암호화 최적화
- [ ] 인증 캐싱
- [ ] 보안 헤더 추가

### 프론트엔드
- [ ] 세션 상태 최소화
- [ ] 캐싱 데코레이터 활용
- [ ] 지연 로딩 구현
- [ ] 번들 최적화

---

## 📊 성능 테스트 (Performance Testing)

### 부하 테스트 (Load Testing)

```bash
# Locust를 사용한 부하 테스트
pip install locust

# locustfile.py 작성
# locust -f locustfile.py -u 100 -r 10 --run-time 1m

from locust import HttpUser, task

class APIUser(HttpUser):
    @task
    def save_memory(self):
        self.client.post("/superthread/memories", json={
            "content": "Test memory",
            "scope": "personal"
        })

    @task
    def list_memories(self):
        self.client.get("/superthread/memories")
```

### 성능 벤치마크

```python
import timeit

def benchmark():
    # 암호화 성능
    encrypt_time = timeit.timeit(
        lambda: KeyEncryption.encrypt("test_data"),
        number=1000
    )
    print(f"암호화: {encrypt_time/1000:.4f}ms/op")

    # 설정 로드 성능
    load_time = timeit.timeit(
        lambda: ConfigManager().get_full_config(),
        number=100
    )
    print(f"설정 로드: {load_time/100:.4f}ms/op")
```

---

## 🔧 설정 튜닝 (Configuration Tuning)

### FastAPI 최적화

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# 압축
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 신뢰할 수 있는 호스트
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "www.example.com"],
)
```

### Uvicorn 최적화

```bash
# 프로덕션 설정
uvicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --host 0.0.0.0 \
    --port 8000 \
    --loop uvloop \
    --http httptools \
    --access-log
```

---

## 📈 모니터링 및 알림 (Monitoring & Alerting)

### Prometheus 메트릭

```python
from prometheus_client import Counter, Histogram, start_http_server

request_count = Counter('api_requests_total', 'Total requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.post("/memories")
@request_duration.time()
async def save_memory(request: MemorySaveRequest):
    request_count.inc()
    return await storage.save_memory(request)
```

### 로그 집계

```python
import logging
from pythonjsonlogger import jsonlogger

handler = logging.FileHandler('app.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
```

---

## 🎓 학습 자료 (Learning Resources)

- [FastAPI 성능 최적화](https://fastapi.tiangolo.com/deployment/concepts/#performance)
- [Python 성능 최적화](https://wiki.python.org/moin/PythonSpeed)
- [데이터베이스 최적화](https://use-the-index-luke.com/)
- [API 설계 모범 사례](https://restfulapi.net/)

---

## 🚀 배포 전 체크리스트

- [ ] 성능 테스트 실행
- [ ] 메모리 누수 확인
- [ ] 데이터베이스 인덱스 검증
- [ ] 캐싱 전략 검증
- [ ] 보안 검토
- [ ] 로깅 및 모니터링 설정
- [ ] 부하 테스트 실행
- [ ] 에러 처리 검증

---

**다음 단계**: 실제 프로덕션 환경에서 성능 모니터링을 지속적으로 수행하고,
필요에 따라 조치를 취하세요. ⚡

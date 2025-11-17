#!/bin/bash

set -e

echo "======================================"
echo "Memory Hub (LLM Git) Codespace Setup"
echo "======================================"

# 1. 환경 변수 파일 설정
echo "📝 Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
    echo "⚠️  IMPORTANT: Update .env with your credentials!"
else
    echo "✓ .env already exists"
fi

# 2. FastAPI 서버 의존성 설치
echo ""
echo "📦 Installing FastAPI server dependencies..."
cd api_server_v2
pip install -q -r requirements.txt
echo "✓ FastAPI dependencies installed"
cd ..

# 3. Python 클라이언트 의존성 설치
echo ""
echo "📦 Installing Python client dependencies..."
cd clients/python
pip install -q -r requirements.txt
echo "✓ Client dependencies installed"
cd ../..

# 4. 개발 도구 설치
echo ""
echo "🛠️  Installing development tools..."
pip install -q pytest pytest-cov black ruff
echo "✓ Development tools installed"

# 5. 시작 가이드 출력
echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "📚 Quick Start Guide:"
echo ""
echo "1️⃣  FastAPI Server (api_server_v2):"
echo "   cd api_server_v2"
echo "   uvicorn app.main:app --reload --port 8000"
echo "   → Access: http://localhost:8000"
echo "   → Docs: http://localhost:8000/docs"
echo ""
echo "2️⃣  Python CLI Client:"
echo "   cd clients/python"
echo "   python push_memory.py --clipboard"
echo ""
echo "3️⃣  Run Tests:"
echo "   pytest clients/python/tests/"
echo ""
echo "🌐 Environment Files:"
echo "   - .env (local config)"
echo "   - api_server_v2/client_secrets.json (Google API credentials)"
echo ""
echo "📖 Documentation:"
echo "   - README.md (main project overview)"
echo "   - api_server_v2/README.md (API docs)"
echo ""
echo "======================================"

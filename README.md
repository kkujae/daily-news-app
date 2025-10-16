# Daily Tech & World News Digest (MVP)

간단한 FastAPI 앱으로 해외 주요 뉴스/기술 트렌드를 수집하고 요약 결과를 보여줍니다.

## 빠른 시작 (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

브라우저에서 http://localhost:8000 접속.

## 구조
- `app.py`: FastAPI 엔트리포인트
- `services/rss.py`: 여러 RSS에서 기사 수집
- `services/summarize.py`: 간단 요약(문장 추출 기반)

## Docker 실행

```bash
# 이미지 빌드
docker build -t news-app .

# 컨테이너 실행
docker run -p 8000:8000 news-app

# 또는 docker-compose 사용
docker-compose up --build
```

## 🚀 배포하기

### 1. Render.com (추천 - 무료)

1. [Render.com](https://render.com)에서 계정 생성
2. GitHub 저장소 연결
3. "New Web Service" 선택
4. 저장소 선택 후 다음 설정:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.11.0`

### 2. Railway.app (무료 티어)

1. [Railway.app](https://railway.app)에서 계정 생성
2. GitHub 저장소 연결
3. "Deploy from GitHub repo" 선택
4. 자동으로 `railway.json` 설정 감지

### 3. Docker Hub 배포

```bash
# Docker Hub에 로그인
docker login

# 이미지 태깅
docker tag news-app your-username/news-app:latest

# Docker Hub에 푸시
docker push your-username/news-app:latest
```

## 환경변수
현재 필요 없음. 추후 API 키 기반 확장 시 `.env` 추가 예정.


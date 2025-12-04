# 🐿️ Moa Village - 감정 분석 챗봇

귀여운 다람쥐 "모아"와 함께하는 AI 기반 감정 분석 및 심리 상담 앱입니다.

## ✨ 주요 기능

- 📝 **감정 기록**: 오늘 하루의 감정을 선택하고 기록
- 🗓️ **감정 달력**: 날짜별 감정을 시각적으로 확인
- 💬 **AI 상담**: GPT 기반 감정 분석 및 솔루션 제공
- 📊 **주간 리포트**: 이번 주 감정 변화 그래프

## 🚀 배포 방법 (Streamlit Cloud)

### 1. Streamlit Cloud 접속
https://share.streamlit.io/ 에 접속하고 GitHub 계정으로 로그인

### 2. 새 앱 배포
- "New app" 버튼 클릭
- **Repository**: `peter0524-lab/Moa` 선택
- **Branch**: `main` 선택
- **Main file path**: `app.py` 입력
- **App URL**: 원하는 URL 입력 (예: `moa-village`)

### 3. 환경 변수 설정
- "Advanced settings" 클릭
- "Secrets" 섹션에 다음 추가:
  ```
  OPENAI_API_KEY=sk-proj-...
  ```
  (실제 API 키 값 입력)

### 4. 배포 시작
- "Deploy!" 버튼 클릭
- 배포 완료까지 약 2-3분 소요

## 📦 로컬 실행

```bash
# 1. 저장소 클론
git clone git@github.com:peter0524-lab/Moa.git
cd Moa

# 2. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
# .env 파일 생성 후 OPENAI_API_KEY=sk-... 입력

# 5. 앱 실행
streamlit run app.py
```

## 📁 프로젝트 구조

```
Moa/
├── app.py              # 메인 애플리케이션
├── ingest.py           # 벡터 DB 생성 스크립트
├── requirements.txt    # Python 의존성
├── sample_data.txt     # 샘플 데이터
└── .streamlit/        # Streamlit 설정
    └── config.toml
```

## 🔐 보안 주의사항

- `.env` 파일은 절대 GitHub에 올리지 마세요!
- Streamlit Cloud에서는 "Secrets" 기능을 사용하세요.

## 📝 라이선스

MIT License


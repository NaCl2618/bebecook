# 베베쿡 식단표 변환기 - GitHub Actions 자동화

이 프로젝트는 베베쿡 식단표를 월력 형식으로 변환하는 웹 애플리케이션입니다. GitHub Actions를 통해 매일 자동으로 식단 데이터를 수집합니다.

## 주요 기능

- 🤖 **자동 데이터 수집**: GitHub Actions가 매일 새벽 3시에 자동으로 최신 식단 데이터 수집
- 📅 **월력 변환**: 베베쿡 식단표를 보기 쉬운 달력 형식으로 표시
- 🖨️ **인쇄 지원**: 인쇄 최적화된 레이아웃 제공
- 📱 **반응형 디자인**: 모바일 및 데스크톱 모두 지원

## 로컬 실행

```bash
# Python 간단한 HTTP 서버 실행
python -m http.server 8000

# 브라우저에서 접속
# http://localhost:8000/index.html
```

## GitHub Pages 배포

1. GitHub 저장소 생성 후 코드 푸시
2. Settings > Pages에서 배포 설정
3. Actions 탭에서 "Scrape Bebecook Schedule" 워크플로우 수동 실행

## 파일 구조

- `index.html` - 메인 웹 인터페이스
- `crawler.py` - Python 크롤러 스크립트
- `.github/workflows/scrape.yml` - GitHub Actions 워크플로우
- `data/diet_data.json` - 수집된 식단 데이터

## 기술 스택

- **Frontend**: HTML, CSS, JavaScript
- **Crawler**: Python, Selenium, Webdriver-manager
- **Automation**: GitHub Actions
- **Hosting**: GitHub Pages

# Netflix Dashboard (Supabase) — CLAUDE.md

## 프로젝트 개요

Supabase PostgreSQL에서 Netflix 콘텐츠 데이터(8,859건)를 실시간으로 불러오는 대시보드.
GitHub Pages로 자동 배포. 단일 HTML 파일(`frontend/index.html`).

**파일 구조**
```
netflix-dashboard/
├── frontend/index.html      # 전체 앱 (Supabase 연동 버전)
├── backend/schema.sql       # DB 스키마 (Supabase SQL Editor 실행용)
├── scripts/upload_data.py   # 데이터 업로더 (최초 1회)
├── .env.example             # 환경변수 템플릿
└── .github/workflows/deploy.yml  # GitHub Pages 자동 배포
```

---

## 아키텍처

`frontend/index.html` 단일 파일 안에 HTML/CSS/JS 모두 포함.

| 영역 | 위치 | 설명 |
|------|------|------|
| CSS | `<style>` | 로딩 오버레이 포함 |
| HTML 마크업 | `<body>` | 로딩/에러 오버레이 + 대시보드 |
| Supabase 설정 | JS 상단 | `SUPABASE_URL`, `SUPABASE_KEY` |
| 비동기 fetch | `fetchAllData()` | 1,000건씩 배치 fetch |
| 데이터 계산 | `computeDerivedData()` | GENRE/YEAR/RATINGS/GENRES 계산 |
| 앱 초기화 | `initApp()` | 필터 셋업 + 차트 + 초기 렌더 |
| 부트 | `init()` (IIFE) | async/await 진입점 |

**외부 의존성** (CDN)
- `Chart.js 4.4.1` — 바 차트 렌더링
- Google Fonts — `Bebas Neue`, `DM Sans`

---

## Supabase 설정

```js
const SUPABASE_URL = 'https://rduehiofyxpromgjsxij.supabase.co';
const SUPABASE_KEY = '<anon-key>';  // 공개 읽기 전용
const BATCH_SIZE   = 1000;         // 한 번에 가져오는 레코드 수
```

### REST API 엔드포인트

```
GET /rest/v1/netflix_titles
  ?select=name,year,rating,duration,category
  &limit=1000
  &offset=0
  &order=id
```

헤더:
- `apikey: <SUPABASE_KEY>`
- `Authorization: Bearer <SUPABASE_KEY>`

---

## 데이터 흐름

```
Supabase DB
  ↓  fetchAllData()   — 1,000건 배치, while loop
rawRows[]              — {name, year, rating, duration, category}
  ↓  computeDerivedData()
ALL_DATA[]             — {Name, Year, Rating, Duration, CateAllory}  ← 원본 스키마 복원
GENRE_COUNTS           — 상위 15개 장르 (차트용)
ALL_GENRES             — 전체 장르 배열 (드롭다운용)
YEAR_COUNTS            — 연도별 편수 (차트용)
ALL_RATINGS            — 유효 등급 배열 (드롭다운용)
  ↓  initApp()
필터 DOM 셋업 + 차트 빌드 + 초기 renderTable()
```

---

## 레코드 스키마

Supabase 컬럼 (소문자) → JS 객체 (원본 형식):

| DB 컬럼 | JS 키 | 타입 | 비고 |
|---------|-------|------|------|
| `name` | `Name` | string | 콘텐츠 제목 |
| `year` | `Year` | number | 0 = 결측치 |
| `rating` | `Rating` | string | 없으면 Unknown |
| `duration` | `Duration` | string | 상영 시간 |
| `category` | `CateAllory` | string | 원본 CSV 오타 유지 |

---

## JS 함수 목록

| 함수 | 역할 |
|------|------|
| `fetchAllData()` | Supabase REST API 배치 fetch (async) |
| `computeDerivedData(rawRows)` | GENRE/YEAR/RATINGS/GENRES 계산 |
| `initApp(...)` | 필터 DOM 셋업 + 차트 빌드 + 첫 렌더 |
| `buildGenreChart(...)` | 장르별 가로 바 차트 초기화 |
| `buildYearChart(...)` | 연도별 세로 바 차트 초기화 |
| `applyFilters()` | AND 조건 필터 → KPI·테이블 갱신 |
| `resetFilters()` | 전체 필터 초기화 |
| `clearGenreFilter()` | 장르 필터 태그 해제 |
| `clearYearFilter()` | 연도 필터 태그 해제 |
| `updateKPIs()` | KPI 카드 수치 갱신 |
| `sortTable(key)` | 컬럼 정렬 토글 |
| `renderTable()` | 현재 페이지 테이블 행 렌더링 |
| `renderPagination(total)` | 페이지 버튼 생성 |
| `goPage(p)` | 페이지 이동 + 스크롤 |
| `getRatingClass(r)` | 등급 배지 CSS 클래스 반환 |
| `showLoading/hideLoading()` | 로딩 오버레이 표시/숨기기 |
| `showError(msg)` | 에러 오버레이 표시 |

### 전역 상태

```js
let ALL_DATA = [];         // 전체 레코드 (Supabase에서 로드 후 채워짐)
let filtered = [];         // 현재 필터 결과
let sortKey  = 'Year';     // 정렬 기준
let sortDir  = -1;         // 1: 오름차순, -1: 내림차순
let page     = 1;          // 현재 페이지
const PAGE_SIZE = 50;
let activeGenreFilter = '';
let activeYearFilter  = 0;
```

---

## 데이터베이스 스키마

`backend/schema.sql`:

```sql
CREATE TABLE netflix_titles (
  id       SERIAL PRIMARY KEY,
  name     TEXT    NOT NULL,
  year     INTEGER DEFAULT 0,
  rating   TEXT    DEFAULT 'Unknown',
  duration TEXT,
  category TEXT    DEFAULT 'Unknown'
);
ALTER TABLE netflix_titles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read" ON netflix_titles FOR SELECT TO anon USING (true);
-- 인덱스: year, rating, category, name (gin/tsvector)
```

---

## 업로드 스크립트

`scripts/upload_data.py`:

1. `frontend/index.html`에서 `ALL_DATA` JSON 추출 (정규식)
2. Supabase REST API로 기존 데이터 전체 삭제
3. 500건씩 배치 POST

실행:
```bash
pip install python-dotenv
python3 scripts/upload_data.py
```

필요한 `.env`:
```
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...   # service_role 키 (쓰기 권한)
```

---

## 배포 플로우

```
git push origin main
  → GitHub Actions (deploy.yml)
  → frontend/ 폴더 → Pages artifact 업로드
  → https://jjjuni-0818.github.io/netflix-dashboard/
```

---

## 개발 가이드

### 로컬 테스트

Supabase CORS 설정 기준 `file://` 에서는 fetch가 차단될 수 있음.
로컬 서버 사용 권장:

```bash
cd frontend
python3 -m http.server 8080
# → http://localhost:8080
```

### 새 차트 추가

1. HTML에 `<canvas id="newChart">` 추가
2. `buildNewChart(DATA)` 함수 작성 (Chart.js 패턴 동일)
3. `initApp()` 안에서 호출

### 로딩 오버레이 구조

- `#loading-overlay` — fetch 중 전체 화면 덮개 (`.hidden` 클래스로 숨김)
- `#loading-progress` — 로딩된 레코드 수 표시
- `#error-overlay` — fetch 실패 시 에러 메시지 표시

# Netflix Content Dashboard — Supabase Edition

> Netflix 콘텐츠 데이터(8,859건)를 Supabase에서 실시간으로 불러오는 대시보드

🔗 **Live Demo:** https://jjjuni-0818.github.io/netflix-dashboard/

---

## 프로젝트 구조

```
netflix-dashboard/
├── frontend/
│   └── index.html          # 대시보드 (Supabase 연동, GitHub Pages 배포)
├── backend/
│   └── schema.sql          # Supabase 테이블 + RLS + 인덱스
├── scripts/
│   └── upload_data.py      # 데이터 업로드 스크립트 (최초 1회)
├── .env.example            # 환경변수 템플릿
├── .gitignore
└── README.md
```

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Vanilla HTML/CSS/JS, Chart.js 4.4.1 |
| Database | Supabase (PostgreSQL) |
| 배포 | GitHub Pages + GitHub Actions |

---

## 초기 설정 가이드

### 1. Supabase 테이블 생성

[Supabase SQL Editor](https://supabase.com/dashboard/project/_/sql) 에서 `backend/schema.sql` 전체 실행

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에 실제 키 값 입력
```

### 3. 데이터 업로드

```bash
pip install python-dotenv
python3 scripts/upload_data.py
```

> ⚠️ `upload_data.py` 는 `frontend/index.html` 에서 `ALL_DATA` 를 추출해 업로드합니다.
> 이 스크립트를 실행하기 전에 반드시 원본 단일 파일 대시보드(`../netflix_dashboard.html`)를
> `frontend/index.html` 위치에 복사하거나 경로를 맞춰주세요.

### 4. GitHub Pages 배포

```bash
git push origin main
# GitHub Actions 자동 배포 → frontend/ 폴더가 Pages로 배포됨
```

---

## 데이터 스키마

```sql
CREATE TABLE netflix_titles (
  id        SERIAL PRIMARY KEY,
  name      TEXT    NOT NULL,
  year      INTEGER DEFAULT 0,
  rating    TEXT    DEFAULT 'Unknown',
  duration  TEXT,
  category  TEXT    DEFAULT 'Unknown'
);
```

- `year = 0` → 결측치 (UI에서 `정보 없음` 표시)
- `category` → 원본 CSV의 `CateAllory` 컬럼 (오타 포함)
- RLS: anon 키로 SELECT만 허용 (INSERT/UPDATE/DELETE 차단)

---

## 주요 기능

- **KPI 카드** — 총 콘텐츠 수 / 최다 장르 / 연도 범위 실시간 갱신
- **복합 필터** — 장르 / 등급 / 연도 범위 / 제목 검색 AND 조건
- **차트 클릭** — 장르·연도 차트 막대 클릭 → 테이블 즉시 필터링
- **정렬·페이지네이션** — 컬럼 정렬, 50개씩 페이지

---

*Built with Claude Code · Supabase · GitHub Pages*

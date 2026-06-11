-- Netflix Content Dashboard — Supabase Schema
-- Supabase SQL Editor에서 실행하세요

-- 1. 테이블 생성
CREATE TABLE IF NOT EXISTS netflix_titles (
  id        SERIAL PRIMARY KEY,
  name      TEXT    NOT NULL,
  year      INTEGER DEFAULT 0,
  rating    TEXT    DEFAULT 'Unknown',
  duration  TEXT,
  category  TEXT    DEFAULT 'Unknown'
);

-- 2. Row Level Security 활성화
ALTER TABLE netflix_titles ENABLE ROW LEVEL SECURITY;

-- 3. 공개 읽기 허용 (프론트엔드에서 anon key로 조회 가능)
CREATE POLICY "public_read" ON netflix_titles
  FOR SELECT TO anon USING (true);

-- 4. 인덱스 (필터/정렬 성능 향상)
CREATE INDEX IF NOT EXISTS idx_netflix_year     ON netflix_titles(year);
CREATE INDEX IF NOT EXISTS idx_netflix_rating   ON netflix_titles(rating);
CREATE INDEX IF NOT EXISTS idx_netflix_category ON netflix_titles(category);
CREATE INDEX IF NOT EXISTS idx_netflix_name     ON netflix_titles USING gin(to_tsvector('simple', name));

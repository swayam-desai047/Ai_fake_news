-- ============================================================
-- AI News Aggregator — Complete Unified Database Schema (v2)
-- Fresh install: paste and run this once in the Supabase SQL Editor. It is idempotent, so it can
-- also be re-run on an existing database (it then behaves like migrations 01 + 02).
-- https://supabase.com/dashboard/project/_/sql
-- ============================================================

-- 0. Enable pgcrypto for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ────────────────────────────────────────────────────────────
-- 1. ARTICLES TABLE
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title               text NOT NULL UNIQUE,
  source_domain       text,
  source_url          text,
  content_summary     text,
  category            text DEFAULT 'general',
  sentiment           text,
  is_fake             boolean,
  credibility_score   real,
  ai_reasoning        text,
  published_at        timestamp with time zone DEFAULT now(),
  created_at          timestamp with time zone DEFAULT now(),

  -- M.Sc Synopsis & 8-Dimension Analysis Fields
  risk_score          real,                 -- 0..1 heuristic risk (not a calibrated probability)
  confidence_level    real,                 -- classifier's top-class softmax score (uncalibrated)
  credibility_label   text,                 -- Low/Moderate/High Risk; NULL = not computed
  needs_verification  boolean DEFAULT false,
  ai_summary          text,
  dimensions          jsonb DEFAULT '{}'::jsonb,
  group_id            text DEFAULT NULL,
  event_title         text DEFAULT NULL,

  -- v2 analysis provenance
  analysis_status        text,              -- complete | partial | unavailable | pending | legacy
  analysis_method        text,              -- model+rules | rules
  model_version          text,
  analyzed_at            timestamptz,
  summary_method         text,              -- extractive
  model_fake_probability real               -- raw classifier fake-class score
);

-- Ensure upgrade columns exist if the table was previously created
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS risk_score REAL,
  ADD COLUMN IF NOT EXISTS confidence_level REAL,
  ADD COLUMN IF NOT EXISTS credibility_label TEXT,
  ADD COLUMN IF NOT EXISTS needs_verification BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS ai_summary TEXT,
  ADD COLUMN IF NOT EXISTS dimensions JSONB DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS group_id TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS event_title TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS analysis_status TEXT,
  ADD COLUMN IF NOT EXISTS analysis_method TEXT,
  ADD COLUMN IF NOT EXISTS model_version TEXT,
  ADD COLUMN IF NOT EXISTS analyzed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS summary_method TEXT,
  ADD COLUMN IF NOT EXISTS model_fake_probability REAL;
ALTER TABLE articles ALTER COLUMN credibility_label DROP DEFAULT;

-- ────────────────────────────────────────────────────────────
-- 2. NAMED VISITORS TABLE (Display name / visitor login)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS named_visitors (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name       text UNIQUE NOT NULL,
  created_at timestamp with time zone DEFAULT now()
);

-- ────────────────────────────────────────────────────────────
-- 3. USER PROFILES TABLE (Authenticated user accounts)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
  id           uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  name         text,
  saved_topics text[],
  created_at   timestamp with time zone DEFAULT now()
);

-- ────────────────────────────────────────────────────────────
-- 4. ROW LEVEL SECURITY (RLS)
-- ────────────────────────────────────────────────────────────
ALTER TABLE articles       ENABLE ROW LEVEL SECURITY;
ALTER TABLE named_visitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles  ENABLE ROW LEVEL SECURITY;

-- Articles: public READ only. The FastAPI backend writes with the service-role key (bypasses RLS);
-- the anon/publishable key used by the frontend cannot insert, update or delete articles.
DROP POLICY IF EXISTS "Articles: public read" ON articles;
CREATE POLICY "Articles: public read" ON articles FOR SELECT USING (true);
DROP POLICY IF EXISTS "Articles: public insert" ON articles;
DROP POLICY IF EXISTS "Articles: public update" ON articles;

-- Named Visitors: public read, insert (name-only reader registration). No update/delete policy.
DROP POLICY IF EXISTS "Allow public read" ON named_visitors;
CREATE POLICY "Allow public read" ON named_visitors FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public insert" ON named_visitors;
CREATE POLICY "Allow public insert" ON named_visitors FOR INSERT WITH CHECK (true);

-- User Profiles: Scoped to logged-in authenticated user
DROP POLICY IF EXISTS "Profiles: user can insert own row" ON user_profiles;
CREATE POLICY "Profiles: user can insert own row" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Profiles: user can view own row" ON user_profiles;
CREATE POLICY "Profiles: user can view own row" ON user_profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Profiles: user can update own row" ON user_profiles;
CREATE POLICY "Profiles: user can update own row" ON user_profiles FOR UPDATE USING (auth.uid() = id);

-- ────────────────────────────────────────────────────────────
-- 5. PERFORMANCE INDEXES
-- ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_articles_published_at      ON articles (published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_category          ON articles (category);
CREATE INDEX IF NOT EXISTS idx_articles_credibility       ON articles (credibility_score DESC);
CREATE INDEX IF NOT EXISTS idx_articles_group_id          ON articles (group_id);
CREATE INDEX IF NOT EXISTS idx_articles_credibility_label ON articles (credibility_label);
CREATE INDEX IF NOT EXISTS idx_articles_needs_verification ON articles (needs_verification);
CREATE INDEX IF NOT EXISTS idx_articles_source_url        ON articles (source_url);
CREATE INDEX IF NOT EXISTS idx_articles_analysis_status   ON articles (analysis_status);

-- ────────────────────────────────────────────────────────────
-- 6. VALUE CONSTRAINTS (NOT VALID = existing rows are not re-checked)
-- ────────────────────────────────────────────────────────────
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'articles_credibility_label_check') THEN
    ALTER TABLE articles ADD CONSTRAINT articles_credibility_label_check
      CHECK (credibility_label IS NULL OR credibility_label IN ('Low Risk', 'Moderate Risk', 'High Risk')) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'articles_risk_score_range') THEN
    ALTER TABLE articles ADD CONSTRAINT articles_risk_score_range
      CHECK (risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 1)) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'articles_analysis_status_check') THEN
    ALTER TABLE articles ADD CONSTRAINT articles_analysis_status_check
      CHECK (analysis_status IS NULL OR analysis_status IN ('complete', 'partial', 'unavailable', 'pending', 'legacy')) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'named_visitors_name_length') THEN
    ALTER TABLE named_visitors ADD CONSTRAINT named_visitors_name_length
      CHECK (char_length(btrim(name)) BETWEEN 1 AND 40) NOT VALID;
  END IF;
END $$;

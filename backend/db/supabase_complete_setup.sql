-- ============================================================
-- AI News Aggregator — Complete Unified Database Schema
-- Paste and run this once in Supabase SQL Editor:
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
  risk_score          real,
  confidence_level    real,
  credibility_label   text DEFAULT 'Low Risk',
  needs_verification  boolean DEFAULT false,
  ai_summary          text,
  dimensions          jsonb DEFAULT '{}'::jsonb,
  group_id            text DEFAULT NULL,
  event_title         text DEFAULT NULL
);

-- Ensure upgrade columns exist if the table was previously created
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS risk_score REAL,
  ADD COLUMN IF NOT EXISTS confidence_level REAL,
  ADD COLUMN IF NOT EXISTS credibility_label TEXT DEFAULT 'Low Risk',
  ADD COLUMN IF NOT EXISTS needs_verification BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS ai_summary TEXT,
  ADD COLUMN IF NOT EXISTS dimensions JSONB DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS group_id TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS event_title TEXT DEFAULT NULL;

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

-- Articles: public read, insert, update
DROP POLICY IF EXISTS "Articles: public read" ON articles;
CREATE POLICY "Articles: public read" ON articles FOR SELECT USING (true);

DROP POLICY IF EXISTS "Articles: public insert" ON articles;
CREATE POLICY "Articles: public insert" ON articles FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Articles: public update" ON articles;
CREATE POLICY "Articles: public update" ON articles FOR UPDATE USING (true);

-- Named Visitors: public read, insert
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

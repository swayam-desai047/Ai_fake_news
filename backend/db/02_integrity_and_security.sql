-- ============================================================
-- Migration 02: analysis integrity + security hardening
-- Safe to run more than once. Does not drop tables, columns or article data.
-- Run AFTER schema.sql and 01_upgrade_to_msc_synopsis.sql
-- (supabase_complete_setup.sql already includes everything below).
-- ============================================================

-- 1. No more "Low Risk" by default --------------------------------------------------------
-- An article that has not been analysed must not look like a low-risk article.
ALTER TABLE articles ALTER COLUMN credibility_label DROP DEFAULT;

-- 2. Analysis provenance columns ----------------------------------------------------------
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS analysis_status        TEXT,         -- complete | partial | unavailable | legacy
  ADD COLUMN IF NOT EXISTS analysis_method        TEXT,         -- model+rules | rules
  ADD COLUMN IF NOT EXISTS model_version          TEXT,         -- pipeline version + model ids used
  ADD COLUMN IF NOT EXISTS analyzed_at            TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS summary_method         TEXT,         -- extractive (NULL when no summary)
  ADD COLUMN IF NOT EXISTS model_fake_probability REAL;         -- raw classifier fake-class score (uncalibrated)

-- 3. Correct rows written by the old pipeline ---------------------------------------------
-- Old rows received credibility_label = 'Low Risk' from a default, without any risk score behind it.
-- The label is cleared (it was never computed) and the rows are marked as legacy so the UI shows
-- "Unavailable" until scripts/reanalyze.py re-scores them. Titles, excerpts and URLs are untouched.
UPDATE articles
   SET credibility_label = NULL
 WHERE risk_score IS NULL
   AND credibility_label IS NOT NULL;

UPDATE articles
   SET analysis_status = 'legacy'
 WHERE analysis_status IS NULL;

-- 4. Value constraints (NOT VALID: enforced for new writes, existing rows are not re-checked) ---
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

-- 5. Indexes ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_articles_source_url      ON articles (source_url);
CREATE INDEX IF NOT EXISTS idx_articles_analysis_status ON articles (analysis_status);

-- 6. Row Level Security -------------------------------------------------------------------
-- Articles are written only by the FastAPI backend with the service-role key (which bypasses RLS).
-- The public anon/publishable key used by the Next.js frontend may only read them.
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Articles: public insert" ON articles;
DROP POLICY IF EXISTS "Articles: public update" ON articles;
DROP POLICY IF EXISTS "Articles: public read"   ON articles;
CREATE POLICY "Articles: public read" ON articles FOR SELECT USING (true);

-- Named visitors: the name-only reader registration needs read + insert from the frontend.
-- No public UPDATE or DELETE policy exists, so names cannot be changed or removed anonymously.
ALTER TABLE named_visitors ENABLE ROW LEVEL SECURITY;

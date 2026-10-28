-- Migration: 01_upgrade_to_msc_synopsis.sql
-- Description: Non-destructive schema upgrade for M.Sc Synopsis alignment

-- 1. Add Credibility Risk & Calibration Fields
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS risk_score REAL,
  ADD COLUMN IF NOT EXISTS confidence_level REAL,
  ADD COLUMN IF NOT EXISTS credibility_label TEXT DEFAULT 'Low Risk',
  ADD COLUMN IF NOT EXISTS needs_verification BOOLEAN DEFAULT FALSE;

-- 2. Add AI Summarization Field
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS ai_summary TEXT;

-- 3. Add 8-Dimension Analysis Structured JSONB Column
-- Structure:
-- {
--   "sentiment": 72,
--   "bias": 80,
--   "objectivity": 85,
--   "readability": 76,
--   "propaganda": 88,
--   "headline_accuracy": 79,
--   "source_credibility": 83,
--   "content_quality": 81,
--   "explanations": {
--     "sentiment": "Tone is predominantly neutral and informative.",
--     "bias": "Uses balanced attribution without partisan loading.",
--     "objectivity": "High concentration of factual statements.",
--     "readability": "Standard college-level reading ease.",
--     "propaganda": "No emotional manipulation patterns detected.",
--     "headline_accuracy": "Headline matches article key facts.",
--     "source_credibility": "Reputable international news agency.",
--     "content_quality": "Well-structured article with clear context."
--   }
-- }
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS dimensions JSONB DEFAULT '{}'::jsonb;

-- 4. Add Cross-Source Event Clustering Fields
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS group_id TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS event_title TEXT DEFAULT NULL;

-- 5. Add Performance Indexes
CREATE INDEX IF NOT EXISTS idx_articles_group_id ON articles(group_id);
CREATE INDEX IF NOT EXISTS idx_articles_credibility_label ON articles(credibility_label);
CREATE INDEX IF NOT EXISTS idx_articles_needs_verification ON articles(needs_verification);

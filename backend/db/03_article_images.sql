-- ============================================================
-- Migration 03: story photos
-- Safe to run more than once. Does not drop tables, columns or article data.
-- Run AFTER 02_integrity_and_security.sql
-- (supabase_complete_setup.sql already includes everything below).
-- ============================================================

-- The feed-supplied image (media:content / media:thumbnail / enclosure) for each article.
ALTER TABLE articles ADD COLUMN IF NOT EXISTS image_url TEXT;

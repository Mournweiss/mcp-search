-- Firecrawl NUQ Database Schema
-- Initializes nuq schema with all required tables, indexes, and cron jobs
-- for the Firecrawl queue system to function correctly.

-- Load required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Create schema and custom data types
CREATE SCHEMA IF NOT EXISTS nuq;

DO $$ BEGIN
    CREATE TYPE nuq.job_status AS ENUM ('queued', 'active', 'completed', 'failed');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE nuq.group_status AS ENUM ('active', 'completed', 'cancelled');
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- Table: queue_scrape
CREATE TABLE IF NOT EXISTS nuq.queue_scrape (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  status nuq.job_status NOT NULL DEFAULT 'queued',
  data jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  priority int NOT NULL DEFAULT 0,
  lock uuid,
  locked_at timestamptz,
  stalls integer,
  finished_at timestamptz,
  listen_channel_id text,
  returnvalue jsonb,
  failedreason text,
  owner_id uuid,
  group_id uuid,
  CONSTRAINT queue_scrape_pkey PRIMARY KEY (id)
);

-- Optimize autovacuum parameters for high-throughput queue operations
ALTER TABLE nuq.queue_scrape SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_analyze_scale_factor = 0.01,
  autovacuum_vacuum_cost_limit = 10000,
  autovacuum_vacuum_cost_delay = 0
);

-- Indexes for queue_scrape
CREATE INDEX IF NOT EXISTS queue_scrape_active_locked_at_idx ON nuq.queue_scrape USING btree (locked_at) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_queued_optimal_2_idx ON nuq.queue_scrape (priority ASC, created_at ASC, id) WHERE status = 'queued';
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_failed_created_at_idx ON nuq.queue_scrape (created_at) WHERE status = 'failed';
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_completed_created_at_idx ON nuq.queue_scrape (created_at) WHERE status = 'completed';
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_group_owner_mode_idx ON nuq.queue_scrape (group_id, owner_id) WHERE (data->>'mode') = 'single_urls';
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_group_mode_status_idx ON nuq.queue_scrape (group_id, status) WHERE (data->>'mode') = 'single_urls';
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_group_completed_listing_idx ON nuq.queue_scrape (group_id, finished_at ASC, created_at ASC) WHERE status = 'completed' AND (data->>'mode') = 'single_urls';
CREATE INDEX IF NOT EXISTS idx_queue_scrape_group_status ON nuq.queue_scrape (group_id, status) WHERE status IN ('active', 'queued');

-- Table: queue_scrape_backlog
CREATE TABLE IF NOT EXISTS nuq.queue_scrape_backlog (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  data jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  priority int NOT NULL DEFAULT 0,
  listen_channel_id text,
  owner_id uuid,
  group_id uuid,
  times_out_at timestamptz,
  CONSTRAINT queue_scrape_backlog_pkey PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_backlog_owner_id_idx ON nuq.queue_scrape_backlog (owner_id);
CREATE INDEX IF NOT EXISTS nuq_queue_scrape_backlog_group_mode_idx ON nuq.queue_scrape_backlog (group_id) WHERE (data->>'mode') = 'single_urls';

-- Table: queue_crawl_finished
CREATE TABLE IF NOT EXISTS nuq.queue_crawl_finished (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  status nuq.job_status NOT NULL DEFAULT 'queued',
  data jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  priority int NOT NULL DEFAULT 0,
  lock uuid,
  locked_at timestamptz,
  stalls integer,
  finished_at timestamptz,
  listen_channel_id text,
  returnvalue jsonb,
  failedreason text,
  owner_id uuid,
  group_id uuid,
  CONSTRAINT queue_crawl_finished_pkey PRIMARY KEY (id)
);

ALTER TABLE nuq.queue_crawl_finished SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_analyze_scale_factor = 0.01,
  autovacuum_vacuum_cost_limit = 10000,
  autovacuum_vacuum_cost_delay = 0
);

-- Indexes for queue_crawl_finished
CREATE INDEX IF NOT EXISTS queue_crawl_finished_active_locked_at_idx ON nuq.queue_crawl_finished USING btree (locked_at) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS nuq_queue_crawl_finished_queued_optimal_2_idx ON nuq.queue_crawl_finished (priority ASC, created_at ASC, id) WHERE status = 'queued';
CREATE INDEX IF NOT EXISTS nuq_queue_crawl_finished_failed_created_at_idx ON nuq.queue_crawl_finished (created_at) WHERE status = 'failed';
CREATE INDEX IF NOT EXISTS nuq_queue_crawl_finished_completed_created_at_idx ON nuq.queue_crawl_finished (created_at) WHERE status = 'completed';

-- Table: group_crawl
CREATE TABLE IF NOT EXISTS nuq.group_crawl (
  id uuid NOT NULL,
  status nuq.group_status NOT NULL DEFAULT 'active',
  created_at timestamptz NOT NULL DEFAULT now(),
  owner_id uuid NOT NULL,
  ttl int8 NOT NULL DEFAULT 86400000,
  expires_at timestamptz,
  CONSTRAINT group_crawl_pkey PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS idx_group_crawl_status ON nuq.group_crawl (status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_queue_scrape_backlog_group_id ON nuq.queue_scrape_backlog (group_id);

-- Schedule maintenance and cleanup jobs idempotently
DO $$
DECLARE
  job_name text;
BEGIN
  FOR job_name IN VALUES
    ('nuq_queue_scrape_clean_completed'), ('nuq_queue_scrape_clean_failed'),
    ('nuq_queue_scrape_lock_reaper'), ('nuq_queue_scrape_backlog_reaper'), ('nuq_queue_scrape_reindex'),
    ('nuq_queue_crawl_finished_clean_completed'), ('nuq_queue_crawl_finished_clean_failed'),
    ('nuq_queue_crawl_finished_lock_reaper'), ('nuq_queue_crawl_finished_reindex'),
    ('nuq_group_crawl_finished'), ('nuq_group_crawl_clean')
  LOOP
    BEGIN
      PERFORM cron.unschedule(job_name);
    EXCEPTION WHEN OTHERS THEN
      NULL;
    END;
  END LOOP;

  -- Scraping queue maintenance
  PERFORM cron.schedule('nuq_queue_scrape_clean_completed', '*/5 * * * *',
    $cmd$ DELETE FROM nuq.queue_scrape WHERE status = 'completed' AND created_at < now() - interval '1 hour' AND group_id IS NULL; $cmd$);
  PERFORM cron.schedule('nuq_queue_scrape_clean_failed', '*/5 * * * *',
    $cmd$ DELETE FROM nuq.queue_scrape WHERE status = 'failed' AND created_at < now() - interval '6 hours' AND group_id IS NULL; $cmd$);
  PERFORM cron.schedule('nuq_queue_scrape_lock_reaper', '15 seconds',
    $cmd$ UPDATE nuq.queue_scrape SET status = 'queued', lock = null, locked_at = null, stalls = COALESCE(stalls, 0) + 1 WHERE locked_at <= now() - interval '1 minute' AND status = 'active' AND COALESCE(stalls, 0) < 9; WITH stallfail AS (UPDATE nuq.queue_scrape SET status = 'failed', lock = null, locked_at = null, stalls = COALESCE(stalls, 0) + 1 WHERE locked_at <= now() - interval '1 minute' AND status = 'active' AND COALESCE(stalls, 0) >= 9 RETURNING id) SELECT pg_notify('nuq.queue_scrape', id::text || '|failed') FROM stallfail; $cmd$);
  PERFORM cron.schedule('nuq_queue_scrape_backlog_reaper', '* * * * *',
    $cmd$ DELETE FROM nuq.queue_scrape_backlog WHERE times_out_at < now(); $cmd$);
  PERFORM cron.schedule('nuq_queue_scrape_reindex', '0 9 * * *',
    $cmd$ REINDEX TABLE CONCURRENTLY nuq.queue_scrape; $cmd$);

  -- Crawl completion queue maintenance
  PERFORM cron.schedule('nuq_queue_crawl_finished_clean_completed', '*/5 * * * *',
    $cmd$ DELETE FROM nuq.queue_crawl_finished WHERE status = 'completed' AND created_at < now() - interval '1 hour' AND group_id IS NULL; $cmd$);
  PERFORM cron.schedule('nuq_queue_crawl_finished_clean_failed', '*/5 * * * *',
    $cmd$ DELETE FROM nuq.queue_crawl_finished WHERE status = 'failed' AND created_at < now() - interval '6 hours' AND group_id IS NULL; $cmd$);
  PERFORM cron.schedule('nuq_queue_crawl_finished_lock_reaper', '15 seconds',
    $cmd$ UPDATE nuq.queue_crawl_finished SET status = 'queued', lock = null, locked_at = null, stalls = COALESCE(stalls, 0) + 1 WHERE locked_at <= now() - interval '1 minute' AND status = 'active' AND COALESCE(stalls, 0) < 9; WITH stallfail AS (UPDATE nuq.queue_crawl_finished SET status = 'failed', lock = null, locked_at = null, stalls = COALESCE(stalls, 0) + 1 WHERE locked_at <= now() - interval '1 minute' AND status = 'active' AND COALESCE(stalls, 0) >= 9 RETURNING id) SELECT pg_notify('nuq.queue_crawl_finished', id::text || '|failed') FROM stallfail; $cmd$);
  PERFORM cron.schedule('nuq_queue_crawl_finished_reindex', '0 9 * * *',
    $cmd$ REINDEX TABLE CONCURRENTLY nuq.queue_crawl_finished; $cmd$);

  -- Group lifecycle management
  PERFORM cron.schedule('nuq_group_crawl_finished', '15 seconds',
    $cmd$ WITH finished_groups AS ( UPDATE nuq.group_crawl SET status = 'completed', expires_at = now() + MAKE_INTERVAL(secs => ttl / 1000) WHERE status = 'active' AND NOT EXISTS (SELECT 1 FROM nuq.queue_scrape WHERE status IN ('active', 'queued') AND group_id = nuq.group_crawl.id) AND NOT EXISTS (SELECT 1 FROM nuq.queue_scrape_backlog WHERE group_id = nuq.group_crawl.id) RETURNING id, owner_id ) INSERT INTO nuq.queue_crawl_finished (data, owner_id, group_id) SELECT '{}'::jsonb, owner_id, id FROM finished_groups; $cmd$);
  PERFORM cron.schedule('nuq_group_crawl_clean', '*/5 * * * *',
    $cmd$ WITH cleaned_groups AS ( DELETE FROM nuq.group_crawl WHERE status = 'completed' AND expires_at < now() RETURNING * ), _q1 AS (DELETE FROM nuq.queue_scrape WHERE group_id IN (SELECT id FROM cleaned_groups)), _q2 AS (DELETE FROM nuq.queue_scrape_backlog WHERE group_id IN (SELECT id FROM cleaned_groups)), _q3 AS (DELETE FROM nuq.queue_crawl_finished WHERE group_id IN (SELECT id FROM cleaned_groups)) SELECT 1; $cmd$);

  RAISE NOTICE 'NUQ cron jobs scheduled successfully';
END $$;

-- Final status message
DO $$
BEGIN
  RAISE NOTICE 'NUQ schema initialization completed for database: firecrawl';
END $$;
-- stashgres database initialization
--
-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
--
-- Table: stashes
CREATE TABLE
    stashes (
        id UUID DEFAULT uuid_generate_v4 () NOT NULL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT timezone ('utc', now()) NOT NULL,
        updated_at TIMESTAMPTZ DEFAULT timezone ('utc', now()) NOT NULL
    );
COMMENT ON TABLE stashes IS 'Data on each stash.';
COMMENT ON COLUMN stashes.id IS 'Unique identifier for each stash.';
COMMENT ON COLUMN stashes.name IS 'Unique name for referencing the stash.';
--
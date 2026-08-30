-- Experiment 03 — Same Database
-- PostgreSQL 18.6
--
-- Purpose:
--   Create one PostgreSQL database with separate logical schemas
--   for the Authorization Server and Resource Server.
--
-- Experiment topology:
--   Authorization Server ──┐
--                          ├── PostgreSQL
--   Resource Server ───────┘

CREATE SCHEMA IF NOT EXISTS authz;
CREATE SCHEMA IF NOT EXISTS resource;

CREATE TABLE IF NOT EXISTS authz.authorizations (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_id text NOT NULL,
    permission text NOT NULL
);

CREATE TABLE IF NOT EXISTS resource.profiles (
    id text PRIMARY KEY,
    display_name text NOT NULL
);

INSERT INTO authz.authorizations (
    subject_id,
    permission
)
VALUES (
    'demo-user',
    'read:profile'
)
ON CONFLICT DO NOTHING;

INSERT INTO resource.profiles (
    id,
    display_name
)
VALUES (
    'demo-user',
    'Lab User'
)
ON CONFLICT DO NOTHING;
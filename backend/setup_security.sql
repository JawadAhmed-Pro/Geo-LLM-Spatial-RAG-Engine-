-- Hardening Script for Geo-LLM Engine
-- Protects the database by creating a low-privilege 'reader' account

-- 1. Create the reader user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'geollm_reader') THEN
        CREATE USER geollm_reader WITH PASSWORD 'geollm_reader_secret';
    END IF;
END
$$;

-- 2. Grant connection and usage
GRANT CONNECT ON DATABASE geollm TO geollm_reader;
GRANT USAGE ON SCHEMA public TO geollm_reader;

-- 3. Grant SELECT only on the core data table
GRANT SELECT ON infrastructure TO geollm_reader;

-- 4. Grant access to PostGIS spatial reference table (required for some functions)
GRANT SELECT ON spatial_ref_sys TO geollm_reader;

-- 5. Future-proof: Ensure new tables also grant SELECT to reader
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO geollm_reader;

-- 6. Verify (Optional logging)
SELECT 'Security setup complete. Reader user created and restricted.' as status;

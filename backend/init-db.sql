-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create n8n database
CREATE DATABASE n8n_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE art_buddy_db TO art_buddy;
GRANT ALL PRIVILEGES ON DATABASE n8n_db TO art_buddy;
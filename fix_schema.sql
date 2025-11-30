-- Fix schema for LangChain SupabaseVectorStore compatibility
-- Run this if you already created the table with BIGSERIAL

-- Drop the old table if it exists (WARNING: This will delete all data!)
-- DROP TABLE IF EXISTS repository_embeddings CASCADE;

-- Recreate with correct schema
CREATE TABLE IF NOT EXISTS repository_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recreate indexes
CREATE INDEX IF NOT EXISTS repository_embeddings_embedding_idx 
ON repository_embeddings 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS repository_embeddings_metadata_idx 
ON repository_embeddings 
USING GIN (metadata);

CREATE INDEX IF NOT EXISTS repository_embeddings_content_idx 
ON repository_embeddings 
USING GIN (to_tsvector('english', content));


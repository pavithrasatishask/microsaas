-- Supabase Database Schema for Repository Intelligence Backend
-- Run this SQL in your Supabase SQL Editor

-- Step 1: Enable the pgvector extension (required for vector embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create the repository_embeddings table
-- This table stores the embedded code/documentation chunks from repositories
-- Note: LangChain's SupabaseVectorStore expects UUID for id column
CREATE TABLE IF NOT EXISTS repository_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),  -- OpenAI text-embedding-ada-002 uses 1536 dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create index for vector similarity search (HNSW index for fast searches)
CREATE INDEX IF NOT EXISTS repository_embeddings_embedding_idx 
ON repository_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- Step 4: Create index for metadata queries (if you want to filter by metadata)
CREATE INDEX IF NOT EXISTS repository_embeddings_metadata_idx 
ON repository_embeddings 
USING GIN (metadata);

-- Step 5: Create index for content search (optional, for text search)
CREATE INDEX IF NOT EXISTS repository_embeddings_content_idx 
ON repository_embeddings 
USING GIN (to_tsvector('english', content));

-- Step 6: Create match_documents function (required by LangChain SupabaseVectorStore)
-- This function performs similarity search using cosine distance
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_count int DEFAULT 5,
  filter jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  embedding vector(1536),
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    re.id,
    re.content,
    re.metadata,
    re.embedding,
    1 - (re.embedding <=> query_embedding) AS similarity
  FROM repository_embeddings re
  WHERE 1=1
    AND (filter = '{}'::jsonb OR re.metadata @> filter)
  ORDER BY re.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Step 7: Add helpful comments
COMMENT ON TABLE repository_embeddings IS 'Stores embedded code/documentation chunks for semantic search';
COMMENT ON COLUMN repository_embeddings.content IS 'The actual text content of the code/documentation chunk';
COMMENT ON COLUMN repository_embeddings.metadata IS 'JSON metadata including file_path, file_name, file_type, etc.';
COMMENT ON COLUMN repository_embeddings.embedding IS 'Vector embedding of the content (1536 dimensions for OpenAI ada-002)';

-- Verification query (run this to verify the setup)
-- SELECT 
--     tablename, 
--     indexname, 
--     indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'repository_embeddings';


-- Update existing schema with match_documents function
-- Run this if you already have the repository_embeddings table

-- Create match_documents function (required by LangChain SupabaseVectorStore)
-- Fixed: Using table alias to avoid ambiguous column reference
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


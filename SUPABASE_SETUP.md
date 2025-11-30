# Supabase Database Setup Guide

## Quick Setup Steps

1. **Go to your Supabase project**: https://supabase.com/dashboard
2. **Open SQL Editor**: Click on "SQL Editor" in the left sidebar
3. **Run the schema**: Copy and paste the contents of `schema.sql` and click "Run"
4. **Verify setup**: Check that the table was created successfully

## Detailed Steps

### Step 1: Enable pgvector Extension

The `pgvector` extension is required for storing and searching vector embeddings. Run this in your SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 2: Create the Table

The `repository_embeddings` table stores all the embedded code/documentation chunks. The schema includes:

- `id`: Primary key (auto-incrementing)
- `content`: The actual text content
- `metadata`: JSONB field for storing file paths, types, etc.
- `embedding`: Vector embedding (1536 dimensions for OpenAI)
- `created_at`: Timestamp for tracking

### Step 3: Verify Installation

After running the schema, verify everything is set up correctly:

```sql
-- Check if extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check if table exists
SELECT * FROM information_schema.tables 
WHERE table_name = 'repository_embeddings';

-- Check indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'repository_embeddings';
```

## Table Structure

The table structure matches what LangChain's `SupabaseVectorStore` expects:

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `content` | TEXT | Code/documentation text |
| `metadata` | JSONB | File path, name, type, etc. |
| `embedding` | vector(1536) | OpenAI embedding vector |
| `created_at` | TIMESTAMP | Creation timestamp |

## Indexes

Three indexes are created for optimal performance:

1. **HNSW Index on embedding**: Fast vector similarity search
2. **GIN Index on metadata**: Fast JSONB queries
3. **GIN Index on content**: Full-text search (optional)

## Troubleshooting

### Error: "extension 'vector' does not exist"
- Make sure you're running the SQL in the Supabase SQL Editor
- The extension should be enabled automatically, but you can manually enable it

### Error: "relation 'repository_embeddings' already exists"
- The table already exists, which is fine
- You can drop it first if you want to recreate: `DROP TABLE repository_embeddings CASCADE;`

### Performance Issues
- The HNSW index should handle most queries efficiently
- For very large datasets, you may need to tune the index parameters

## Next Steps

After setting up the database:

1. Update your `.env` file with Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_VECTOR_TABLE=repository_embeddings
   ```

2. Test the connection by running:
   ```bash
   python -c "from embeddings.vector_store import get_vector_store; vs = get_vector_store(); print('✓ Connected to Supabase')"
   ```

3. Start indexing your repository!


# Repository Intelligence Backend

A MicroSaaS backend system for analyzing code repositories, answering architecture questions, validating change requests, and performing impact assessments using LangChain and vector embeddings.

## Features

- **Repository Q&A**: Answer architecture and framework questions using vector search
- **Change Validation**: Validate feature requests against existing codebase
- **Impact Analysis**: Detect conflicts and assess impact on existing modules
- **Decision Engine**: Automated decision making (SAFE TO IMPLEMENT / CHANGE REQUEST WARNING)

## Architecture

```
/src
  /api          - Flask routes and endpoints
  /services     - Business logic services
  /chains       - LangChain chains (QA, Validation, Impact, Decision)
  /embeddings   - Vector store management (Chroma/Supabase)
  /loaders      - Document loading and chunking
  /models       - Pydantic schemas
  /utils        - Configuration and logging
  main.py       - Flask application entry point
```

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Index a repository** (via API or script):
```python
from services.repository_service import RepositoryService

service = RepositoryService()
service.index_repository("/path/to/repository")
```

4. **Run the server**:
```bash
python src/main.py
# Or using Flask CLI:
flask --app src.main run --host=0.0.0.0 --port=8000
```

## API Endpoints

### Health Check
```
GET /health
```

### Ask Question
```
POST /api/v1/question
Body: {
  "question": "How does authentication work?",
  "max_results": 5
}
```

### Validate Change
```
POST /api/v1/validate
Body: {
  "description": "Add new payment method",
  "feature_type": "new_feature",
  "target_modules": ["payment", "billing"]
}
```

### Analyze Impact
```
POST /api/v1/impact
Body: {
  "description": "Modify user authentication flow",
  "feature_type": "modification"
}
```

### Full Analysis
```
POST /api/v1/analyze
Body: {
  "description": "Add new feature",
  "feature_type": "new_feature"
}
```

Returns structured response with:
- Summary
- Repository Evidence
- Analysis
- Impact Assessment
- Decision (SAFE TO IMPLEMENT / CHANGE REQUEST WARNING)
- Recommended Next Steps

## Configuration

- **Vector DB**: Supabase Vector (required)
- **Embeddings**: OpenAI embeddings (configurable)
- **LLM**: GPT-4 for reasoning chains (configurable)

## Development

The system uses:
- Flask for REST API
- LangChain for chain orchestration
- Supabase for vector storage
- OpenAI for embeddings and LLM

## Supabase Setup

1. **Create a Supabase project** at https://supabase.com
2. **Run the database schema**:
   - Open SQL Editor in your Supabase dashboard
   - Copy and paste the contents of `schema.sql`
   - Click "Run" to execute
   - This will create the `repository_embeddings` table with proper indexes
3. **Verify the setup** (optional):
   ```bash
   python verify_supabase.py
   ```
4. **Add your Supabase credentials to `.env`**:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_VECTOR_TABLE=repository_embeddings
   ```

For detailed setup instructions, see `SUPABASE_SETUP.md`.

## License

MIT


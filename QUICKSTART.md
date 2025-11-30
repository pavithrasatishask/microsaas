# Quick Start Guide

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your credentials:
# OPENAI_API_KEY=sk-your-key-here
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-supabase-anon-key
```

**Supabase Setup:**
1. Create a Supabase project at https://supabase.com
2. Enable the `pgvector` extension in your database (SQL Editor):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Create the embeddings table:
   ```sql
   CREATE TABLE repository_embeddings (
     id BIGSERIAL PRIMARY KEY,
     content TEXT,
     metadata JSONB,
     embedding vector(1536)
   );
   ```
4. Get your Supabase URL and anon key from Project Settings > API

3. **Index a repository**:
```bash
# Option 1: Using the script
python scripts/index_repository.py /path/to/your/repository

# Option 2: Using the API
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/your/repository"}'
```

4. **Start the server**:
```bash
python src/main.py
# Or using Flask CLI:
flask --app src.main run --host=0.0.0.0 --port=8000
```

## Usage Examples

### 1. Ask a Question
```bash
curl -X POST http://localhost:8000/api/v1/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does authentication work in this system?",
    "max_results": 5
  }'
```

### 2. Validate a Change Request
```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Add support for OAuth2 authentication",
    "feature_type": "new_feature",
    "target_modules": ["auth", "security"]
  }'
```

### 3. Analyze Impact
```bash
curl -X POST http://localhost:8000/api/v1/impact \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Modify the user authentication flow to support MFA",
    "feature_type": "modification"
  }'
```

### 4. Full Analysis (Recommended)
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Add new payment processing module",
    "feature_type": "new_feature",
    "target_modules": ["payment", "billing"]
  }'
```

## Response Format

All endpoints return structured responses following this format:

```json
{
  "summary": "Executive summary",
  "repository_evidence": {
    "chunks": ["relevant code snippets"],
    "file_paths": ["src/module/file.py"],
    "metadata": {}
  },
  "analysis": {
    "reasoning": "Detailed analysis",
    "confidence": 0.85,
    "related_modules": ["module1", "module2"],
    "dependencies": ["dependency1", "dependency2"]
  },
  "impact_assessment": {
    "impact": true,
    "level": "Medium Impact",
    "details": "Impact description",
    "affected_modules": ["module1"],
    "affected_endpoints": ["/api/endpoint1"],
    "affected_flows": ["flow1"],
    "client_impact": "Client-facing impact description",
    "breaking_changes": ["change1"]
  },
  "decision": "SAFE TO IMPLEMENT" | "CHANGE REQUEST WARNING",
  "recommended_next_steps": ["step1", "step2"],
  "mitigation_steps": ["mitigation1"] // Only if warning
}
```

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Index repository
response = requests.post(
    f"{BASE_URL}/index",
    json={"repository_path": "/path/to/repo"}
)
print(response.json())

# Ask a question
response = requests.post(
    f"{BASE_URL}/question",
    json={
        "question": "How does the payment processing work?",
        "max_results": 5
    }
)
print(response.json())

# Full analysis
response = requests.post(
    f"{BASE_URL}/analyze",
    json={
        "description": "Add new feature for email notifications",
        "feature_type": "new_feature"
    }
)
result = response.json()
print(f"Decision: {result['decision']}")
print(f"Impact: {result['impact_assessment']['level']}")
```

## Notes

- The system uses OpenAI embeddings and GPT-4 for analysis
- Vector storage defaults to ChromaDB (local), but can be configured to use Supabase
- Repository indexing may take time depending on repository size
- All responses follow the mandatory format specified in the system requirements


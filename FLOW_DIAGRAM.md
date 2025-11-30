# System Flow Diagrams

Complete flow diagrams showing how the Repository Intelligence Backend works.

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Repository Indexing Flow](#repository-indexing-flow)
3. [Question & Answer Flow](#question--answer-flow)
4. [Change Analysis Flow](#change-analysis-flow)
5. [Complete Request Flow](#complete-request-flow)

---

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        API[API Client<br/>curl/PowerShell/Python]
    end
    
    subgraph "API Layer"
        FLASK[Flask Application<br/>src/main.py]
        ROUTES[API Routes<br/>src/api/routes.py]
    end
    
    subgraph "Service Layer"
        REPO_SVC[RepositoryService<br/>Indexing & Storage]
        ANALYSIS_SVC[AnalysisService<br/>Q&A & Analysis]
    end
    
    subgraph "Chain Layer"
        QA_CHAIN[QA Chain<br/>Question Answering]
        VAL_CHAIN[Validation Chain<br/>Change Validation]
        IMPACT_CHAIN[Impact Chain<br/>Impact Analysis]
        DEC_CHAIN[Decision Chain<br/>Decision Making]
    end
    
    subgraph "Data Layer"
        LOADER[RepositoryLoader<br/>File Loading & Chunking]
        VECTOR[Vector Store<br/>Supabase + OpenAI Embeddings]
        SUPABASE[(Supabase Database<br/>Vector Storage)]
    end
    
    subgraph "External Services"
        GITHUB[GitHub<br/>Repository Cloning]
        OPENAI[OpenAI API<br/>Embeddings & LLM]
    end
    
    API -->|HTTP Requests| FLASK
    FLASK --> ROUTES
    ROUTES -->|Index Requests| REPO_SVC
    ROUTES -->|Q&A/Analysis| ANALYSIS_SVC
    
    REPO_SVC -->|Load Files| LOADER
    REPO_SVC -->|Store Embeddings| VECTOR
    REPO_SVC -->|Clone Repo| GITHUB
    
    ANALYSIS_SVC -->|Answer Questions| QA_CHAIN
    ANALYSIS_SVC -->|Validate Changes| VAL_CHAIN
    ANALYSIS_SVC -->|Analyze Impact| IMPACT_CHAIN
    ANALYSIS_SVC -->|Make Decisions| DEC_CHAIN
    
    QA_CHAIN -->|Search| VECTOR
    VAL_CHAIN -->|Search| VECTOR
    IMPACT_CHAIN -->|Search| VECTOR
    DEC_CHAIN -->|Search| VECTOR
    
    LOADER -->|Generate Embeddings| OPENAI
    VECTOR -->|Store/Retrieve| SUPABASE
    VECTOR -->|Generate Embeddings| OPENAI
    QA_CHAIN -->|LLM Calls| OPENAI
    VAL_CHAIN -->|LLM Calls| OPENAI
    IMPACT_CHAIN -->|LLM Calls| OPENAI
    DEC_CHAIN -->|LLM Calls| OPENAI
```

---

## Repository Indexing Flow

### GitHub Repository Indexing

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask API
    participant RepoService as RepositoryService
    participant GitHubUtil as GitHub Clone Util
    participant Loader as RepositoryLoader
    participant Embeddings as OpenAI Embeddings
    participant VectorStore as Vector Store
    participant Supabase as Supabase DB

    Client->>API: POST /api/v1/index<br/>{repository_path: "https://github.com/user/repo"}
    API->>API: Validate request
    API->>RepoService: index_repository(repository_path)
    
    RepoService->>RepoService: is_github_url()?
    alt GitHub URL
        RepoService->>GitHubUtil: clone_github_repo(url)
        GitHubUtil->>GitHubUtil: Create temp directory
        GitHubUtil->>GitHub: Clone repository
        GitHub-->>GitHubUtil: Repository files
        GitHubUtil-->>RepoService: Temp directory path
    else Local Path
        RepoService->>RepoService: Validate path exists
    end
    
    RepoService->>Loader: RepositoryLoader(path)
    Loader->>Loader: Scan directory for files
    Loader->>Loader: Load files by type<br/>(.py, .js, .md, .pdf, etc.)
    Loader->>Loader: Split into chunks<br/>(RecursiveCharacterTextSplitter)
    Loader-->>RepoService: List[Document]
    
    RepoService->>VectorStore: add_documents(documents)
    VectorStore->>Embeddings: Generate embeddings for each chunk
    Embeddings->>OpenAI: API call (text-embedding-ada-002)
    OpenAI-->>Embeddings: Vector embeddings (1536 dim)
    Embeddings-->>VectorStore: Embeddings + Documents
    VectorStore->>Supabase: Store in repository_embeddings table
    Supabase-->>VectorStore: Success
    
    VectorStore-->>RepoService: Documents indexed
    RepoService->>RepoService: Cleanup temp directory (if cleanup=true)
    RepoService-->>API: Success
    API-->>Client: 200 OK<br/>{status: "success", message: "..."}
```

### File Upload Indexing

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask API
    participant RepoService as RepositoryService
    participant Loader as RepositoryLoader
    participant Embeddings as OpenAI Embeddings
    participant VectorStore as Vector Store
    participant Supabase as Supabase DB

    Client->>API: POST /api/v1/index/file<br/>(multipart/form-data)
    API->>API: Extract file from request
    API->>API: Save to temp directory
    API->>RepoService: index_repository(temp_file_path)
    
    RepoService->>Loader: RepositoryLoader(file_path)
    Loader->>Loader: Detect file type<br/>(PDF, text, etc.)
    Loader->>Loader: Load file content<br/>(PyPDFLoader, TextLoader, etc.)
    Loader->>Loader: Split into chunks
    Loader-->>RepoService: List[Document]
    
    RepoService->>VectorStore: add_documents(documents)
    VectorStore->>Embeddings: Generate embeddings
    Embeddings->>OpenAI: API call
    OpenAI-->>Embeddings: Vector embeddings
    Embeddings-->>VectorStore: Embeddings + Documents
    VectorStore->>Supabase: Store embeddings
    Supabase-->>VectorStore: Success
    
    VectorStore-->>RepoService: Success
    RepoService-->>API: Success
    API->>API: Cleanup temp file
    API-->>Client: 200 OK<br/>{status: "success"}
```

---

## Question & Answer Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask API
    participant AnalysisService as AnalysisService
    participant QAChain as QA Chain
    participant VectorStore as Vector Store
    participant Supabase as Supabase DB
    participant LLM as OpenAI GPT-4

    Client->>API: POST /api/v1/question<br/>{question: "...", max_results: 5}
    API->>API: Validate QuestionRequest
    API->>AnalysisService: answer_question(request)
    
    AnalysisService->>QAChain: answer_question(request)
    QAChain->>QAChain: Prepare query
    QAChain->>VectorStore: similarity_search(question, k=max_results)
    
    VectorStore->>VectorStore: Generate query embedding
    VectorStore->>OpenAI: Embedding API call
    OpenAI-->>VectorStore: Query embedding
    VectorStore->>Supabase: match_documents(query_embedding, k)
    Note over Supabase: Cosine similarity search<br/>using HNSW index
    Supabase-->>VectorStore: Top K similar documents
    
    VectorStore-->>QAChain: List[Document] (relevant chunks)
    QAChain->>QAChain: Build prompt with:<br/>- Question<br/>- Retrieved context
    QAChain->>LLM: GPT-4 API call with prompt
    LLM-->>QAChain: Generated answer
    
    QAChain->>QAChain: Format QuestionResponse
    QAChain-->>AnalysisService: QuestionResponse
    AnalysisService-->>API: QuestionResponse
    API-->>Client: 200 OK<br/>{answer: "...", sources: [...]}
```

---

## Change Analysis Flow

### Full Analysis Flow (Validation + Impact + Decision)

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask API
    participant AnalysisService as AnalysisService
    participant ValChain as Validation Chain
    participant ImpactChain as Impact Chain
    participant DecChain as Decision Chain
    participant VectorStore as Vector Store
    participant LLM as OpenAI GPT-4

    Client->>API: POST /api/v1/analyze<br/>{description, feature_type, ...}
    API->>AnalysisService: full_analysis(request)
    
    par Validation Phase
        AnalysisService->>ValChain: validate_change(request)
        ValChain->>VectorStore: similarity_search(description)
        VectorStore-->>ValChain: Relevant code chunks
        ValChain->>LLM: Validate against codebase
        LLM-->>ValChain: Validation result
        ValChain-->>AnalysisService: ChangeValidationResponse
    and Impact Phase
        AnalysisService->>ImpactChain: analyze_impact(request)
        ImpactChain->>VectorStore: similarity_search(description + modules)
        VectorStore-->>ImpactChain: Relevant code chunks
        ImpactChain->>LLM: Analyze conflicts & impact
        LLM-->>ImpactChain: Impact assessment
        ImpactChain-->>AnalysisService: ImpactAssessment
    end
    
    AnalysisService->>DecChain: make_decision(validation, impact)
    DecChain->>LLM: Synthesize decision
    LLM-->>DecChain: Decision (SAFE/WARNING)
    DecChain-->>AnalysisService: DecisionResponse
    
    AnalysisService-->>API: DecisionResponse
    API-->>Client: 200 OK<br/>{validation, impact, decision, ...}
```

### Individual Analysis Endpoints

```mermaid
graph LR
    subgraph "Validation Endpoint"
        V1[POST /api/v1/validate] --> V2[Validation Chain]
        V2 --> V3[Vector Search]
        V3 --> V4[LLM Validation]
        V4 --> V5[ChangeValidationResponse]
    end
    
    subgraph "Impact Endpoint"
        I1[POST /api/v1/impact] --> I2[Impact Chain]
        I2 --> I3[Vector Search]
        I3 --> I4[LLM Impact Analysis]
        I4 --> I5[ImpactAssessment]
    end
    
    subgraph "Full Analysis Endpoint"
        A1[POST /api/v1/analyze] --> A2[Validation Chain]
        A1 --> A3[Impact Chain]
        A2 --> A4[Decision Chain]
        A3 --> A4
        A4 --> A5[DecisionResponse]
    end
```

---

## Complete Request Flow

### End-to-End Flow: From Indexing to Query

```mermaid
graph TB
    subgraph "Phase 1: Indexing"
        START([Start]) --> INPUT{Input Type?}
        INPUT -->|GitHub URL| GH[Clone GitHub Repo]
        INPUT -->|File Upload| FILE[Save Uploaded File]
        INPUT -->|Local Path| LOCAL[Validate Path]
        
        GH --> LOAD[Load & Parse Files]
        FILE --> LOAD
        LOCAL --> LOAD
        
        LOAD --> CHUNK[Split into Chunks]
        CHUNK --> EMBED[Generate Embeddings<br/>OpenAI API]
        EMBED --> STORE[Store in Supabase<br/>Vector Database]
        STORE --> INDEXED([Repository Indexed])
    end
    
    subgraph "Phase 2: Querying"
        INDEXED --> QUERY{Query Type?}
        
        QUERY -->|Question| QA[QA Chain]
        QUERY -->|Validation| VAL[Validation Chain]
        QUERY -->|Impact| IMP[Impact Chain]
        QUERY -->|Full Analysis| FULL[All Chains]
        
        QA --> SEARCH1[Vector Similarity Search]
        VAL --> SEARCH2[Vector Similarity Search]
        IMP --> SEARCH3[Vector Similarity Search]
        FULL --> SEARCH2
        FULL --> SEARCH3
        
        SEARCH1 --> RETRIEVE1[Retrieve Top K Documents]
        SEARCH2 --> RETRIEVE2[Retrieve Top K Documents]
        SEARCH3 --> RETRIEVE3[Retrieve Top K Documents]
        
        RETRIEVE1 --> LLM1[GPT-4 Processing]
        RETRIEVE2 --> LLM2[GPT-4 Processing]
        RETRIEVE3 --> LLM3[GPT-4 Processing]
        
        LLM1 --> RESP1[QuestionResponse]
        LLM2 --> RESP2[ChangeValidationResponse]
        LLM3 --> RESP3[ImpactAssessment]
        LLM2 --> RESP4[DecisionResponse]
        LLM3 --> RESP4
        
        RESP1 --> END1([Response])
        RESP2 --> END2([Response])
        RESP3 --> END3([Response])
        RESP4 --> END4([Response])
    end
```

---

## Data Flow Diagram

### How Data Moves Through the System

```mermaid
graph LR
    subgraph "Input Sources"
        GH[GitHub Repo]
        FILE[PDF/Text Files]
        LOCAL[Local Directory]
    end
    
    subgraph "Processing"
        CLONE[Git Clone]
        LOAD[File Loaders<br/>PyPDFLoader, TextLoader, etc.]
        SPLIT[Text Splitter<br/>RecursiveCharacterTextSplitter]
    end
    
    subgraph "Embedding"
        EMBED[OpenAI Embeddings<br/>text-embedding-ada-002]
        VEC[1536-dim Vectors]
    end
    
    subgraph "Storage"
        SUPABASE[(Supabase<br/>repository_embeddings<br/>HNSW Index)]
    end
    
    subgraph "Retrieval"
        QUERY[User Query]
        QEMBED[Query Embedding]
        SEARCH[Similarity Search<br/>Cosine Distance]
        RESULTS[Top K Results]
    end
    
    subgraph "Generation"
        PROMPT[Build Prompt<br/>Context + Question]
        GPT4[GPT-4 LLM]
        RESPONSE[Structured Response]
    end
    
    GH --> CLONE
    FILE --> LOAD
    LOCAL --> LOAD
    CLONE --> LOAD
    LOAD --> SPLIT
    SPLIT --> EMBED
    EMBED --> VEC
    VEC --> SUPABASE
    
    QUERY --> QEMBED
    QEMBED --> SEARCH
    SUPABASE --> SEARCH
    SEARCH --> RESULTS
    RESULTS --> PROMPT
    PROMPT --> GPT4
    GPT4 --> RESPONSE
```

---

## Component Interaction Diagram

### Detailed Component Interactions

```mermaid
graph TB
    subgraph "API Layer"
        ROUTES[routes.py<br/>- index_repository<br/>- index_file<br/>- ask_question<br/>- validate_change<br/>- analyze_impact<br/>- full_analysis]
    end
    
    subgraph "Service Layer"
        REPO_SVC[RepositoryService<br/>- index_repository<br/>- is_indexed]
        ANALYSIS_SVC[AnalysisService<br/>- answer_question<br/>- validate_change<br/>- analyze_impact<br/>- full_analysis]
    end
    
    subgraph "Chain Layer"
        QA[QA Chain<br/>- answer_question]
        VAL[Validation Chain<br/>- validate_change]
        IMPACT[Impact Chain<br/>- analyze_impact]
        DEC[Decision Chain<br/>- make_decision]
    end
    
    subgraph "Data Processing"
        LOADER[RepositoryLoader<br/>- load_repository<br/>- _get_file_loader<br/>- _chunk_documents]
        GITHUB_UTIL[GitHub Clone Util<br/>- clone_github_repo<br/>- is_github_url]
    end
    
    subgraph "Storage"
        VECTOR[VectorStore<br/>- add_documents<br/>- similarity_search<br/>- similarity_search_with_score]
        SUPABASE[(Supabase<br/>- repository_embeddings table<br/>- match_documents function)]
    end
    
    subgraph "External"
        OPENAI_EMB[OpenAI Embeddings API]
        OPENAI_LLM[OpenAI GPT-4 API]
    end
    
    ROUTES -->|Index| REPO_SVC
    ROUTES -->|Query/Analysis| ANALYSIS_SVC
    
    REPO_SVC -->|Load| LOADER
    REPO_SVC -->|Clone| GITHUB_UTIL
    REPO_SVC -->|Store| VECTOR
    
    ANALYSIS_SVC -->|Q&A| QA
    ANALYSIS_SVC -->|Validate| VAL
    ANALYSIS_SVC -->|Impact| IMPACT
    ANALYSIS_SVC -->|Decision| DEC
    
    QA -->|Search| VECTOR
    VAL -->|Search| VECTOR
    IMPACT -->|Search| VECTOR
    DEC -->|Search| VECTOR
    
    LOADER -->|Embed| OPENAI_EMB
    VECTOR -->|Embed| OPENAI_EMB
    VECTOR -->|Store/Query| SUPABASE
    
    QA -->|LLM| OPENAI_LLM
    VAL -->|LLM| OPENAI_LLM
    IMPACT -->|LLM| OPENAI_LLM
    DEC -->|LLM| OPENAI_LLM
```

---

## Key Components Summary

### 1. **Indexing Pipeline**
- **Input**: GitHub URL, file upload, or local path
- **Processing**: Clone (if GitHub) → Load files → Chunk text → Generate embeddings
- **Output**: Vector embeddings stored in Supabase

### 2. **Query Pipeline**
- **Input**: User question or change request
- **Processing**: Generate query embedding → Similarity search → Retrieve context → LLM generation
- **Output**: Structured response with answer/analysis

### 3. **Analysis Pipeline**
- **Input**: Change request description
- **Processing**: 
  - Validation: Check against existing codebase
  - Impact: Analyze conflicts and dependencies
  - Decision: Synthesize into SAFE/WARNING decision
- **Output**: Comprehensive analysis with recommendations

### 4. **Vector Search Process**
1. User query → Embedding generation (OpenAI)
2. Query embedding → Supabase similarity search
3. Cosine distance calculation using HNSW index
4. Return top K most similar document chunks
5. Use chunks as context for LLM

---

## Technology Stack Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (curl, PowerShell, Python, JavaScript, Postman, etc.)        │
└───────────────────────┬───────────────────────────────────────┘
                        │ HTTP/REST
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
│  - Flask Framework                                           │
│  - CORS Support                                              │
│  - Blueprint-based Routing                                   │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  - RepositoryService (Indexing)                              │
│  - AnalysisService (Q&A & Analysis)                         │
└───────────────────────┬───────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│  LangChain       │          │  LangChain       │
│  Chains          │          │  Loaders         │
│  - QA Chain      │          │  - TextLoader    │
│  - Validation    │          │  - PyPDFLoader   │
│  - Impact        │          │  - PythonLoader  │
│  - Decision      │          │  - JSONLoader    │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         │                             ▼
         │                    ┌──────────────────┐
         │                    │  Text Splitter    │
         │                    │  (Chunking)       │
         │                    └────────┬───────────┘
         │                             │
         └─────────────┬───────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │    OpenAI Embeddings API    │
         │  (text-embedding-ada-002)    │
         └─────────────┬───────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │    Supabase Vector Store    │
         │  - PostgreSQL + pgvector    │
         │  - HNSW Index               │
         │  - Cosine Similarity        │
         └─────────────┬───────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │      OpenAI GPT-4 API       │
         │  (LLM for Generation)       │
         └─────────────────────────────┘
```

---

## Notes

- **Embeddings**: All text chunks are converted to 1536-dimensional vectors using OpenAI's `text-embedding-ada-002`
- **Vector Search**: Uses cosine similarity with HNSW (Hierarchical Navigable Small World) index for fast approximate nearest neighbor search
- **Chunking**: Documents are split into overlapping chunks (default: 1000 chars with 200 char overlap) for better context preservation
- **LLM**: GPT-4 is used for all reasoning tasks (Q&A, validation, impact analysis, decision making)
- **Storage**: All embeddings are persisted in Supabase PostgreSQL database with vector extension
- **Temporary Files**: GitHub clones and uploaded files are stored temporarily and cleaned up after processing

---

## Viewing These Diagrams

These Mermaid diagrams can be viewed in:
- **GitHub**: Automatically rendered in markdown files
- **VS Code**: With the "Markdown Preview Mermaid Support" extension
- **Online**: Copy diagram code to https://mermaid.live
- **Documentation Tools**: Most modern documentation platforms support Mermaid


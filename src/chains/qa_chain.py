from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.embeddings.vector_store import get_vector_store
from src.models.schemas import QuestionRequest, QuestionResponse, RepositoryEvidence, AnalysisResult
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger()


class RepositoryQAChain:
    """Chain for answering architecture and framework questions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            api_key=self.settings.openai_api_key
        )
        self.vector_store = get_vector_store()
        self._setup_chain()
    
    def _setup_chain(self):
        """Setup the QA chain using LCEL"""
        prompt_template = """You are an expert software architect analyzing a healthcare insurance system repository.

Use the following pieces of context from the repository to answer the question. 
If you don't know the answer based on the provided context, say so explicitly.

Context from repository:
{context}

Question: {question}

Provide a detailed, technically accurate answer based ONLY on the retrieved evidence.
Use terminology suitable for software engineers and architects.
If the context is insufficient, state what additional information would be needed.

Answer:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        retriever = self.vector_store.store.as_retriever(
            search_kwargs={"k": 5}
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Create a chain that properly extracts question from input
        from langchain_core.runnables import RunnableLambda
        
        def extract_question(input_data):
            """Extract question string from input (handles both dict and string)"""
            if isinstance(input_data, dict):
                return input_data.get("question", "")
            return str(input_data)
        
        # Chain: extract question -> retrieve -> format -> prompt -> LLM -> parse
        self.qa_chain = (
            {
                "context": RunnableLambda(extract_question) | retriever | format_docs,
                "question": RunnableLambda(extract_question)
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
    
    def answer_question(self, request: QuestionRequest) -> QuestionResponse:
        """Answer a repository question"""
        logger.info(f"Processing question: {request.question}")
        
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(
            request.question,
            k=request.max_results
        )
        
        # Run QA chain (pass as dict for LCEL)
        answer = self.qa_chain.invoke({"question": request.question})
        
        # Extract evidence
        chunks = [doc.page_content for doc in docs]
        file_paths = list(set([
            doc.metadata.get("file_path", "unknown")
            for doc in docs
        ]))
        
        evidence = RepositoryEvidence(
            chunks=chunks,
            file_paths=file_paths,
            metadata={
                "num_results": len(docs),
                "query": request.question
            }
        )
        
        # Analyze dependencies and modules
        related_modules = self._extract_modules(file_paths)
        dependencies = self._extract_dependencies(chunks)
        
        analysis = AnalysisResult(
            reasoning=answer,
            confidence=0.85,  # Could be calculated based on similarity scores
            related_modules=related_modules,
            dependencies=dependencies
        )
        
        return QuestionResponse(
            summary=f"Answer to: {request.question}",
            repository_evidence=evidence,
            analysis=analysis,
            answer=answer
        )
    
    def _extract_modules(self, file_paths: List[str]) -> List[str]:
        """Extract module names from file paths"""
        modules = set()
        for path in file_paths:
            parts = path.split("/")
            if len(parts) > 1:
                modules.add(parts[0])
        return sorted(list(modules))
    
    def _extract_dependencies(self, chunks: List[str]) -> List[str]:
        """Extract dependency mentions from chunks"""
        dependencies = set()
        keywords = ["import", "from", "depends", "requires", "uses"]
        
        for chunk in chunks:
            for keyword in keywords:
                if keyword in chunk.lower():
                    # Simple extraction - could be enhanced
                    lines = chunk.split("\n")
                    for line in lines:
                        if keyword in line.lower():
                            dependencies.add(line.strip())
        
        return sorted(list(dependencies))[:10]  # Limit to top 10


from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from embeddings.vector_store import get_vector_store
from models.schemas import (
    ChangeRequest,
    ChangeValidationResponse,
    RepositoryEvidence,
    AnalysisResult
)
from utils.logger import get_logger
from utils.config import get_settings

logger = get_logger()


class ChangeValidationChain:
    """Chain for validating change requests"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=self.settings.openai_api_key
        )
        self.vector_store = get_vector_store()
        self._setup_chain()
    
    def _setup_chain(self):
        """Setup validation chain"""
        prompt_template = """You are a software architect validating a change request against a healthcare insurance system repository.

Analyze the change request and compare it with the retrieved repository context.

Change Request:
{change_request}

Repository Context:
{context}

Your task:
1. Determine if the request is logically valid
2. Check for conflicts with existing code, business rules, or API definitions
3. Identify if this duplicates an existing feature
4. Check for contradictions with documented behavior

Respond in JSON format:
{{
    "is_valid": true/false,
    "reasoning": "detailed explanation",
    "conflicts": ["list of conflicts"],
    "duplicates": ["list of duplicate features"],
    "contradictions": ["list of contradictions"]
}}

Response:"""
        
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def validate_change(self, request: ChangeRequest) -> ChangeValidationResponse:
        """Validate a change request"""
        logger.info(f"Validating change request: {request.description}")
        
        # Build search query
        search_query = f"{request.description} {request.feature_type}"
        if request.target_modules:
            search_query += " " + " ".join(request.target_modules)
        
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(search_query, k=10)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Prepare change request text
        change_text = f"""
Type: {request.feature_type}
Description: {request.description}
Target Modules: {request.target_modules or 'Not specified'}
Business Rules: {request.business_rules or 'Not specified'}
"""
        
        # Run validation chain
        result = self.chain.invoke({
            "change_request": change_text,
            "context": context
        })
        
        # Parse result (simplified - in production, use structured output)
        validation_result = self._parse_validation_result(result)
        
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
                "change_type": request.feature_type,
                "num_results": len(docs)
            }
        )
        
        # Build analysis
        related_modules = self._extract_modules(file_paths)
        if request.target_modules:
            related_modules.extend(request.target_modules)
        related_modules = list(set(related_modules))
        
        analysis = AnalysisResult(
            reasoning=validation_result.get("reasoning", ""),
            confidence=0.8 if validation_result.get("is_valid") else 0.9,
            related_modules=related_modules,
            dependencies=self._extract_dependencies(chunks)
        )
        
        return ChangeValidationResponse(
            summary=f"Validation of {request.feature_type} change request",
            repository_evidence=evidence,
            analysis=analysis,
            is_valid=validation_result.get("is_valid", False),
            conflicts=validation_result.get("conflicts", []),
            duplicates=validation_result.get("duplicates", []),
            contradictions=validation_result.get("contradictions", [])
        )
    
    def _parse_validation_result(self, result: str) -> dict:
        """Parse LLM validation result"""
        import json
        import re
        
        # Try to extract JSON from result
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # Fallback: parse text response
        is_valid = "is_valid" in result.lower() and "true" in result.lower()
        conflicts = self._extract_list(result, "conflicts")
        duplicates = self._extract_list(result, "duplicates")
        contradictions = self._extract_list(result, "contradictions")
        
        return {
            "is_valid": is_valid,
            "reasoning": result,
            "conflicts": conflicts,
            "duplicates": duplicates,
            "contradictions": contradictions
        }
    
    def _extract_list(self, text: str, key: str) -> List[str]:
        """Extract list items from text"""
        import re
        pattern = f'"{key}":\\s*\\[([^\\]]+)\\]'
        match = re.search(pattern, text)
        if match:
            items = match.group(1)
            return [item.strip().strip('"') for item in items.split(",")]
        return []
    
    def _extract_modules(self, file_paths: List[str]) -> List[str]:
        """Extract module names from file paths"""
        modules = set()
        for path in file_paths:
            parts = path.split("/")
            if len(parts) > 1:
                modules.add(parts[0])
        return sorted(list(modules))
    
    def _extract_dependencies(self, chunks: List[str]) -> List[str]:
        """Extract dependency mentions"""
        dependencies = set()
        for chunk in chunks:
            if "import" in chunk or "from" in chunk:
                lines = chunk.split("\n")
                for line in lines:
                    if "import" in line or "from" in line:
                        dependencies.add(line.strip())
        return sorted(list(dependencies))[:10]


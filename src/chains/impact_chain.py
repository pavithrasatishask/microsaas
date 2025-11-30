from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.embeddings.vector_store import get_vector_store
from src.models.schemas import (
    ChangeRequest,
    ImpactAssessment,
    ImpactLevel
)
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger()


class ImpactAnalysisChain:
    """Chain for analyzing impact of change requests"""
    
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
        """Setup impact analysis chain"""
        prompt_template = """You are a software architect performing impact analysis on a healthcare insurance system.

Analyze the proposed change and determine its impact on the existing codebase.

Change Request:
{change_request}

Repository Context:
{context}

Your task:
1. Identify all affected modules, endpoints, and business flows
2. Determine impact severity (None, Low, Medium, High, Critical)
3. List any breaking changes
4. Describe client-facing impact

Respond in JSON format:
{{
    "has_impact": true/false,
    "impact_level": "None|Low|Medium|High|Critical",
    "affected_modules": ["module1", "module2"],
    "affected_endpoints": ["/api/endpoint1", "/api/endpoint2"],
    "affected_flows": ["flow1", "flow2"],
    "breaking_changes": ["change1", "change2"],
    "client_impact": "description of client-facing impact",
    "details": "detailed impact analysis"
}}

Response:"""
        
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def analyze_impact(self, request: ChangeRequest) -> ImpactAssessment:
        """Analyze impact of a change request"""
        logger.info(f"Analyzing impact for: {request.description}")
        
        # Build comprehensive search query
        search_terms = [
            request.description,
            request.feature_type
        ]
        if request.target_modules:
            search_terms.extend(request.target_modules)
        
        search_query = " ".join(search_terms)
        
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(search_query, k=15)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Prepare change request text
        change_text = f"""
Type: {request.feature_type}
Description: {request.description}
Target Modules: {request.target_modules or 'Not specified'}
Business Rules: {request.business_rules or 'Not specified'}
"""
        
        # Run impact analysis chain
        result = self.chain.invoke({
            "change_request": change_text,
            "context": context
        })
        
        # Parse result
        impact_result = self._parse_impact_result(result)
        
        # Map impact level
        level_map = {
            "none": ImpactLevel.NONE,
            "low": ImpactLevel.LOW,
            "medium": ImpactLevel.MEDIUM,
            "high": ImpactLevel.HIGH,
            "critical": ImpactLevel.CRITICAL
        }
        
        impact_level = level_map.get(
            impact_result.get("impact_level", "none").lower(),
            ImpactLevel.NONE
        )
        
        return ImpactAssessment(
            impact=impact_result.get("has_impact", False),
            level=impact_level,
            details=impact_result.get("details", ""),
            affected_modules=impact_result.get("affected_modules", []),
            affected_endpoints=impact_result.get("affected_endpoints", []),
            affected_flows=impact_result.get("affected_flows", []),
            client_impact=impact_result.get("client_impact", ""),
            breaking_changes=impact_result.get("breaking_changes", [])
        )
    
    def _parse_impact_result(self, result: str) -> dict:
        """Parse LLM impact analysis result"""
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
        has_impact = "has_impact" in result.lower() and "true" in result.lower()
        
        # Extract impact level
        level = "none"
        for lvl in ["critical", "high", "medium", "low", "none"]:
            if lvl in result.lower():
                level = lvl
                break
        
        affected_modules = self._extract_list(result, "affected_modules")
        affected_endpoints = self._extract_list(result, "affected_endpoints")
        affected_flows = self._extract_list(result, "affected_flows")
        breaking_changes = self._extract_list(result, "breaking_changes")
        
        return {
            "has_impact": has_impact,
            "impact_level": level,
            "affected_modules": affected_modules,
            "affected_endpoints": affected_endpoints,
            "affected_flows": affected_flows,
            "breaking_changes": breaking_changes,
            "client_impact": self._extract_field(result, "client_impact"),
            "details": result
        }
    
    def _extract_list(self, text: str, key: str) -> List[str]:
        """Extract list items from text"""
        import re
        pattern = f'"{key}":\\s*\\[([^\\]]+)\\]'
        match = re.search(pattern, text)
        if match:
            items = match.group(1)
            return [item.strip().strip('"') for item in items.split(",") if item.strip()]
        return []
    
    def _extract_field(self, text: str, key: str) -> str:
        """Extract field value from text"""
        import re
        pattern = f'"{key}":\\s*"([^"]+)"'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return ""


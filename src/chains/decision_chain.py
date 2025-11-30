from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.models.schemas import (
    ChangeRequest,
    ChangeValidationResponse,
    ImpactAssessment,
    DecisionResponse,
    DecisionType,
    RepositoryEvidence,
    AnalysisResult
)
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger()


class DecisionChain:
    """Chain that merges validation and impact analysis to make final decision"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=self.settings.openai_api_key
        )
        self._setup_chain()
    
    def _setup_chain(self):
        """Setup decision chain"""
        prompt_template = """You are a software architect making a final decision on a change request.

Based on the validation and impact analysis, determine if the change is safe to implement.

Change Request:
{change_request}

Validation Results:
{validation}

Impact Assessment:
{impact}

Your task:
1. Review all evidence
2. Make a final decision: SAFE TO IMPLEMENT or CHANGE REQUEST WARNING
3. Provide recommended next steps
4. If warning, suggest mitigation steps

Respond in JSON format:
{{
    "decision": "SAFE TO IMPLEMENT" or "CHANGE REQUEST WARNING",
    "summary": "executive summary",
    "recommended_steps": ["step1", "step2"],
    "mitigation_steps": ["mitigation1", "mitigation2"] (only if warning)
}}

Response:"""
        
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def make_decision(
        self,
        request: ChangeRequest,
        validation: ChangeValidationResponse,
        impact: ImpactAssessment
    ) -> DecisionResponse:
        """Make final decision based on validation and impact"""
        logger.info("Making final decision on change request")
        
        # Prepare inputs
        change_text = f"""
Type: {request.feature_type}
Description: {request.description}
Target Modules: {request.target_modules or 'Not specified'}
"""
        
        validation_text = f"""
Is Valid: {validation.is_valid}
Conflicts: {validation.conflicts}
Duplicates: {validation.duplicates}
Contradictions: {validation.contradictions}
Reasoning: {validation.analysis.reasoning}
"""
        
        impact_text = f"""
Has Impact: {impact.impact}
Level: {impact.level}
Affected Modules: {impact.affected_modules}
Affected Endpoints: {impact.affected_endpoints}
Affected Flows: {impact.affected_flows}
Breaking Changes: {impact.breaking_changes}
Client Impact: {impact.client_impact}
Details: {impact.details}
"""
        
        # Run decision chain
        result = self.chain.invoke({
            "change_request": change_text,
            "validation": validation_text,
            "impact": impact_text
        })
        
        # Parse result
        decision_result = self._parse_decision_result(result)
        
        # Determine decision type
        decision_str = decision_result.get("decision", "").upper()
        if "SAFE" in decision_str or "IMPLEMENT" in decision_str:
            decision_type = DecisionType.SAFE_TO_IMPLEMENT
        else:
            decision_type = DecisionType.CHANGE_REQUEST_WARNING
        
        # Merge evidence from validation
        evidence = validation.repository_evidence
        
        # Merge analysis
        analysis = AnalysisResult(
            reasoning=f"{validation.analysis.reasoning}\n\nImpact: {impact.details}",
            confidence=min(validation.analysis.confidence, 0.9),
            related_modules=list(set(
                validation.analysis.related_modules + impact.affected_modules
            )),
            dependencies=validation.analysis.dependencies
        )
        
        return DecisionResponse(
            summary=decision_result.get("summary", "Decision on change request"),
            repository_evidence=evidence,
            analysis=analysis,
            impact_assessment=impact,
            decision=decision_type,
            recommended_next_steps=decision_result.get("recommended_steps", []),
            mitigation_steps=decision_result.get("mitigation_steps") if decision_type == DecisionType.CHANGE_REQUEST_WARNING else None
        )
    
    def _parse_decision_result(self, result: str) -> dict:
        """Parse LLM decision result"""
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
        decision = "CHANGE REQUEST WARNING"
        if "SAFE" in result.upper() or "IMPLEMENT" in result.upper():
            decision = "SAFE TO IMPLEMENT"
        
        recommended_steps = self._extract_list(result, "recommended_steps")
        mitigation_steps = self._extract_list(result, "mitigation_steps")
        
        return {
            "decision": decision,
            "summary": result[:200] if len(result) > 200 else result,
            "recommended_steps": recommended_steps,
            "mitigation_steps": mitigation_steps
        }
    
    def _extract_list(self, text: str, key: str) -> list:
        """Extract list items from text"""
        import re
        pattern = f'"{key}":\\s*\\[([^\\]]+)\\]'
        match = re.search(pattern, text)
        if match:
            items = match.group(1)
            return [item.strip().strip('"') for item in items.split(",") if item.strip()]
        return []


from chains.qa_chain import RepositoryQAChain
from chains.validation_chain import ChangeValidationChain
from chains.impact_chain import ImpactAnalysisChain
from chains.decision_chain import DecisionChain
from models.schemas import (
    QuestionRequest,
    QuestionResponse,
    ChangeRequest,
    ChangeValidationResponse,
    ImpactAssessment,
    DecisionResponse
)
from utils.logger import get_logger

logger = get_logger()


class AnalysisService:
    """Service for orchestrating analysis chains"""
    
    def __init__(self):
        self.qa_chain = RepositoryQAChain()
        self.validation_chain = ChangeValidationChain()
        self.impact_chain = ImpactAnalysisChain()
        self.decision_chain = DecisionChain()
    
    def answer_question(self, request: QuestionRequest) -> QuestionResponse:
        """Answer a repository question"""
        logger.info(f"Processing question: {request.question}")
        return self.qa_chain.answer_question(request)
    
    def validate_change(self, request: ChangeRequest) -> ChangeValidationResponse:
        """Validate a change request"""
        logger.info(f"Validating change: {request.description}")
        return self.validation_chain.validate_change(request)
    
    def analyze_impact(self, request: ChangeRequest) -> ImpactAssessment:
        """Analyze impact of a change request"""
        logger.info(f"Analyzing impact: {request.description}")
        return self.impact_chain.analyze_impact(request)
    
    def full_analysis(self, request: ChangeRequest) -> DecisionResponse:
        """Perform full analysis: validation + impact + decision"""
        logger.info(f"Performing full analysis: {request.description}")
        
        # Run validation
        validation = self.validate_change(request)
        
        # Run impact analysis
        impact = self.analyze_impact(request)
        
        # Make decision
        decision = self.decision_chain.make_decision(request, validation, impact)
        
        return decision


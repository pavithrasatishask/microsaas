from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ImpactLevel(str, Enum):
    NONE = "No Impact"
    LOW = "Low Impact"
    MEDIUM = "Medium Impact"
    HIGH = "High Impact"
    CRITICAL = "Critical Impact"


class DecisionType(str, Enum):
    SAFE_TO_IMPLEMENT = "SAFE TO IMPLEMENT"
    CHANGE_REQUEST_WARNING = "CHANGE REQUEST WARNING"


class RepositoryEvidence(BaseModel):
    """Evidence retrieved from vector search"""
    chunks: List[str] = Field(description="Relevant code/documentation chunks")
    file_paths: List[str] = Field(description="Source file paths")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AnalysisResult(BaseModel):
    """Result of analysis chain"""
    reasoning: str = Field(description="Detailed reasoning and analysis")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0-1)")
    related_modules: List[str] = Field(default_factory=list, description="Related module names")
    dependencies: List[str] = Field(default_factory=list, description="Dependency chains")


class ImpactAssessment(BaseModel):
    """Impact assessment result"""
    impact: bool = Field(description="Whether impact was detected")
    level: ImpactLevel = Field(description="Impact severity level")
    details: str = Field(description="Detailed impact description")
    affected_modules: List[str] = Field(default_factory=list, description="Affected module names")
    affected_endpoints: List[str] = Field(default_factory=list, description="Affected API endpoints")
    affected_flows: List[str] = Field(default_factory=list, description="Affected business flows")
    client_impact: str = Field(description="Client-facing impact description")
    breaking_changes: List[str] = Field(default_factory=list, description="List of breaking changes")


class QuestionRequest(BaseModel):
    """Request for repository Q&A"""
    question: str = Field(description="Architecture or framework question")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results to retrieve")


class QuestionResponse(BaseModel):
    """Response for repository Q&A"""
    summary: str = Field(description="Summary of the answer")
    repository_evidence: RepositoryEvidence = Field(description="Retrieved evidence from repository")
    analysis: AnalysisResult = Field(description="Analysis result")
    answer: str = Field(description="Complete answer to the question")


class ChangeRequest(BaseModel):
    """Change request or feature proposal"""
    description: str = Field(description="Description of the requested change or feature")
    feature_type: str = Field(description="Type: new_feature, modification, extension, deprecation")
    target_modules: Optional[List[str]] = Field(default=None, description="Target module names if known")
    business_rules: Optional[List[str]] = Field(default=None, description="Related business rules")


class ChangeValidationResponse(BaseModel):
    """Response from change validation chain"""
    summary: str = Field(description="Summary of validation")
    repository_evidence: RepositoryEvidence = Field(description="Retrieved evidence")
    analysis: AnalysisResult = Field(description="Validation analysis")
    is_valid: bool = Field(description="Whether the request is logically valid")
    conflicts: List[str] = Field(default_factory=list, description="List of detected conflicts")
    duplicates: List[str] = Field(default_factory=list, description="List of duplicate features")
    contradictions: List[str] = Field(default_factory=list, description="List of contradictions")


class DecisionResponse(BaseModel):
    """Final decision response combining all analyses"""
    summary: str = Field(description="Executive summary")
    repository_evidence: RepositoryEvidence = Field(description="Retrieved evidence")
    analysis: AnalysisResult = Field(description="Combined analysis")
    impact_assessment: ImpactAssessment = Field(description="Impact assessment")
    decision: DecisionType = Field(description="Final decision")
    recommended_next_steps: List[str] = Field(description="Recommended actions")
    mitigation_steps: Optional[List[str]] = Field(default=None, description="Mitigation steps if warning")


"""
Data models for Neurologix Smart Search POV
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AssessmentType(str, Enum):
    SYMPTOM_CHECKLIST = "symptom_checklist"
    REACTION_TIME = "reaction_time"
    BASELINE = "baseline"
    POST_INJURY = "post_injury"

class SymptomSeverity(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class Patient(BaseModel):
    """Patient data model"""
    patient_id: str
    name: str
    team_id: str
    age: Optional[int] = None
    position: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SymptomData(BaseModel):
    """Symptom assessment data model"""
    symptom_id: str
    patient_id: str
    assessment_date: datetime
    headache_severity: int = Field(ge=0, le=6, description="Headache severity (0-6)")
    nausea_severity: int = Field(ge=0, le=6, description="Nausea severity (0-6)")
    dizziness_severity: int = Field(ge=0, le=6, description="Dizziness severity (0-6)")
    confusion_severity: int = Field(ge=0, le=6, description="Confusion severity (0-6)")
    memory_problems_severity: int = Field(ge=0, le=6, description="Memory problems severity (0-6)")
    emotional_symptoms_severity: int = Field(ge=0, le=6, description="Emotional symptoms severity (0-6)")
    total_symptom_score: int = Field(ge=0, le=132, description="Total symptom score")
    assessment_type: AssessmentType

class ReactionTimeData(BaseModel):
    """Reaction time test data model"""
    test_id: str
    patient_id: str
    assessment_date: datetime
    average_reaction_time: float = Field(description="Average reaction time in milliseconds")
    best_reaction_time: float = Field(description="Best reaction time in milliseconds")
    worst_reaction_time: float = Field(description="Worst reaction time in milliseconds")
    total_attempts: int = Field(ge=1, description="Total number of test attempts")
    successful_attempts: int = Field(ge=0, description="Number of successful attempts")
    accuracy_percentage: float = Field(ge=0, le=100, description="Accuracy percentage")
    assessment_type: AssessmentType

class QueryContext(BaseModel):
    """Context for natural language queries"""
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    modules: List[AssessmentType] = []
    filters: Dict[str, Any] = {}

class AnalysisResult(BaseModel):
    """Result of data analysis"""
    metric_name: str
    value: float
    unit: str
    description: str
    patient_count: int
    date_range: Dict[str, datetime]

class QueryClassification(BaseModel):
    """Classification of natural language query"""
    intent: str = Field(description="The main intent of the query")
    modules: List[AssessmentType] = Field(description="Relevant assessment modules")
    metrics: List[str] = Field(description="Metrics to calculate")
    filters: Dict[str, Any] = Field(description="Filters to apply")
    time_range: Optional[Dict[str, str]] = Field(description="Time range filters")
    confidence: float = Field(ge=0, le=1, description="Classification confidence")

class DatabaseConfig(BaseModel):
    """Database configuration model"""
    host: str
    port: int
    database: str
    username: str
    password: str
    
class AWSConfig(BaseModel):
    """AWS configuration model"""
    access_key_id: str
    secret_access_key: str
    region: str
    s3_bucket: str
    rds_endpoint: str
    opensearch_endpoint: str

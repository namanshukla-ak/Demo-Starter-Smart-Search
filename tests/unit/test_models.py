"""
Unit tests for data models and schemas
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from backend.models.schemas import (
    Patient, SymptomData, ReactionTimeData, QueryClassification,
    AssessmentType, SymptomSeverity, QueryContext, AnalysisResult
)

class TestPatientModel:
    """Test Patient data model"""
    
    def test_valid_patient_creation(self):
        """Test creating a valid patient"""
        patient = Patient(
            patient_id="P001",
            name="John Smith",
            team_id="LSU_TIGERS",
            age=20,
            position="Quarterback",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert patient.patient_id == "P001"
        assert patient.name == "John Smith"
        assert patient.team_id == "LSU_TIGERS"
        assert patient.age == 20
        assert patient.position == "Quarterback"
    
    def test_patient_without_optional_fields(self):
        """Test creating patient without optional fields"""
        patient = Patient(
            patient_id="P002",
            name="Jane Doe",
            team_id="DEMO_TEAM",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert patient.age is None
        assert patient.position is None
    
    def test_invalid_patient_missing_required_fields(self):
        """Test validation error for missing required fields"""
        with pytest.raises(ValidationError):
            Patient(
                name="Invalid Patient"
                # Missing required fields
            )

class TestSymptomDataModel:
    """Test SymptomData model"""
    
    def test_valid_symptom_data_creation(self):
        """Test creating valid symptom data"""
        symptom_data = SymptomData(
            symptom_id="S001",
            patient_id="P001",
            assessment_date=datetime.now(),
            headache_severity=3,
            nausea_severity=2,
            dizziness_severity=1,
            confusion_severity=0,
            memory_problems_severity=2,
            emotional_symptoms_severity=1,
            total_symptom_score=45,
            assessment_type=AssessmentType.BASELINE
        )
        
        assert symptom_data.headache_severity == 3
        assert symptom_data.total_symptom_score == 45
        assert symptom_data.assessment_type == AssessmentType.BASELINE
    
    def test_symptom_severity_validation(self):
        """Test symptom severity validation (0-6 range)"""
        # Valid severity
        symptom_data = SymptomData(
            symptom_id="S001",
            patient_id="P001",
            assessment_date=datetime.now(),
            headache_severity=6,  # Max valid value
            total_symptom_score=100,
            assessment_type=AssessmentType.BASELINE
        )
        assert symptom_data.headache_severity == 6
        
        # Invalid severity - too high
        with pytest.raises(ValidationError):
            SymptomData(
                symptom_id="S002",
                patient_id="P001",
                assessment_date=datetime.now(),
                headache_severity=7,  # Invalid - above max
                total_symptom_score=100,
                assessment_type=AssessmentType.BASELINE
            )
        
        # Invalid severity - negative
        with pytest.raises(ValidationError):
            SymptomData(
                symptom_id="S003",
                patient_id="P001",
                assessment_date=datetime.now(),
                headache_severity=-1,  # Invalid - negative
                total_symptom_score=100,
                assessment_type=AssessmentType.BASELINE
            )
    
    def test_total_symptom_score_validation(self):
        """Test total symptom score validation (0-132 range)"""
        # Valid score
        symptom_data = SymptomData(
            symptom_id="S001",
            patient_id="P001",
            assessment_date=datetime.now(),
            total_symptom_score=132,  # Max valid value
            assessment_type=AssessmentType.BASELINE
        )
        assert symptom_data.total_symptom_score == 132
        
        # Invalid score - too high
        with pytest.raises(ValidationError):
            SymptomData(
                symptom_id="S002",
                patient_id="P001",
                assessment_date=datetime.now(),
                total_symptom_score=133,  # Invalid - above max
                assessment_type=AssessmentType.BASELINE
            )

class TestReactionTimeDataModel:
    """Test ReactionTimeData model"""
    
    def test_valid_reaction_time_creation(self):
        """Test creating valid reaction time data"""
        reaction_data = ReactionTimeData(
            test_id="R001",
            patient_id="P001",
            assessment_date=datetime.now(),
            average_reaction_time=245.5,
            best_reaction_time=198.2,
            worst_reaction_time=312.1,
            total_attempts=50,
            successful_attempts=47,
            accuracy_percentage=94.0,
            assessment_type=AssessmentType.BASELINE
        )
        
        assert reaction_data.average_reaction_time == 245.5
        assert reaction_data.accuracy_percentage == 94.0
        assert reaction_data.assessment_type == AssessmentType.BASELINE
    
    def test_reaction_time_validation(self):
        """Test reaction time validation (must be positive)"""
        # Valid reaction time
        reaction_data = ReactionTimeData(
            test_id="R001",
            patient_id="P001",
            assessment_date=datetime.now(),
            average_reaction_time=200.0,
            best_reaction_time=150.0,
            worst_reaction_time=300.0,
            total_attempts=50,
            successful_attempts=47,
            accuracy_percentage=94.0,
            assessment_type=AssessmentType.BASELINE
        )
        assert reaction_data.average_reaction_time == 200.0
        
        # Invalid reaction time - negative
        with pytest.raises(ValidationError):
            ReactionTimeData(
                test_id="R002",
                patient_id="P001",
                assessment_date=datetime.now(),
                average_reaction_time=-100.0,  # Invalid - negative
                best_reaction_time=150.0,
                worst_reaction_time=300.0,
                total_attempts=50,
                successful_attempts=47,
                accuracy_percentage=94.0,
                assessment_type=AssessmentType.BASELINE
            )
    
    def test_accuracy_percentage_validation(self):
        """Test accuracy percentage validation (0-100 range)"""
        # Valid accuracy
        reaction_data = ReactionTimeData(
            test_id="R001",
            patient_id="P001",
            assessment_date=datetime.now(),
            average_reaction_time=200.0,
            best_reaction_time=150.0,
            worst_reaction_time=300.0,
            total_attempts=50,
            successful_attempts=50,
            accuracy_percentage=100.0,  # Max valid value
            assessment_type=AssessmentType.BASELINE
        )
        assert reaction_data.accuracy_percentage == 100.0
        
        # Invalid accuracy - above 100
        with pytest.raises(ValidationError):
            ReactionTimeData(
                test_id="R002",
                patient_id="P001",
                assessment_date=datetime.now(),
                average_reaction_time=200.0,
                best_reaction_time=150.0,
                worst_reaction_time=300.0,
                total_attempts=50,
                successful_attempts=47,
                accuracy_percentage=101.0,  # Invalid - above max
                assessment_type=AssessmentType.BASELINE
            )
    
    def test_attempts_validation(self):
        """Test attempts validation (total >= successful >= 0)"""
        # Valid attempts
        reaction_data = ReactionTimeData(
            test_id="R001",
            patient_id="P001",
            assessment_date=datetime.now(),
            average_reaction_time=200.0,
            best_reaction_time=150.0,
            worst_reaction_time=300.0,
            total_attempts=50,
            successful_attempts=47,
            accuracy_percentage=94.0,
            assessment_type=AssessmentType.BASELINE
        )
        assert reaction_data.total_attempts == 50
        assert reaction_data.successful_attempts == 47
        
        # Invalid - negative total attempts
        with pytest.raises(ValidationError):
            ReactionTimeData(
                test_id="R002",
                patient_id="P001",
                assessment_date=datetime.now(),
                average_reaction_time=200.0,
                best_reaction_time=150.0,
                worst_reaction_time=300.0,
                total_attempts=-1,  # Invalid - negative
                successful_attempts=47,
                accuracy_percentage=94.0,
                assessment_type=AssessmentType.BASELINE
            )

class TestQueryClassificationModel:
    """Test QueryClassification model"""
    
    def test_valid_query_classification(self):
        """Test creating valid query classification"""
        classification = QueryClassification(
            intent="average",
            modules=[AssessmentType.SYMPTOM_CHECKLIST],
            metrics=["headache_severity"],
            filters={"team": "LSU_TIGERS"},
            time_range={"period": "last_week"},
            confidence=0.85
        )
        
        assert classification.intent == "average"
        assert AssessmentType.SYMPTOM_CHECKLIST in classification.modules
        assert "headache_severity" in classification.metrics
        assert classification.confidence == 0.85
    
    def test_confidence_validation(self):
        """Test confidence validation (0-1 range)"""
        # Valid confidence
        classification = QueryClassification(
            intent="average",
            modules=[AssessmentType.SYMPTOM_CHECKLIST],
            metrics=["headache_severity"],
            filters={},
            confidence=1.0  # Max valid value
        )
        assert classification.confidence == 1.0
        
        # Invalid confidence - above 1
        with pytest.raises(ValidationError):
            QueryClassification(
                intent="average",
                modules=[AssessmentType.SYMPTOM_CHECKLIST],
                metrics=["headache_severity"],
                filters={},
                confidence=1.5  # Invalid - above max
            )
        
        # Invalid confidence - negative
        with pytest.raises(ValidationError):
            QueryClassification(
                intent="average",
                modules=[AssessmentType.SYMPTOM_CHECKLIST],
                metrics=["headache_severity"],
                filters={},
                confidence=-0.1  # Invalid - negative
            )

class TestEnums:
    """Test enum values"""
    
    def test_assessment_type_enum(self):
        """Test AssessmentType enum values"""
        assert AssessmentType.SYMPTOM_CHECKLIST == "symptom_checklist"
        assert AssessmentType.REACTION_TIME == "reaction_time"
        assert AssessmentType.BASELINE == "baseline"
        assert AssessmentType.POST_INJURY == "post_injury"
    
    def test_symptom_severity_enum(self):
        """Test SymptomSeverity enum values"""
        assert SymptomSeverity.NONE == "none"
        assert SymptomSeverity.MILD == "mild"
        assert SymptomSeverity.MODERATE == "moderate"
        assert SymptomSeverity.SEVERE == "severe"

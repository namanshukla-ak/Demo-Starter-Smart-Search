"""
Test configuration and fixtures for Neurologix Smart Search POV
"""
import pytest
import os
import asyncio
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set test environment
os.environ["TESTING"] = "True"
os.environ["DB_NAME"] = "neurologix_test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_settings():
    """Mock application settings for testing"""
    from config.settings import Settings
    
    settings = Settings(
        # Database config
        db_host="localhost",
        db_port=3306,
        db_name="neurologix_test_db",
        db_user="test_user",
        db_password="test_password",
        
        # AWS config (mock)
        aws_access_key_id="test_access_key",
        aws_secret_access_key="test_secret_key",
        aws_region="us-east-1",
        aws_s3_bucket="test-bucket",
        aws_rds_endpoint="test-rds-endpoint",
        aws_opensearch_endpoint="test-opensearch-endpoint",
        
        # Test mode
        debug=True,
        testing=True
    )
    
    with patch('config.settings.get_settings', return_value=settings):
        yield settings

@pytest.fixture
def mock_database():
    """Mock database session for testing"""
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    from backend.models.schemas import Patient, SymptomData, ReactionTimeData
    # Note: In real implementation, you'd use SQLAlchemy Base.metadata.create_all(engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_patients():
    """Sample patient data for testing"""
    return [
        {
            "patient_id": "P001",
            "name": "John Smith",
            "team_id": "LSU_TIGERS",
            "age": 20,
            "position": "Quarterback"
        },
        {
            "patient_id": "P002", 
            "name": "Sarah Wilson",
            "team_id": "LSU_TIGERS",
            "age": 19,
            "position": "Defender"
        }
    ]

@pytest.fixture
def sample_symptom_data():
    """Sample symptom assessment data for testing"""
    return [
        {
            "symptom_id": "S001",
            "patient_id": "P001",
            "assessment_date": datetime.now() - timedelta(days=5),
            "headache_severity": 2,
            "nausea_severity": 1,
            "dizziness_severity": 0,
            "confusion_severity": 1,
            "memory_problems_severity": 2,
            "emotional_symptoms_severity": 1,
            "total_symptom_score": 35,
            "assessment_type": "baseline"
        },
        {
            "symptom_id": "S002",
            "patient_id": "P001",
            "assessment_date": datetime.now() - timedelta(days=1),
            "headache_severity": 4,
            "nausea_severity": 3,
            "dizziness_severity": 2,
            "confusion_severity": 3,
            "memory_problems_severity": 4,
            "emotional_symptoms_severity": 3,
            "total_symptom_score": 78,
            "assessment_type": "post_injury"
        }
    ]

@pytest.fixture
def sample_reaction_time_data():
    """Sample reaction time test data for testing"""
    return [
        {
            "test_id": "R001",
            "patient_id": "P001", 
            "assessment_date": datetime.now() - timedelta(days=5),
            "average_reaction_time": 245.5,
            "best_reaction_time": 198.2,
            "worst_reaction_time": 312.1,
            "total_attempts": 50,
            "successful_attempts": 47,
            "accuracy_percentage": 94.0,
            "assessment_type": "baseline"
        },
        {
            "test_id": "R002",
            "patient_id": "P001",
            "assessment_date": datetime.now() - timedelta(days=1),
            "average_reaction_time": 298.7,
            "best_reaction_time": 241.3,
            "worst_reaction_time": 387.9,
            "total_attempts": 50,
            "successful_attempts": 42,
            "accuracy_percentage": 84.0,
            "assessment_type": "post_injury"
        }
    ]

@pytest.fixture
def mock_aws_clients():
    """Mock AWS clients for testing"""
    mock_s3 = Mock()
    mock_s3.get_object.return_value = {
        'Body': Mock(read=lambda: b'{"detailed_assessment": "test_data"}')
    }
    
    mock_opensearch = Mock()
    
    with patch('boto3.client') as mock_boto_client:
        def client_side_effect(service_name, **kwargs):
            if service_name == 's3':
                return mock_s3
            elif service_name == 'opensearch':
                return mock_opensearch
            return Mock()
        
        mock_boto_client.side_effect = client_side_effect
        yield {
            's3': mock_s3,
            'opensearch': mock_opensearch
        }

@pytest.fixture
def test_client():
    """FastAPI test client"""
    from backend.main import app
    return TestClient(app)

@pytest.fixture
def sample_queries():
    """Sample natural language queries for testing"""
    return [
        {
            "question": "What is the average headache severity for LSU players?",
            "expected_intent": "average",
            "expected_modules": ["symptom_checklist"],
            "expected_metrics": ["headache_severity"]
        },
        {
            "question": "Show me players with reaction time above 300ms",
            "expected_intent": "list",
            "expected_modules": ["reaction_time"],
            "expected_metrics": ["average_reaction_time"]
        },
        {
            "question": "List players with high symptom scores and slow reaction times",
            "expected_intent": "list",
            "expected_modules": ["symptom_checklist", "reaction_time"],
            "expected_metrics": ["total_symptom_score", "average_reaction_time"]
        }
    ]

@pytest.fixture
def mock_openai():
    """Mock OpenAI API for testing"""
    with patch('openai.chat.completions.create') as mock_create:
        mock_create.return_value = Mock(
            choices=[Mock(
                message=Mock(
                    content='{"intent": "average", "modules": ["symptom_checklist"], "confidence": 0.85}'
                )
            )]
        )
        yield mock_create

"""
Unit tests for query processor service
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from backend.services.query_processor import QueryProcessor
from backend.models.schemas import AssessmentType, QueryClassification

class TestQueryProcessor:
    """Test QueryProcessor class"""
    
    @pytest.fixture
    def mock_query_processor(self, mock_settings):
        """Create a mocked query processor"""
        with patch('backend.services.query_processor.DatabaseService') as mock_db_service_class:
            mock_db_service = Mock()
            mock_db_service_class.return_value = mock_db_service
            
            processor = QueryProcessor()
            processor.db_service = mock_db_service  # Store mock for testing
            yield processor
    
    def test_query_processor_initialization(self, mock_query_processor):
        """Test query processor initialization"""
        assert mock_query_processor is not None
        assert hasattr(mock_query_processor, 'symptom_keywords')
        assert hasattr(mock_query_processor, 'reaction_time_keywords')
        assert hasattr(mock_query_processor, 'aggregation_keywords')
        assert hasattr(mock_query_processor, 'time_patterns')
    
    def test_classify_symptom_query(self, mock_query_processor):
        """Test classifying symptom-related queries"""
        question = "What is the average headache severity for LSU players?"
        
        classification = mock_query_processor.classify_query(question)
        
        assert classification.intent == "average"
        assert AssessmentType.SYMPTOM_CHECKLIST in classification.modules
        assert "headache_severity" in classification.metrics
        assert isinstance(classification.confidence, float)
        assert 0 <= classification.confidence <= 1
    
    def test_classify_reaction_time_query(self, mock_query_processor):
        """Test classifying reaction time-related queries"""
        question = "Show me players with reaction time above 300ms"
        
        classification = mock_query_processor.classify_query(question)
        
        assert classification.intent == "list"
        assert AssessmentType.REACTION_TIME in classification.modules
        assert "average_reaction_time" in classification.metrics
    
    def test_classify_combined_query(self, mock_query_processor):
        """Test classifying queries involving both modules"""
        question = "List players with high symptom scores and slow reaction times"
        
        classification = mock_query_processor.classify_query(question)
        
        assert classification.intent == "list"
        assert AssessmentType.SYMPTOM_CHECKLIST in classification.modules
        assert AssessmentType.REACTION_TIME in classification.modules
        assert "total_symptom_score" in classification.metrics
        assert "average_reaction_time" in classification.metrics
    
    def test_classify_generic_query(self, mock_query_processor):
        """Test classifying generic queries (no specific keywords)"""
        question = "Tell me about the team performance"
        
        classification = mock_query_processor.classify_query(question)
        
        # Should include both modules when no specific module detected
        assert len(classification.modules) == 2
        assert AssessmentType.SYMPTOM_CHECKLIST in classification.modules
        assert AssessmentType.REACTION_TIME in classification.modules
    
    def test_determine_intent_average(self, mock_query_processor):
        """Test intent determination for average queries"""
        question = "what is the average headache score"
        intent = mock_query_processor._determine_intent(question)
        assert intent == "average"
        
        question = "show me the mean symptom severity"
        intent = mock_query_processor._determine_intent(question)
        assert intent == "average"
    
    def test_determine_intent_maximum(self, mock_query_processor):
        """Test intent determination for maximum queries"""
        question = "what is the highest reaction time"
        intent = mock_query_processor._determine_intent(question)
        assert intent == "maximum"
        
        question = "show me the worst performance"
        intent = mock_query_processor._determine_intent(question)
        assert intent == "maximum"
    
    def test_determine_intent_list(self, mock_query_processor):
        """Test intent determination for list queries"""
        question = "list all players with symptoms"
        intent = mock_query_processor._determine_intent(question)
        assert intent == "list"
        
        question = "show me the players"
        intent = mock_query_processor._determine_intent(question)
        assert intent == "list"
    
    def test_extract_time_range_last_week(self, mock_query_processor):
        """Test extracting 'last week' time range"""
        question = "show me data from last week"
        time_range = mock_query_processor._extract_time_range(question)
        
        assert time_range is not None
        assert time_range["period"] == "last_week"
    
    def test_extract_time_range_last_month(self, mock_query_processor):
        """Test extracting 'last month' time range"""
        question = "what happened in the past month"
        time_range = mock_query_processor._extract_time_range(question)
        
        assert time_range is not None
        assert time_range["period"] == "last_month"
    
    def test_extract_time_range_none(self, mock_query_processor):
        """Test when no time range is specified"""
        question = "show me the data"
        time_range = mock_query_processor._extract_time_range(question)
        
        assert time_range is None
    
    def test_extract_filters_team(self, mock_query_processor):
        """Test extracting team filters"""
        question = "show me LSU players with symptoms"
        filters = mock_query_processor._extract_filters(question)
        
        assert "team" in filters
        assert filters["team"] == "LSU"
    
    def test_extract_filters_severity(self, mock_query_processor):
        """Test extracting severity filters"""
        question = "show me players with severe symptoms"
        filters = mock_query_processor._extract_filters(question)
        
        assert "min_severity" in filters
        assert filters["min_severity"] == 4
        
        question = "list moderate symptom cases"
        filters = mock_query_processor._extract_filters(question)
        
        assert "min_severity" in filters
        assert filters["min_severity"] == 2
    
    def test_convert_time_range_last_week(self, mock_query_processor):
        """Test converting 'last week' time range to datetime"""
        time_range = {"period": "last_week"}
        result = mock_query_processor._convert_time_range(time_range)
        
        assert "start" in result
        assert "end" in result
        assert result["start"] is not None
        assert result["end"] is not None
        assert isinstance(result["start"], datetime)
        assert isinstance(result["end"], datetime)
        
        # Verify it's approximately one week ago
        now = datetime.now()
        week_ago = now - timedelta(weeks=1)
        assert abs((result["start"] - week_ago).total_seconds()) < 3600  # Within 1 hour
    
    def test_convert_time_range_none(self, mock_query_processor):
        """Test converting None time range"""
        result = mock_query_processor._convert_time_range(None)
        
        assert result["start"] is None
        assert result["end"] is None
    
    def test_process_query_symptom_only(self, mock_query_processor):
        """Test processing a symptom-only query"""
        question = "What is the average headache severity?"
        
        # Mock database responses
        mock_query_processor.db_service.get_symptom_data.return_value = [
            {'total_symptom_score': 35, 'headache_severity': 2, 'patient_id': 'P001'},
            {'total_symptom_score': 78, 'headache_severity': 4, 'patient_id': 'P002'}
        ]
        mock_query_processor.db_service.calculate_symptom_metrics.return_value = {
            'avg_total_symptom_score': 56.5,
            'avg_headache_severity': 3.0
        }
        
        result = mock_query_processor.process_query(question)
        
        assert "answer" in result
        assert "confidence" in result
        assert "source_modules" in result
        assert "metadata" in result
        assert "symptom_checklist" in result["source_modules"]
        assert "symptom" in result["answer"].lower() or "headache" in result["answer"].lower()
    
    def test_process_query_reaction_time_only(self, mock_query_processor):
        """Test processing a reaction time-only query"""
        question = "Show me reaction times for the team"
        
        # Mock database responses
        mock_query_processor.db_service.get_reaction_time_data.return_value = [
            {'average_reaction_time': 245.5, 'accuracy_percentage': 94.0, 'patient_id': 'P001'},
            {'average_reaction_time': 298.7, 'accuracy_percentage': 84.0, 'patient_id': 'P002'}
        ]
        mock_query_processor.db_service.calculate_reaction_time_metrics.return_value = {
            'avg_reaction_time': 272.1,
            'avg_accuracy': 89.0
        }
        
        result = mock_query_processor.process_query(question)
        
        assert "answer" in result
        assert "reaction_time" in result["source_modules"]
        assert "reaction" in result["answer"].lower() or "time" in result["answer"].lower()
    
    def test_process_query_combined_modules(self, mock_query_processor):
        """Test processing a query involving both modules"""
        question = "Show me overall patient assessments"
        
        # Mock database responses for both modules
        mock_query_processor.db_service.get_symptom_data.return_value = [
            {'total_symptom_score': 35, 'headache_severity': 2, 'patient_id': 'P001'}
        ]
        mock_query_processor.db_service.get_reaction_time_data.return_value = [
            {'average_reaction_time': 245.5, 'accuracy_percentage': 94.0, 'patient_id': 'P001'}
        ]
        mock_query_processor.db_service.calculate_symptom_metrics.return_value = {
            'avg_total_symptom_score': 35.0,
            'avg_headache_severity': 2.0
        }
        mock_query_processor.db_service.calculate_reaction_time_metrics.return_value = {
            'avg_reaction_time': 245.5,
            'avg_accuracy': 94.0
        }
        
        result = mock_query_processor.process_query(question)
        
        assert "answer" in result
        assert len(result["source_modules"]) == 2
        assert "symptom_checklist" in result["source_modules"]
        assert "reaction_time" in result["source_modules"]
    
    def test_process_query_no_data(self, mock_query_processor):
        """Test processing a query with no matching data"""
        question = "Show me data for non-existent team"
        
        # Mock empty database responses
        mock_query_processor.db_service.get_symptom_data.return_value = []
        mock_query_processor.db_service.get_reaction_time_data.return_value = []
        
        result = mock_query_processor.process_query(question)
        
        assert "answer" in result
        assert "couldn't find" in result["answer"].lower() or "no data" in result["answer"].lower()
        assert len(result["source_modules"]) == 0
    
    def test_generate_response_symptom_data(self, mock_query_processor):
        """Test generating response for symptom data"""
        classification = QueryClassification(
            intent="average",
            modules=[AssessmentType.SYMPTOM_CHECKLIST],
            metrics=["total_symptom_score"],
            filters={},
            confidence=0.8
        )
        
        results = [{
            "module": "symptom_checklist",
            "data": {
                "avg_total_symptom_score": 56.5,
                "avg_headache_severity": 3.0
            },
            "count": 10
        }]
        
        response = mock_query_processor._generate_response(classification, results)
        
        assert "symptom" in response.lower()
        assert "56.5" in response
        assert "10" in response
    
    def test_generate_response_reaction_time_data(self, mock_query_processor):
        """Test generating response for reaction time data"""
        classification = QueryClassification(
            intent="average",
            modules=[AssessmentType.REACTION_TIME],
            metrics=["average_reaction_time"],
            filters={},
            confidence=0.8
        )
        
        results = [{
            "module": "reaction_time",
            "data": {
                "avg_reaction_time": 272.1,
                "avg_accuracy": 89.0
            },
            "count": 8
        }]
        
        response = mock_query_processor._generate_response(classification, results)
        
        assert "reaction" in response.lower()
        assert "272" in response
        assert "89.0" in response
        assert "8" in response
    
    def test_generate_response_empty_results(self, mock_query_processor):
        """Test generating response for empty results"""
        classification = QueryClassification(
            intent="list",
            modules=[AssessmentType.SYMPTOM_CHECKLIST],
            metrics=["total_symptom_score"],
            filters={},
            confidence=0.8
        )
        
        results = []
        
        response = mock_query_processor._generate_response(classification, results)
        
        assert "couldn't find" in response.lower() or "no data" in response.lower()

class TestQueryProcessorErrorHandling:
    """Test error handling in query processor"""
    
    def test_database_error_handling(self, mock_settings):
        """Test handling of database errors"""
        with patch('backend.services.query_processor.DatabaseService') as mock_db_service_class:
            mock_db_service = Mock()
            mock_db_service.get_symptom_data.side_effect = Exception("Database error")
            mock_db_service_class.return_value = mock_db_service
            
            processor = QueryProcessor()
            
            with pytest.raises(Exception):
                processor.process_query("Test query")
    
    def test_invalid_query_handling(self, mock_query_processor):
        """Test handling of invalid queries"""
        # Empty query
        result = mock_query_processor.classify_query("")
        assert result.intent == "summary"  # Default intent
        
        # Very short query
        result = mock_query_processor.classify_query("a")
        assert result.intent == "summary"

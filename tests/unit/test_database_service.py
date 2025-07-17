"""
Unit tests for database service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from backend.services.database_service import DatabaseService
from backend.models.schemas import AssessmentType

class TestDatabaseService:
    """Test DatabaseService class"""
    
    @pytest.fixture
    def mock_db_service(self, mock_settings, mock_aws_clients):
        """Create a mocked database service"""
        with patch('backend.services.database_service.create_engine') as mock_engine, \
             patch('backend.services.database_service.sessionmaker') as mock_sessionmaker, \
             patch('backend.services.database_service.boto3.client') as mock_boto_client:
            
            # Mock database session
            mock_session = Mock()
            mock_sessionmaker.return_value = Mock(return_value=mock_session)
            
            # Mock boto3 client creation
            mock_boto_client.side_effect = lambda service, **kwargs: mock_aws_clients[service]
            
            service = DatabaseService()
            service._session = mock_session  # Store mock session for testing
            yield service
    
    def test_database_service_initialization(self, mock_db_service):
        """Test database service initialization"""
        assert mock_db_service is not None
        assert hasattr(mock_db_service, 's3_client')
        assert hasattr(mock_db_service, 'opensearch_client')
    
    def test_get_patients_by_team(self, mock_db_service, sample_patients):
        """Test getting patients by team"""
        # Mock database query result
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([
            Mock(_mapping={'patient_id': 'P001', 'name': 'John Smith', 'team_id': 'LSU_TIGERS'}),
            Mock(_mapping={'patient_id': 'P002', 'name': 'Sarah Wilson', 'team_id': 'LSU_TIGERS'})
        ]))
        
        mock_db_service._session.execute.return_value = mock_result
        mock_db_service._session.__enter__ = Mock(return_value=mock_db_service._session)
        mock_db_service._session.__exit__ = Mock(return_value=None)
        
        with patch.object(mock_db_service, 'get_db_session', return_value=mock_db_service._session):
            result = mock_db_service.get_patients_by_team("LSU_TIGERS")
        
        assert len(result) == 2
        assert result[0]['patient_id'] == 'P001'
        assert result[1]['patient_id'] == 'P002'
        mock_db_service._session.execute.assert_called_once()
    
    def test_get_symptom_data_with_filters(self, mock_db_service, sample_symptom_data):
        """Test getting symptom data with various filters"""
        # Mock database query result
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([
            Mock(_mapping=sample_symptom_data[0]),
            Mock(_mapping=sample_symptom_data[1])
        ]))
        
        mock_db_service._session.execute.return_value = mock_result
        mock_db_service._session.__enter__ = Mock(return_value=mock_db_service._session)
        mock_db_service._session.__exit__ = Mock(return_value=None)
        
        with patch.object(mock_db_service, 'get_db_session', return_value=mock_db_service._session):
            result = mock_db_service.get_symptom_data(
                patient_id="P001",
                team_id="LSU_TIGERS",
                date_from=datetime.now() - timedelta(days=7),
                date_to=datetime.now()
            )
        
        assert len(result) == 2
        mock_db_service._session.execute.assert_called_once()
        
        # Verify the query parameters were used
        call_args = mock_db_service._session.execute.call_args
        assert "patient_id" in call_args[0][1]
        assert "team_id" in call_args[0][1]
        assert "date_from" in call_args[0][1]
        assert "date_to" in call_args[0][1]
    
    def test_get_reaction_time_data_with_filters(self, mock_db_service, sample_reaction_time_data):
        """Test getting reaction time data with filters"""
        # Mock database query result
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([
            Mock(_mapping=sample_reaction_time_data[0]),
            Mock(_mapping=sample_reaction_time_data[1])
        ]))
        
        mock_db_service._session.execute.return_value = mock_result
        mock_db_service._session.__enter__ = Mock(return_value=mock_db_service._session)
        mock_db_service._session.__exit__ = Mock(return_value=None)
        
        with patch.object(mock_db_service, 'get_db_session', return_value=mock_db_service._session):
            result = mock_db_service.get_reaction_time_data(
                team_id="LSU_TIGERS",
                date_from=datetime.now() - timedelta(days=7)
            )
        
        assert len(result) == 2
        mock_db_service._session.execute.assert_called_once()
    
    def test_get_s3_assessment_data(self, mock_db_service, mock_aws_clients):
        """Test getting assessment data from S3"""
        # Mock S3 response
        mock_aws_clients['s3'].get_object.return_value = {
            'Body': Mock(read=lambda: b'{"detailed_assessment": "test_data"}')
        }
        
        result = mock_db_service.get_s3_assessment_data("P001", "symptom_checklist")
        
        assert result == {"detailed_assessment": "test_data"}
        mock_aws_clients['s3'].get_object.assert_called_once_with(
            Bucket=mock_db_service.settings.aws_s3_bucket,
            Key="assessments/P001/symptom_checklist/latest.json"
        )
    
    def test_get_s3_assessment_data_error_handling(self, mock_db_service, mock_aws_clients):
        """Test S3 error handling"""
        # Mock S3 exception
        mock_aws_clients['s3'].get_object.side_effect = Exception("S3 Error")
        
        result = mock_db_service.get_s3_assessment_data("P001", "symptom_checklist")
        
        assert result == {}
    
    def test_calculate_symptom_metrics(self, mock_db_service, sample_symptom_data):
        """Test calculating symptom metrics"""
        # Prepare test data with known values
        test_data = [
            {'total_symptom_score': 35, 'headache_severity': 2, 'patient_id': 'P001'},
            {'total_symptom_score': 78, 'headache_severity': 4, 'patient_id': 'P001'},
            {'total_symptom_score': 15, 'headache_severity': 1, 'patient_id': 'P002'}
        ]
        
        result = mock_db_service.calculate_symptom_metrics(test_data)
        
        # Verify calculations
        expected_avg_total = (35 + 78 + 15) / 3  # 42.67
        expected_avg_headache = (2 + 4 + 1) / 3  # 2.33
        
        assert abs(result['avg_total_symptom_score'] - expected_avg_total) < 0.01
        assert abs(result['avg_headache_severity'] - expected_avg_headache) < 0.01
        assert result['max_total_symptom_score'] == 78
        assert result['patient_count'] == 2  # P001 and P002
        assert result['assessment_count'] == 3
    
    def test_calculate_symptom_metrics_empty_data(self, mock_db_service):
        """Test calculating metrics with empty data"""
        result = mock_db_service.calculate_symptom_metrics([])
        assert result == {}
    
    def test_calculate_reaction_time_metrics(self, mock_db_service):
        """Test calculating reaction time metrics"""
        # Prepare test data with known values
        test_data = [
            {
                'average_reaction_time': 245.5, 
                'accuracy_percentage': 94.0, 
                'patient_id': 'P001'
            },
            {
                'average_reaction_time': 298.7, 
                'accuracy_percentage': 84.0, 
                'patient_id': 'P001'
            },
            {
                'average_reaction_time': 234.2, 
                'accuracy_percentage': 96.0, 
                'patient_id': 'P002'
            }
        ]
        
        result = mock_db_service.calculate_reaction_time_metrics(test_data)
        
        # Verify calculations
        expected_avg_time = (245.5 + 298.7 + 234.2) / 3  # 259.47
        expected_avg_accuracy = (94.0 + 84.0 + 96.0) / 3  # 91.33
        
        assert abs(result['avg_reaction_time'] - expected_avg_time) < 0.01
        assert abs(result['avg_accuracy'] - expected_avg_accuracy) < 0.01
        assert abs(result['max_reaction_time'] - 298.7) < 0.01
        assert abs(result['min_reaction_time'] - 234.2) < 0.01
        assert result['patient_count'] == 2  # P001 and P002
        assert result['test_count'] == 3
    
    def test_calculate_reaction_time_metrics_empty_data(self, mock_db_service):
        """Test calculating reaction time metrics with empty data"""
        result = mock_db_service.calculate_reaction_time_metrics([])
        assert result == {}

class TestDatabaseServiceIntegration:
    """Integration tests for database service (require database setup)"""
    
    @pytest.mark.integration
    def test_database_connection(self, mock_settings):
        """Test actual database connection (integration test)"""
        # This would test actual database connectivity
        # Skip if no test database is available
        pytest.skip("Integration test - requires test database setup")
    
    @pytest.mark.integration 
    def test_real_s3_connection(self, mock_settings):
        """Test actual S3 connection (integration test)"""
        # This would test actual S3 connectivity
        # Skip if no test AWS environment is available
        pytest.skip("Integration test - requires test AWS environment")

class TestDatabaseServiceErrorHandling:
    """Test error handling in database service"""
    
    def test_database_connection_error(self, mock_settings):
        """Test handling of database connection errors"""
        with patch('backend.services.database_service.create_engine') as mock_engine:
            mock_engine.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception, match="Database connection failed"):
                DatabaseService()
    
    def test_query_execution_error(self, mock_db_service):
        """Test handling of query execution errors"""
        mock_db_service._session.execute.side_effect = Exception("Query failed")
        mock_db_service._session.__enter__ = Mock(return_value=mock_db_service._session)
        mock_db_service._session.__exit__ = Mock(return_value=None)
        
        with patch.object(mock_db_service, 'get_db_session', return_value=mock_db_service._session):
            with pytest.raises(Exception, match="Query failed"):
                mock_db_service.get_patients_by_team("INVALID_TEAM")

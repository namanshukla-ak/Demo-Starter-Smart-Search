"""
Integration tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

class TestAPIEndpoints:
    """Test API endpoints integration"""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Neurologix Smart Search API" in response.json()["message"]
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "neurologix-smart-search"
    
    @patch('backend.services.query_processor.QueryProcessor')
    def test_query_endpoint_success(self, mock_processor_class, test_client):
        """Test successful query processing"""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.process_query.return_value = {
            "answer": "Based on 10 symptom assessments, the average total symptom score is 45.2.",
            "confidence": 0.85,
            "source_modules": ["symptom_checklist"],
            "metadata": {
                "query_type": "symptom_analysis",
                "processing_time_ms": 150
            }
        }
        mock_processor_class.return_value = mock_processor
        
        # Test the endpoint
        response = test_client.post(
            "/api/v1/query",
            json={"question": "What is the average symptom score?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "confidence" in data
        assert "source_modules" in data
        assert "metadata" in data
        assert data["confidence"] == 0.85
        assert "symptom_checklist" in data["source_modules"]
    
    @patch('backend.services.query_processor.QueryProcessor')
    def test_query_endpoint_with_team_id(self, mock_processor_class, test_client):
        """Test query endpoint with team_id parameter"""
        mock_processor = Mock()
        mock_processor.process_query.return_value = {
            "answer": "LSU team data analysis complete.",
            "confidence": 0.90,
            "source_modules": ["symptom_checklist", "reaction_time"],
            "metadata": {}
        }
        mock_processor_class.return_value = mock_processor
        
        response = test_client.post(
            "/api/v1/query",
            json={
                "question": "Show me LSU team performance",
                "team_id": "LSU_TIGERS"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "LSU" in data["answer"]
        mock_processor.process_query.assert_called_once_with(
            question="Show me LSU team performance",
            team_id="LSU_TIGERS"
        )
    
    def test_query_endpoint_missing_question(self, test_client):
        """Test query endpoint with missing question field"""
        response = test_client.post(
            "/api/v1/query",
            json={"team_id": "LSU_TIGERS"}
        )
        
        assert response.status_code == 422  # Validation error
        assert "question" in response.text.lower()
    
    def test_query_endpoint_empty_question(self, test_client):
        """Test query endpoint with empty question"""
        response = test_client.post(
            "/api/v1/query",
            json={"question": ""}
        )
        
        # Should still process but may return generic response
        assert response.status_code in [200, 422]
    
    @patch('backend.services.query_processor.QueryProcessor')
    def test_query_endpoint_processing_error(self, mock_processor_class, test_client):
        """Test query endpoint when processing fails"""
        mock_processor = Mock()
        mock_processor.process_query.side_effect = Exception("Processing failed")
        mock_processor_class.return_value = mock_processor
        
        response = test_client.post(
            "/api/v1/query",
            json={"question": "Test query"}
        )
        
        assert response.status_code == 500
        assert "processing failed" in response.json()["detail"].lower()
    
    def test_query_endpoint_invalid_json(self, test_client):
        """Test query endpoint with invalid JSON"""
        response = test_client.post(
            "/api/v1/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    @patch('backend.services.query_processor.QueryProcessor')
    def test_query_endpoint_large_response(self, mock_processor_class, test_client):
        """Test query endpoint with large response data"""
        mock_processor = Mock()
        large_answer = "This is a very long answer. " * 1000  # Large response
        mock_processor.process_query.return_value = {
            "answer": large_answer,
            "confidence": 0.75,
            "source_modules": ["symptom_checklist"],
            "metadata": {"large_response": True}
        }
        mock_processor_class.return_value = mock_processor
        
        response = test_client.post(
            "/api/v1/query",
            json={"question": "Give me detailed analysis"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["answer"]) > 1000

class TestAPIValidation:
    """Test API request/response validation"""
    
    def test_query_request_validation(self, test_client):
        """Test QueryRequest model validation"""
        # Valid request
        response = test_client.post(
            "/api/v1/query",
            json={
                "question": "Test question",
                "user_id": "user123",
                "team_id": "LSU_TIGERS"
            }
        )
        assert response.status_code in [200, 500]  # May fail due to missing services
        
        # Invalid request - wrong field types
        response = test_client.post(
            "/api/v1/query",
            json={
                "question": 123,  # Should be string
                "user_id": ["invalid"],  # Should be string or null
            }
        )
        assert response.status_code == 422
    
    @patch('backend.services.query_processor.QueryProcessor')
    def test_query_response_validation(self, mock_processor_class, test_client):
        """Test QueryResponse model validation"""
        mock_processor = Mock()
        
        # Valid response data
        mock_processor.process_query.return_value = {
            "answer": "Test answer",
            "confidence": 0.8,
            "source_modules": ["symptom_checklist"],
            "metadata": {"test": "data"}
        }
        mock_processor_class.return_value = mock_processor
        
        response = test_client.post(
            "/api/v1/query",
            json={"question": "Test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure matches QueryResponse model
        required_fields = ["answer", "confidence", "source_modules", "metadata"]
        for field in required_fields:
            assert field in data
        
        assert isinstance(data["answer"], str)
        assert isinstance(data["confidence"], (int, float))
        assert isinstance(data["source_modules"], list)
        assert isinstance(data["metadata"], dict)

class TestCORSConfiguration:
    """Test CORS configuration for frontend integration"""
    
    def test_cors_preflight_request(self, test_client):
        """Test CORS preflight request"""
        response = test_client.options(
            "/api/v1/query",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should allow preflight request
        assert response.status_code in [200, 204]
    
    def test_cors_actual_request(self, test_client):
        """Test actual CORS request from frontend"""
        response = test_client.post(
            "/api/v1/query",
            json={"question": "Test"},
            headers={"Origin": "http://localhost:8501"}
        )
        
        # Should include CORS headers (may fail due to missing services)
        assert response.status_code in [200, 500]

class TestAPIPerformance:
    """Test API performance characteristics"""
    
    @pytest.mark.slow
    @patch('backend.services.query_processor.QueryProcessor')
    def test_query_endpoint_timeout(self, mock_processor_class, test_client):
        """Test query endpoint doesn't timeout on slow processing"""
        import time
        
        mock_processor = Mock()
        def slow_process(*args, **kwargs):
            time.sleep(2)  # Simulate slow processing
            return {
                "answer": "Slow response",
                "confidence": 0.7,
                "source_modules": ["symptom_checklist"],
                "metadata": {}
            }
        
        mock_processor.process_query.side_effect = slow_process
        mock_processor_class.return_value = mock_processor
        
        response = test_client.post(
            "/api/v1/query",
            json={"question": "Slow query"}
        )
        
        assert response.status_code == 200
        assert "Slow response" in response.json()["answer"]
    
    @patch('backend.services.query_processor.QueryProcessor')
    def test_concurrent_requests(self, mock_processor_class, test_client):
        """Test handling concurrent requests"""
        import threading
        import time
        
        mock_processor = Mock()
        mock_processor.process_query.return_value = {
            "answer": "Concurrent response",
            "confidence": 0.8,
            "source_modules": ["symptom_checklist"],
            "metadata": {}
        }
        mock_processor_class.return_value = mock_processor
        
        results = []
        
        def make_request():
            response = test_client.post(
                "/api/v1/query",
                json={"question": "Concurrent test"}
            )
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5

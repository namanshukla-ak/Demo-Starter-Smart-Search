"""
End-to-end tests for Neurologix Smart Search POV
"""
import pytest
import requests
import time
from unittest.mock import patch

@pytest.mark.e2e
class TestEndToEndWorkflow:
    """End-to-end tests requiring full system setup"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Base URL for API testing"""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def frontend_url(self):
        """Base URL for frontend testing"""
        return "http://localhost:8501"
    
    def test_api_server_running(self, api_base_url):
        """Test that API server is running and accessible"""
        try:
            response = requests.get(f"{api_base_url}/health", timeout=10)
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running - skipping E2E tests")
    
    def test_frontend_server_running(self, frontend_url):
        """Test that frontend server is running and accessible"""
        try:
            response = requests.get(frontend_url, timeout=10)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend server not running - skipping E2E tests")
    
    def test_complete_query_workflow(self, api_base_url):
        """Test complete query processing workflow"""
        # Test symptom-related query
        query_data = {
            "question": "What is the average headache severity for LSU players?",
            "team_id": "LSU_TIGERS"
        }
        
        response = requests.post(
            f"{api_base_url}/api/v1/query",
            json=query_data,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        required_fields = ["answer", "confidence", "source_modules", "metadata"]
        for field in required_fields:
            assert field in data
        
        # Verify meaningful response
        assert len(data["answer"]) > 10
        assert 0 <= data["confidence"] <= 1
        assert isinstance(data["source_modules"], list)
    
    def test_multiple_query_types(self, api_base_url):
        """Test different types of queries"""
        test_queries = [
            {
                "question": "Show me players with high symptom scores",
                "expected_modules": ["symptom_checklist"]
            },
            {
                "question": "What are the reaction times for the team?",
                "expected_modules": ["reaction_time"]
            },
            {
                "question": "Give me an overall assessment summary",
                "expected_modules": ["symptom_checklist", "reaction_time"]
            }
        ]
        
        for query_test in test_queries:
            response = requests.post(
                f"{api_base_url}/api/v1/query",
                json={"question": query_test["question"]},
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that expected modules are involved
            for module in query_test["expected_modules"]:
                # Either in source_modules or answer should reference the module
                assert (module in data["source_modules"] or 
                       any(keyword in data["answer"].lower() 
                           for keyword in ["symptom", "reaction", "time"]))
    
    def test_error_handling_workflow(self, api_base_url):
        """Test error handling in complete workflow"""
        # Test with invalid query
        response = requests.post(
            f"{api_base_url}/api/v1/query",
            json={"question": ""},
            timeout=30
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422, 500]
        
        # Test with malformed JSON
        response = requests.post(
            f"{api_base_url}/api/v1/query",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        assert response.status_code == 422
    
    def test_performance_requirements(self, api_base_url):
        """Test that system meets performance requirements"""
        query_data = {
            "question": "What is the average symptom score for the team?"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{api_base_url}/api/v1/query",
            json=query_data,
            timeout=30
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 10.0  # Should respond within 10 seconds
        
        # Test metadata includes processing time
        data = response.json()
        if "metadata" in data and "processing_time_ms" in data["metadata"]:
            processing_time = data["metadata"]["processing_time_ms"]
            assert processing_time < 5000  # Should process within 5 seconds

@pytest.mark.e2e
@pytest.mark.slow
class TestDataIntegration:
    """Test integration with actual data sources"""
    
    def test_database_connectivity(self):
        """Test actual database connectivity"""
        # This would test real database connection
        # Skip if test database not available
        pytest.skip("Requires test database setup")
    
    def test_aws_s3_connectivity(self):
        """Test actual AWS S3 connectivity"""
        # This would test real S3 connection
        # Skip if test AWS environment not available
        pytest.skip("Requires test AWS environment setup")
    
    def test_data_consistency(self):
        """Test data consistency between MySQL and S3"""
        # This would verify data sync between sources
        # Skip if test environment not available
        pytest.skip("Requires test data environment")

@pytest.mark.e2e
class TestUserScenarios:
    """Test realistic user scenarios"""
    
    def test_doctor_workflow(self, api_base_url):
        """Test typical doctor workflow"""
        # Scenario: Doctor wants to check on specific player
        queries = [
            "Show me John Smith's latest assessment",
            "What are John Smith's symptom scores?",
            "How does John Smith's performance compare to baseline?"
        ]
        
        for question in queries:
            response = requests.post(
                f"{api_base_url}/api/v1/query",
                json={"question": question},
                timeout=30
            )
            
            # All queries should be processed successfully
            assert response.status_code == 200
            data = response.json()
            assert len(data["answer"]) > 10
    
    def test_trainer_workflow(self, api_base_url):
        """Test typical athletic trainer workflow"""
        # Scenario: Trainer wants team overview
        queries = [
            "Show me the team's overall health status",
            "Which players have concerning symptoms?",
            "What's the average reaction time for the team this week?"
        ]
        
        for question in queries:
            response = requests.post(
                f"{api_base_url}/api/v1/query",
                json={
                    "question": question,
                    "team_id": "LSU_TIGERS"
                },
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["answer"]) > 10
    
    def test_researcher_workflow(self, api_base_url):
        """Test typical researcher workflow"""
        # Scenario: Researcher wants statistical analysis
        queries = [
            "What's the average symptom severity across all players?",
            "How do baseline scores compare to post-injury scores?",
            "What percentage of players show cognitive decline?"
        ]
        
        for question in queries:
            response = requests.post(
                f"{api_base_url}/api/v1/query",
                json={"question": question},
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            # Researcher queries should have high confidence
            assert data["confidence"] >= 0.5

@pytest.mark.e2e
class TestSecurityAndAccess:
    """Test security and access control"""
    
    def test_team_data_isolation(self, api_base_url):
        """Test that team data is properly isolated"""
        # Query with specific team ID
        response1 = requests.post(
            f"{api_base_url}/api/v1/query",
            json={
                "question": "Show me team data",
                "team_id": "LSU_TIGERS"
            },
            timeout=30
        )
        
        response2 = requests.post(
            f"{api_base_url}/api/v1/query",
            json={
                "question": "Show me team data",
                "team_id": "DEMO_TEAM"
            },
            timeout=30
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Responses should be different (team isolation)
        data1 = response1.json()
        data2 = response2.json()
        
        # At minimum, they shouldn't be identical
        assert data1["answer"] != data2["answer"] or data1["metadata"] != data2["metadata"]
    
    def test_input_sanitization(self, api_base_url):
        """Test input sanitization and injection prevention"""
        malicious_queries = [
            "'; DROP TABLE patients; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "SELECT * FROM patients WHERE 1=1"
        ]
        
        for malicious_query in malicious_queries:
            response = requests.post(
                f"{api_base_url}/api/v1/query",
                json={"question": malicious_query},
                timeout=30
            )
            
            # Should handle malicious input gracefully
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                data = response.json()
                # Response should not contain raw SQL or dangerous content
                assert "DROP TABLE" not in data["answer"]
                assert "<script>" not in data["answer"]

@pytest.mark.e2e
@pytest.mark.slow
class TestLoadAndStress:
    """Test system under load"""
    
    def test_concurrent_users(self, api_base_url):
        """Test system with concurrent users"""
        import threading
        import time
        
        results = []
        
        def make_concurrent_request():
            try:
                response = requests.post(
                    f"{api_base_url}/api/v1/query",
                    json={"question": "What is the team average?"},
                    timeout=30
                )
                results.append({
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
            except Exception as e:
                results.append({"error": str(e)})
        
        # Simulate 10 concurrent users
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_concurrent_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful_requests = [r for r in results if "status_code" in r and r["status_code"] == 200]
        error_requests = [r for r in results if "error" in r]
        
        # At least 80% should succeed
        success_rate = len(successful_requests) / len(results)
        assert success_rate >= 0.8
        
        # Average response time should be reasonable
        if successful_requests:
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            assert avg_response_time < 15.0  # 15 seconds under load

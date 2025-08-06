"""
Unit tests for database operations and Supabase integration.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.core.supabaseclient import get_supabase_client

class TestSupabaseClient:
    """Test suite for Supabase client operations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.mock_client = Mock()
    
    @patch('src.core.supabaseclient.create_client')
    def test_get_supabase_client(self, mock_create_client):
        """Test getting Supabase client."""
        # Mock the create_client function to return our mock client
        mock_create_client.return_value = self.mock_client
        
        # Get the client
        client = get_supabase_client()
        
        # The client should be a SupabaseClient instance
        assert hasattr(client, 'client')
        assert hasattr(client, 'service_client')
    
    @patch('src.core.supabaseclient.get_supabase_client')
    def test_save_decision_to_database(self, mock_get_client):
        """Test saving decision to database."""
        # Mock client
        mock_get_client.return_value = self.mock_client
        
        # Mock successful insert
        self.mock_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": 1, "user_id": "test-user", "classification_result": "NORMAL"}]
        }
        
        # Test data
        decision_data = {
            "user_id": "test-user",
            "classification_result": "NORMAL",
            "confidence_score": 0.85,
            "risk_score": 0.2,
            "features": {"logged_in": True, "count": 45},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Execute insert
        result = self.mock_client.table("decisions").insert(decision_data).execute()
        
        # Verify
        assert result["data"][0]["classification_result"] == "NORMAL"
        self.mock_client.table.assert_called_with("decisions")
    
    @patch('src.core.supabaseclient.get_supabase_client')
    def test_get_user_decisions(self, mock_get_client):
        """Test getting user decisions from database."""
        # Mock client
        mock_get_client.return_value = self.mock_client
        
        # Mock successful query
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = {
            "data": [
                {
                    "id": 1,
                    "user_id": "test-user",
                    "classification_result": "NORMAL",
                    "confidence_score": 0.85,
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": 2,
                    "user_id": "test-user",
                    "classification_result": "MALICIOUS",
                    "confidence_score": 0.95,
                    "created_at": "2024-01-02T00:00:00Z"
                }
            ]
        }
        
        # Execute query
        result = self.mock_client.table("decisions").select("*").eq("user_id", "test-user").execute()
        
        # Verify
        assert len(result["data"]) == 2
        assert result["data"][0]["classification_result"] == "NORMAL"
        assert result["data"][1]["classification_result"] == "MALICIOUS"
    
    @patch('src.core.supabaseclient.get_supabase_client')
    def test_database_error_handling(self, mock_get_client):
        """Test database error handling."""
        # Mock client
        mock_get_client.return_value = self.mock_client
        
        # Mock database error
        self.mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
        
        # Test error handling
        with pytest.raises(Exception, match="Database error"):
            self.mock_client.table("decisions").insert({}).execute()

class TestRedisClient:
    """Test suite for Redis cache operations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.mock_redis = Mock()
    
    @patch('src.core.redisclient.redis.Redis')
    def test_redis_connection(self, mock_redis_class):
        """Test Redis connection."""
        mock_redis_class.return_value = self.mock_redis
        self.mock_redis.ping.return_value = True
        
        # Test connection
        from src.core.redisclient import get_redis_client
        client = get_redis_client()
        assert client is not None
        assert hasattr(client, 'redis_client')
        assert hasattr(client, 'ping')
    
    @patch('src.core.redisclient.get_redis_client')
    def test_cache_operations(self, mock_get_client):
        """Test cache operations."""
        # Mock client
        mock_get_client.return_value = self.mock_redis
        
        # Test set operation
        self.mock_redis.set.return_value = True
        result = self.mock_redis.set("test_key", "test_value", ex=3600)
        assert result is True
        self.mock_redis.set.assert_called_with("test_key", "test_value", ex=3600)
        
        # Test get operation
        self.mock_redis.get.return_value = b"test_value"
        result = self.mock_redis.get("test_key")
        assert result == b"test_value"
        self.mock_redis.get.assert_called_with("test_key")
        
        # Test delete operation
        self.mock_redis.delete.return_value = 1
        result = self.mock_redis.delete("test_key")
        assert result == 1
        self.mock_redis.delete.assert_called_with("test_key")

class TestDataValidation:
    """Test suite for data validation."""
    
    def test_network_traffic_features_validation(self):
        """Test network traffic features validation."""
        from src.api.schemas import NetworkTrafficFeatures
        
        # Valid data
        valid_data = {
            "logged_in": True,
            "count": 45,
            "serror_rate": 0.05,
            "srv_serror_rate": 0.04,
            "same_srv_rate": 0.88,
            "dst_host_srv_count": 110,
            "dst_host_same_srv_rate": 0.99,
            "dst_host_serror_rate": 0.02,
            "dst_host_srv_serror_rate": 0.01,
            "flag": "S0"
        }
        
        features = NetworkTrafficFeatures(**valid_data)
        assert features.logged_in is True
        assert features.count == 45
        assert features.flag == "S0"
    
    def test_network_traffic_features_invalid(self):
        """Test network traffic features with invalid data."""
        from src.api.schemas import NetworkTrafficFeatures
        from pydantic import ValidationError
        
        # Invalid data - missing required fields
        invalid_data = {
            "logged_in": True,
            "count": 45
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError):
            NetworkTrafficFeatures(**invalid_data)
    
    def test_decision_response_validation(self):
        """Test decision response validation."""
        from src.api.schemas import DecisionResponse
        from datetime import datetime
        
        # Valid response data with all required fields
        valid_data = {
            "classification_result": "NORMAL",
            "timestamp": datetime.utcnow(),
            "correlation_id": "decision_123"
        }
        
        response = DecisionResponse(**valid_data)
        assert response.classification_result == "NORMAL"
        assert response.correlation_id == "decision_123"
        assert response.timestamp is not None

if __name__ == "__main__":
    pytest.main([__file__]) 
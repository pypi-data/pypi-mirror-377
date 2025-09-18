#!/usr/bin/env python3
"""
Comprehensive End-to-End tests for sellm - Fixed to match actual implementation
Tests all core functionality including API, configuration, and LLM integration.
"""

import asyncio
import json
import yaml
import pytest
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from aiohttp import ClientSession, web
from aiohttp.test_utils import AioHTTPTestCase
import sys

# Add sellm to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from sellm import Config, ManifestGenerator, APIServer, LLMClient


class TestSellmConfiguration:
    """Test sellm configuration management"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        assert config.llm_model == "mistral:7b"
        assert config.llm_host == "localhost:11434"
        assert config.api_port == 8080
        assert config.enable_cache is True
    
    def test_config_from_env(self):
        """Test configuration loading from environment variables"""
        with patch.dict(os.environ, {
            'SELLM_MODEL': 'llama2:7b',
            'SELLM_HOST': 'localhost:11435',
            'API_PORT': '9000'
        }):
            config = Config.from_env()
            assert config.llm_model == "llama2:7b"
            assert config.llm_host == "localhost:11435"
            assert config.api_port == 9000


class TestManifestGenerator:
    """Test manifest generation functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = Config(enable_cache=False)  # Disable cache for tests
        self.generator = ManifestGenerator(self.config)
    
    @pytest.mark.asyncio
    async def test_manifest_generation_mock(self):
        """Test manifest generation with mocked LLM response"""
        description = "Create a simple REST API for user management"
        
        # Mock LLM response - should return a YAML string that would be extracted
        mock_yaml_response = '''```yaml
name: user-management-api
description: Simple REST API for user management
version: 1.0.0
type: http
port: 8080
endpoints:
  - path: /users
    method: GET
    handler: handlers/users.py:list_users
  - path: /users
    method: POST
    handler: handlers/users.py:create_user
```'''
        
        with patch.object(self.generator.llm, 'generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_yaml_response
            
            result = await self.generator.generate(description)
            
            assert isinstance(result, dict)
            assert result['name'] == "user-management-api"
            assert result['type'] == "http"
            assert result['port'] == 8080
            mock_llm.assert_called_once()
    
    def test_validate_manifest_valid(self):
        """Test manifest validation with valid manifest"""
        valid_manifest = {
            "name": "test-service",
            "description": "Test service",
            "version": "1.0.0",
            "type": "http",
            "port": 8080
        }
        
        is_valid, errors = self.generator._validate_manifest(valid_manifest)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_manifest_invalid(self):
        """Test manifest validation with invalid manifest"""
        invalid_manifest = {
            "description": "Missing required fields"
            # Missing: name, version, type, port
        }
        
        is_valid, errors = self.generator._validate_manifest(invalid_manifest)
        assert is_valid is False
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)
    
    def test_service_type_detection(self):
        """Test automatic service type detection"""
        # Test different descriptions and expected types
        test_cases = [
            ("GPIO sensor monitoring", "hardware"),
            ("Real-time chat application", "websocket"),
            ("Docker microservice API", "microservice"),
            ("IoT MQTT telemetry", "iot"),
            ("Standard REST API", "http")
        ]
        
        for description, expected_type in test_cases:
            detected_type = self.generator._detect_service_type(description)
            assert detected_type == expected_type
    
    def test_extract_manifest_yaml(self):
        """Test YAML extraction from LLM response"""
        yaml_response = '''Here's your manifest:

```yaml
name: test-service
version: 1.0.0
type: http
port: 8080
```

This should work perfectly!'''
        
        manifest = self.generator._extract_manifest(yaml_response)
        assert manifest['name'] == "test-service"
        assert manifest['version'] == "1.0.0"
        assert manifest['type'] == "http"
        assert manifest['port'] == 8080


class TestAPIServer(AioHTTPTestCase):
    """Test API server functionality"""
    
    async def get_application(self):
        """Create test application"""
        self.config = Config(enable_cache=False)
        self.generator = ManifestGenerator(self.config)
        self.server = APIServer(self.generator, self.config)
        return self.server.app
    
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        resp = await self.client.request("GET", "/health")
        assert resp.status == 200
        
        data = await resp.json()
        assert data['status'] == 'healthy'
        assert data['version'] == '1.0.0'
        assert 'model' in data
    
    async def test_generate_endpoint_missing_description(self):
        """Test generate endpoint with missing description"""
        resp = await self.client.request("POST", "/generate", json={})
        assert resp.status == 400
        
        data = await resp.json()
        assert 'error' in data
    
    async def test_generate_endpoint_with_description(self):
        """Test generate endpoint with valid description"""
        # Mock the LLM call
        mock_manifest = {
            "name": "test-api",
            "description": "Generated API",
            "version": "1.0.0",
            "type": "http",
            "port": 8080
        }
        
        with patch.object(self.generator, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_manifest
            
            resp = await self.client.request("POST", "/generate", json={
                "description": "Create a simple API"
            })
            
            assert resp.status == 200
            data = await resp.json()
            assert data['manifest']['name'] == "test-api"
            mock_gen.assert_called_once()
    
    async def test_validate_endpoint_valid_manifest(self):
        """Test validate endpoint with valid manifest"""
        valid_manifest = {
            "name": "test-service",
            "description": "Test service",
            "version": "1.0.0",
            "type": "http",
            "port": 8080
        }
        
        resp = await self.client.request("POST", "/validate", json={
            "manifest": valid_manifest
        })
        
        assert resp.status == 200
        data = await resp.json()
        assert data['is_valid'] is True
        assert data['errors'] == []
    
    async def test_validate_endpoint_invalid_manifest(self):
        """Test validate endpoint with invalid manifest"""
        invalid_manifest = {
            "description": "Missing required fields"
        }
        
        resp = await self.client.request("POST", "/validate", json={
            "manifest": invalid_manifest
        })
        
        assert resp.status == 200
        data = await resp.json()
        assert data['is_valid'] is False
        assert len(data['errors']) > 0
    
    async def test_models_endpoint(self):
        """Test models listing endpoint"""
        resp = await self.client.request("GET", "/models")
        assert resp.status == 200
        
        data = await resp.json()
        assert 'models' in data
        assert isinstance(data['models'], list)


class TestIntegration:
    """Integration tests for sellm components"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = Config(enable_cache=False)
    
    @pytest.mark.asyncio
    async def test_full_workflow_mock(self):
        """Test complete workflow from description to validated manifest"""
        generator = ManifestGenerator(self.config)
        
        # Mock LLM response
        mock_yaml_response = '''```yaml
name: integration-test-api
description: API created during integration test
version: 1.0.0
type: http
port: 8080
endpoints:
  - path: /test
    method: GET
    handler: handlers/test.py:test_handler
```'''
        
        with patch.object(generator.llm, 'generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_yaml_response
            
            # Generate manifest
            result = await generator.generate("Create test API")
            assert result['name'] == "integration-test-api"
            
            # Validate generated manifest
            is_valid, errors = generator._validate_manifest(result)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_yaml_json_compatibility(self):
        """Test YAML and JSON compatibility for manifests"""
        manifest = {
            "name": "compatibility-test",
            "description": "Test YAML/JSON compatibility",
            "version": "1.0.0",
            "type": "http",
            "port": 8080,
            "endpoints": [
                {
                    "path": "/api/v1/test",
                    "method": "POST",
                    "handler": "handlers/test.py:test_handler"
                }
            ]
        }
        
        # Convert to YAML and back
        yaml_str = yaml.dump(manifest)
        yaml_parsed = yaml.safe_load(yaml_str)
        assert yaml_parsed == manifest
        
        # Convert to JSON and back
        json_str = json.dumps(manifest)
        json_parsed = json.loads(json_str)
        assert json_parsed == manifest


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = Config(enable_cache=False)
        self.generator = ManifestGenerator(self.config)
    
    @pytest.mark.asyncio
    async def test_llm_connection_error(self):
        """Test handling of LLM connection errors"""
        with patch.object(self.generator.llm, 'generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception) as exc_info:
                await self.generator.generate("test description")
            
            assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_llm_response(self):
        """Test handling of invalid LLM responses - should return fallback manifest"""
        with patch.object(self.generator.llm, 'generate', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "invalid yaml: {[}]"
            
            # Should not raise exception, but return fallback manifest
            result = await self.generator.generate("test description")
            assert isinstance(result, dict)
            assert result['name'] == "generated-service"  # fallback manifest
    
    def test_empty_description_handling(self):
        """Test validation of empty descriptions"""
        # Test various empty descriptions
        empty_descriptions = ["", "   ", "\n\t"]
        
        for description in empty_descriptions:
            # This should be handled gracefully by the service type detector
            service_type = self.generator._detect_service_type(description)
            assert service_type == "http"  # default fallback


class TestPerformance:
    """Performance and reliability tests"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = Config(enable_cache=False)
    
    def test_concurrent_validation(self):
        """Test concurrent manifest validation"""
        generator = ManifestGenerator(self.config)
        
        manifest = {
            "name": "concurrent-test",
            "description": "Concurrent validation test",
            "version": "1.0.0",
            "type": "http",
            "port": 8080
        }
        
        # Run multiple validations concurrently
        import threading
        results = []
        errors = []
        
        def validate_manifest():
            try:
                is_valid, validation_errors = generator._validate_manifest(manifest)
                results.append(is_valid)
                errors.extend(validation_errors)
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=validate_manifest)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All validations should succeed
        assert len(results) == 10
        assert all(results)
        assert len(errors) == 0
    
    def test_name_sanitization(self):
        """Test automatic name sanitization in validation"""
        generator = ManifestGenerator(self.config)
        
        manifest = {
            "name": "test service with spaces",
            "version": "1.0.0",
            "type": "http",
            "port": 8080
        }
        
        is_valid, errors = generator._validate_manifest(manifest)
        assert is_valid is True
        assert manifest['name'] == "test-service-with-spaces"  # Spaces should be replaced with hyphens


class TestLLMClient:
    """Test LLM client functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = LLMClient("localhost:11434", "mistral:7b")
    
    def test_llm_client_initialization(self):
        """Test LLM client initialization"""
        assert self.client.base_url == "http://localhost:11434"
        assert self.client.model == "mistral:7b"
    
    @pytest.mark.asyncio
    async def test_llm_generate_mock(self):
        """Test LLM generate with mocked response"""
        mock_response = {"response": "Generated text"}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value = mock_resp
            
            result = await self.client.generate("test prompt")
            assert result == "Generated text"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

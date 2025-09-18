"""
Test cases for Flask API endpoints
"""

import pytest
import json
import io
from unittest.mock import patch, Mock


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health endpoint returns success"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


class TestAuthenticationMiddleware:
    """Test API authentication"""

    def test_upload_requires_auth(self, client, sample_sbom):
        """Test SBOM upload requires authentication"""
        with open(sample_sbom, "rb") as f:
            response = client.post(
                "/api/v1/sbom/upload",
                data={
                    "district": "Test District",
                    "business_line": "Test Business Line",
                    "project_name": "test-project",
                    "version": "1.0.0",
                    "sbom": (f, "test.json"),
                },
            )
        assert response.status_code == 401

    def test_invalid_api_key(self, client, sample_sbom):
        """Test invalid API key returns 401"""
        with open(sample_sbom, "rb") as f:
            response = client.post(
                "/api/v1/sbom/upload",
                headers={"X-API-Key": "invalid-key"},
                data={
                    "district": "Test District",
                    "business_line": "Test Business Line",
                    "project_name": "test-project",
                    "version": "1.0.0",
                    "sbom": (f, "test.json"),
                },
            )
        assert response.status_code == 401

    def test_valid_api_key(self, client, sample_sbom, auth_headers, mock_dt_api):
        """Test valid API key allows access"""
        with open(sample_sbom, "rb") as f:
            response = client.post(
                "/api/v1/sbom/upload",
                headers=auth_headers,
                data={
                    "district": "Test District",
                    "business_line": "Test Business Line",
                    "project_name": "test-project",
                    "version": "1.0.0",
                    "sbom": (f, "test.json"),
                },
            )
        assert response.status_code == 200


class TestSBOMUpload:
    """Test SBOM upload functionality"""

    def test_missing_required_fields(self, client, auth_headers):
        """Test upload fails with missing required fields"""
        response = client.post(
            "/api/v1/sbom/upload", headers=auth_headers, data={"district": "Test District"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_missing_sbom_file(self, client, auth_headers):
        """Test upload fails with missing SBOM file"""
        response = client.post(
            "/api/v1/sbom/upload",
            headers=auth_headers,
            data={
                "district": "Test District",
                "business_line": "Test Business Line",
                "project_name": "test-project",
                "version": "1.0.0",
            },
        )
        assert response.status_code == 400

    def test_successful_upload(
        self, client, sample_sbom, sample_upload_data, auth_headers, mock_dt_api
    ):
        """Test successful SBOM upload"""
        with open(sample_sbom, "rb") as f:
            data = sample_upload_data.copy()
            data["sbom"] = (f, "test.json")

            response = client.post("/api/v1/sbom/upload", headers=auth_headers, data=data)

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["status"] == "success"
        assert "hierarchy" in response_data
        assert "upload_result" in response_data

    @patch("dt_api_utils.DependencyTrackAPI")
    def test_dt_api_error_handling(
        self, mock_dt_class, client, sample_sbom, sample_upload_data, auth_headers
    ):
        """Test handling of Dependency-Track API errors"""
        # Mock API to raise an exception
        mock_api = Mock()
        mock_dt_class.return_value = mock_api
        mock_api.get_projects.side_effect = Exception("API connection failed")

        with open(sample_sbom, "rb") as f:
            data = sample_upload_data.copy()
            data["sbom"] = (f, "test.json")

            response = client.post("/api/v1/sbom/upload", headers=auth_headers, data=data)

        assert response.status_code == 500
        response_data = response.get_json()
        assert "error" in response_data


class TestProjectHierarchy:
    """Test project hierarchy endpoints"""

    def test_hierarchy_requires_auth(self, client):
        """Test hierarchy endpoint requires authentication"""
        response = client.get("/api/v1/projects/hierarchy")
        assert response.status_code == 401

    def test_get_hierarchy(self, client, auth_headers, mock_dt_api):
        """Test getting project hierarchy"""
        mock_dt_api.get_projects.return_value = [
            {"uuid": "district-uuid", "name": "Test District", "tags": [{"name": "type:district"}]}
        ]

        response = client.get("/api/v1/projects/hierarchy", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "hierarchy" in data

    def test_get_project_versions(self, client, auth_headers, mock_dt_api):
        """Test getting project versions"""
        mock_dt_api.get_projects.return_value = [
            {"uuid": "project-uuid", "name": "test-project", "version": "1.0.0"}
        ]

        response = client.get(
            "/api/v1/projects/test-project/versions",
            headers=auth_headers,
            query_string={"district": "Test District", "business_line": "Test Business Line"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "versions" in data


class TestAPIValidation:
    """Test API key validation endpoints"""

    def test_validate_key_requires_auth(self, client):
        """Test key validation requires authentication"""
        response = client.get("/api/v1/keys/validate")
        assert response.status_code == 401

    def test_validate_key_success(self, client, auth_headers):
        """Test successful key validation"""
        response = client.get("/api/v1/keys/validate", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["valid"] is True
        assert "key_info" in data

    def test_list_keys_admin_only(self, client, auth_headers):
        """Test list keys requires admin access"""
        response = client.get("/api/v1/keys/list", headers=auth_headers)
        # Should fail since test key is not admin
        assert response.status_code == 403

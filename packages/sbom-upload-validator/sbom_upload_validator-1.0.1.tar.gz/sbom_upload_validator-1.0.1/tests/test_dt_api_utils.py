"""
Test cases for Dependency-Track API utilities
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from dt_api_utils import DependencyTrackAPI, ProjectHierarchyManager


class TestDependencyTrackAPI:
    """Test DependencyTrackAPI class"""

    @pytest.fixture
    def api(self):
        """Create API instance for testing"""
        with patch("requests.Session") as mock_session:
            api = DependencyTrackAPI("http://localhost:8080", "test-api-key")
            api.session = mock_session.return_value
            yield api

    def test_initialization(self):
        """Test API initialization"""
        api = DependencyTrackAPI("http://localhost:8080", "test-api-key")
        assert api.base_url == "http://localhost:8080"
        assert api.api_key == "test-api-key"
        assert api.session.headers["X-Api-Key"] == "test-api-key"

    def test_get_projects_success(self, api):
        """Test successful project retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"uuid": "test-uuid", "name": "test-project"}]
        api.session.get.return_value = mock_response

        projects = api.get_projects()
        assert len(projects) == 1
        assert projects[0]["name"] == "test-project"

    def test_get_projects_error(self, api):
        """Test project retrieval error handling"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        api.session.get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            api.get_projects()

    def test_create_project_success(self, api):
        """Test successful project creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"uuid": "new-project-uuid", "name": "new-project"}
        api.session.put.return_value = mock_response

        project = api.create_project("new-project", "1.0.0")
        assert project["name"] == "new-project"
        api.session.put.assert_called_once()

    def test_upload_bom_success(self, api):
        """Test successful BOM upload"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "upload-token"}
        api.session.post.return_value = mock_response

        result = api.upload_bom("project-uuid", "bom-content")
        assert result["token"] == "upload-token"

    def test_clone_project_success(self, api):
        """Test successful project cloning"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"uuid": "cloned-project-uuid", "name": "cloned-project"}
        api.session.put.return_value = mock_response

        result = api.clone_project("source-uuid", "2.0.0")
        assert result["name"] == "cloned-project"


class TestProjectHierarchyManager:
    """Test ProjectHierarchyManager class"""

    @pytest.fixture
    def mock_api(self):
        """Mock DependencyTrackAPI for testing"""
        return Mock(spec=DependencyTrackAPI)

    @pytest.fixture
    def manager(self, mock_api):
        """Create hierarchy manager for testing"""
        return ProjectHierarchyManager(mock_api)

    def test_initialization(self, mock_api):
        """Test manager initialization"""
        manager = ProjectHierarchyManager(mock_api)
        assert manager.api == mock_api

    def test_find_or_create_district_existing(self, manager, mock_api):
        """Test finding existing district"""
        mock_api.get_projects.return_value = [
            {"uuid": "district-uuid", "name": "Test District", "tags": [{"name": "type:district"}]}
        ]

        district = manager.find_or_create_district("Test District")
        assert district["name"] == "Test District"
        assert district["uuid"] == "district-uuid"

    def test_find_or_create_district_new(self, manager, mock_api):
        """Test creating new district"""
        mock_api.get_projects.return_value = []
        mock_api.create_project.return_value = {"uuid": "new-district-uuid", "name": "New District"}

        district = manager.find_or_create_district("New District")
        assert district["name"] == "New District"
        mock_api.create_project.assert_called_once()

    def test_ensure_hierarchy_complete_flow(self, manager, mock_api):
        """Test complete hierarchy creation flow"""
        # Mock empty project list initially
        mock_api.get_projects.return_value = []

        # Mock project creation responses
        district_response = {"uuid": "district-uuid", "name": "Test District"}
        bl_response = {"uuid": "bl-uuid", "name": "Test Business Line"}
        project_response = {"uuid": "project-uuid", "name": "test-project", "version": "1.0.0"}

        mock_api.create_project.side_effect = [district_response, bl_response, project_response]

        hierarchy = manager.ensure_hierarchy(
            "Test District", "Test Business Line", "test-project", "1.0.0"
        )

        assert hierarchy["district"]["name"] == "Test District"
        assert hierarchy["business_line"]["name"] == "Test Business Line"
        assert hierarchy["project"]["name"] == "test-project"
        assert mock_api.create_project.call_count == 3

    def test_get_latest_version_sorts_correctly(self, manager, mock_api):
        """Test version sorting for latest version detection"""
        mock_api.get_projects.return_value = [
            {"version": "1.0.0", "uuid": "v1"},
            {"version": "1.2.0", "uuid": "v12"},
            {"version": "1.10.0", "uuid": "v110"},
            {"version": "2.0.0", "uuid": "v2"},
        ]

        latest = manager.get_latest_project_version(
            "Test District", "Test Business Line", "test-project"
        )

        # Should return the project with highest version
        assert latest["version"] == "2.0.0"

    def test_metadata_generation(self, manager):
        """Test project metadata generation"""
        metadata = manager._generate_project_metadata(
            district="Test District",
            business_line="Test Business Line",
            project_name="test-project",
            version="1.0.0",
            gitlab_project_id="123",
            commit_sha="abc123",
        )

        assert "Test District" in metadata["description"]
        assert "Test Business Line" in metadata["description"]
        assert len(metadata["tags"]) > 0
        assert any("district:Test District" in tag["name"] for tag in metadata["tags"])

    def test_project_cloning_with_metadata(self, manager, mock_api):
        """Test project cloning preserves metadata"""
        source_project = {"uuid": "source-uuid", "name": "test-project", "version": "1.0.0"}

        mock_api.clone_project.return_value = {
            "uuid": "cloned-uuid",
            "name": "test-project",
            "version": "2.0.0",
        }

        result = manager.clone_project_version(
            source_project,
            "2.0.0",
            district="Test District",
            business_line="Test Business Line",
            gitlab_project_id="123",
        )

        assert result["version"] == "2.0.0"
        mock_api.clone_project.assert_called_once()
        mock_api.update_project.assert_called_once()


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    @pytest.fixture
    def full_setup(self):
        """Full setup with mocked API and manager"""
        with patch("requests.Session"):
            api = DependencyTrackAPI("http://localhost:8080", "test-key")
            api.session = Mock()
            manager = ProjectHierarchyManager(api)
            return api, manager

    def test_new_project_first_upload(self, full_setup):
        """Test first upload for a completely new project"""
        api, manager = full_setup

        # Mock empty project list
        api.get_projects.return_value = []

        # Mock successful project creation
        api.create_project.side_effect = [
            {"uuid": "d-uuid", "name": "District"},
            {"uuid": "bl-uuid", "name": "BusinessLine"},
            {"uuid": "p-uuid", "name": "project", "version": "1.0.0"},
        ]

        api.upload_bom.return_value = {"token": "upload-token"}

        hierarchy = manager.ensure_hierarchy("District", "BusinessLine", "project", "1.0.0")
        upload_result = api.upload_bom(hierarchy["project"]["uuid"], "bom-content")

        assert hierarchy["project"]["version"] == "1.0.0"
        assert upload_result["token"] == "upload-token"
        assert api.create_project.call_count == 3

    def test_existing_project_new_version(self, full_setup):
        """Test upload for existing project with new version"""
        api, manager = full_setup

        # Mock existing hierarchy
        api.get_projects.return_value = [
            {"uuid": "d-uuid", "name": "District", "tags": [{"name": "type:district"}]},
            {"uuid": "bl-uuid", "name": "BusinessLine", "tags": [{"name": "type:business_line"}]},
            {
                "uuid": "p1-uuid",
                "name": "project",
                "version": "1.0.0",
                "tags": [{"name": "type:project"}],
            },
        ]

        # Mock cloning
        api.clone_project.return_value = {"uuid": "p2-uuid", "name": "project", "version": "2.0.0"}

        api.upload_bom.return_value = {"token": "upload-token-v2"}

        hierarchy = manager.ensure_hierarchy("District", "BusinessLine", "project", "2.0.0")

        assert hierarchy["project"]["version"] == "2.0.0"
        assert hierarchy["project"]["uuid"] == "p2-uuid"
        api.clone_project.assert_called_once()

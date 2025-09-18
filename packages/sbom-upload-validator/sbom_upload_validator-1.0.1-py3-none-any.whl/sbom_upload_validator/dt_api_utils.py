import os

# import json
# import uuid
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests


class DependencyTrackAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": api_key, "Accept": "application/json"})

    def _make_request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error: {e}")
            raise
        except requests.exceptions.Timeout as e:
            print(f"Timeout Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise

    def get_projects(self):
        """
        Retrieves a list of all projects.
        Corresponds to GET /api/v1/project
        """
        print("Fetching all projects...")
        return self._make_request("GET", "/api/v1/project")

    def upload_sbom(
        self,
        project_uuid,
        sbom_file_path,
        auto_create=False,
        project_name=None,
        project_version=None,
    ):
        """
        Uploads a BOM file for a specific project.
        Corresponds to POST /api/v1/bom (multipart/form-data)
        """
        print(f"Uploading SBOM for project UUID: {project_uuid} from {sbom_file_path}...")
        if not os.path.exists(sbom_file_path):
            raise FileNotFoundError(f"SBOM file not found: {sbom_file_path}")

        files = {
            "bom": (
                os.path.basename(sbom_file_path),
                open(sbom_file_path, "rb"),
                "application/xml" if sbom_file_path.endswith(".xml") else "application/json",
            )
        }

        data = {
            "project": project_uuid,
            "autoCreate": str(auto_create).lower(),  # Convert boolean to string 'true' or 'false'
        }
        if project_name:
            data["projectName"] = project_name
        if project_version:
            data["projectVersion"] = project_version

        # Dependency-Track expects 'project' and 'autoCreate' as form fields, not part of the file payload
        # The 'bom' field is the file itself.
        # requests handles multipart/form-data correctly when 'files' and 'data' are used.

        try:
            response = self.session.post(f"{self.base_url}/api/v1/bom", files=files, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error during SBOM upload: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during SBOM upload: {e}")
            raise
        finally:
            # Ensure the file is closed
            if "bom" in files and files["bom"][1]:
                files["bom"][1].close()

    def get_project_findings(self, project_uuid):
        """
        Retrieves vulnerability findings for a specific project.
        Corresponds to GET /api/v1/finding/project/{uuid}
        """
        print(f"Fetching findings for project UUID: {project_uuid}...")
        path = f"/api/v1/finding/project/{project_uuid}"
        return self._make_request("GET", path)

    def create_project(
        self, name, version=None, description=None, tags=None, classifier=None, parent_uuid=None
    ):
        """
        Creates a new project.
        Corresponds to PUT /api/v1/project
        """
        data = {"name": name, "classifier": classifier or "APPLICATION"}
        if version:
            data["version"] = version
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        if parent_uuid:
            data["parent"] = {"uuid": parent_uuid}

        return self._make_request("PUT", "/api/v1/project", json=data)

    def clone_project(
        self, project_uuid, version, include_audit_history=True, include_policy_violations=True
    ):
        """
        Clones a project to create a new version.
        Corresponds to PUT /api/v1/project/clone
        """
        data = {
            "project": project_uuid,
            "version": version,
            "includeAuditHistory": include_audit_history,
            "includePolicyViolations": include_policy_violations,
        }
        return self._make_request("PUT", "/api/v1/project/clone", json=data)

    def get_project_by_name_version(self, name, version):
        """
        Gets a project by name and version.
        Corresponds to GET /api/v1/project/lookup
        """
        params = {"name": name, "version": version}
        return self._make_request("GET", "/api/v1/project/lookup", params=params)

    def get_latest_project_version(self, name):
        """
        Gets the latest version of a project by name.
        Corresponds to GET /api/v1/project/latest/{name}
        """
        path = f"/api/v1/project/latest/{name}"
        return self._make_request("GET", path)

    def get_project_children(self, project_uuid):
        """
        Gets child projects of a parent project.
        Corresponds to GET /api/v1/project/{uuid}/children
        """
        path = f"/api/v1/project/{project_uuid}/children"
        return self._make_request("GET", path)

    def get_projects_by_tag(self, tag):
        """
        Gets projects filtered by tag.
        Corresponds to GET /api/v1/project/tag/{tag}
        """
        path = f"/api/v1/project/tag/{tag}"
        return self._make_request("GET", path)

    def get_projects_by_classifier(self, classifier):
        """
        Gets projects filtered by classifier.
        Corresponds to GET /api/v1/project/classifier/{classifier}
        """
        path = f"/api/v1/project/classifier/{classifier}"
        return self._make_request("GET", path)

    def update_project(self, project_uuid, **kwargs):
        """
        Updates an existing project.
        Corresponds to POST /api/v1/project
        """
        # Get current project data first
        current_project = self._make_request("GET", f"/api/v1/project/{project_uuid}")

        # Update with new values
        update_data = {
            "uuid": project_uuid,
            "name": kwargs.get("name", current_project["name"]),
            "version": kwargs.get("version", current_project.get("version")),
            "description": kwargs.get("description", current_project.get("description")),
            "classifier": kwargs.get("classifier", current_project.get("classifier")),
            "tags": kwargs.get("tags", current_project.get("tags", [])),
        }

        return self._make_request("POST", "/api/v1/project", json=update_data)

    def get_project_teams(self, project_uuid):
        """
        Gets all teams that have access to a specific project.
        This requires iterating through teams since there's no direct project->teams endpoint.
        """
        # Note: This is a workaround since DT doesn't have a direct project->teams endpoint
        # We'll need to implement this by checking which teams have access to the project
        # For now, return empty list - this would need to be implemented based on your team structure
        return []

    def add_team_to_project(self, team_uuid, project_uuid):
        """
        Adds a team ACL mapping to a project.
        Corresponds to PUT /api/v1/acl/mapping
        """
        data = {"team": team_uuid, "project": project_uuid}
        return self._make_request("PUT", "/api/v1/acl/mapping", json=data)

    def remove_team_from_project(self, team_uuid, project_uuid):
        """
        Removes a team ACL mapping from a project.
        Corresponds to DELETE /api/v1/acl/mapping/team/{teamUuid}/project/{projectUuid}
        """
        return self._make_request(
            "DELETE", f"/api/v1/acl/mapping/team/{team_uuid}/project/{project_uuid}"
        )

    def get_team_projects(self, team_uuid, exclude_inactive=True, only_root=False):
        """
        Gets all projects assigned to a specific team.
        Corresponds to GET /api/v1/acl/team/{uuid}
        """
        params = {}
        if exclude_inactive:
            params["excludeInactive"] = "true"
        if only_root:
            params["onlyRoot"] = "true"

        return self._make_request("GET", f"/api/v1/acl/team/{team_uuid}", params=params)


class ProjectHierarchyManager:
    """
    Manages hierarchical project structure in Dependency-Track:
    District (SuperParent) -> Business Line (Parent) -> Project (Child)
    Handles version cloning and metadata management.
    """

    def __init__(self, dt_api: DependencyTrackAPI):
        self.dt_api = dt_api

    def _inherit_acls_from_parent(self, parent_uuid: str, child_uuid: str):
        """
        Inherit ACLs from parent project to child project.
        This is a core part of the hierarchical ACL model:
        - District ACLs flow down to Business Lines
        - Business Line ACLs (including inherited District ACLs) flow down to Projects
        """
        try:
            # Note: Since DT doesn't have a direct project->teams endpoint,
            # we'll need to implement a way to track which teams have access
            # This could be done by:
            # 1. Maintaining a mapping in your system
            # 2. Using team metadata/tags to track project assignments
            # 3. Iterating through all teams and checking their project assignments

            # For now, this is a placeholder that logs the inheritance
            print(f"Inheriting ACLs from parent {parent_uuid} to child {child_uuid}")

            # TODO: Implement actual ACL inheritance based on your team structure
            # Example logic would be:
            # 1. Get all teams that have access to parent project
            # 2. Add each team to child project

        except Exception as e:
            print(f"Warning: Could not inherit ACLs from {parent_uuid} to {child_uuid}: {e}")

    def _set_project_acls(self, project_uuid: str, project_type: str, metadata: Dict):
        """
        Set project-specific ACLs based on project type and metadata.

        project_type: 'district', 'business_line', or 'project'
        metadata: Contains team assignments, security requirements, etc.
        """
        try:
            # Extract team assignments from metadata
            teams = metadata.get("teams", [])

            # Add default teams based on project type
            if project_type == "district":
                # District-level teams (high-level visibility)
                default_teams = metadata.get("district_teams", [])
            elif project_type == "business_line":
                # Business line specific teams
                default_teams = metadata.get("business_line_teams", [])
            elif project_type == "project":
                # Project-specific teams
                default_teams = metadata.get("project_teams", [])
            else:
                default_teams = []

            # Combine explicit teams with default teams
            all_teams = list(set(teams + default_teams))

            # Add each team to the project
            for team_uuid in all_teams:
                if team_uuid:  # Ensure team_uuid is not empty
                    try:
                        self.dt_api.add_team_to_project(team_uuid, project_uuid)
                        print(f"Added team {team_uuid} to {project_type} project {project_uuid}")
                    except Exception as e:
                        print(
                            f"Warning: Could not add team {team_uuid} to project {project_uuid}: {e}"
                        )

        except Exception as e:
            print(f"Warning: Could not set ACLs for {project_type} project {project_uuid}: {e}")

    def _get_or_create_district(self, district_name: str, metadata: Dict = None) -> Dict:
        """Get or create a district (top-level project)"""
        try:
            # Look for existing district
            projects = self.dt_api.get_projects_by_tag(f"district:{district_name}")
            if projects:
                return projects[0]
        except:
            pass

        # Create new district
        district_project = self.dt_api.create_project(
            name=district_name,
            description=f"District: {district_name}",
            classifier="APPLICATION",
            tags=[f"district:{district_name}", "hierarchy:district"],
        )
        print(f"Created district: {district_name} ({district_project['uuid']})")

        # Set district-level ACLs
        if metadata:
            self._set_project_acls(district_project["uuid"], "district", metadata)

        return district_project

    def _get_or_create_business_line(
        self, district_uuid: str, business_line_name: str, district_name: str, metadata: Dict = None
    ) -> Dict:
        """Get or create a business line under a district"""
        try:
            # Look for existing business line
            projects = self.dt_api.get_projects_by_tag(f"business_line:{business_line_name}")
            for project in projects:
                # Check if it's under the correct district
                if project.get("parent", {}).get("uuid") == district_uuid:
                    return project
        except:
            pass

        # Create new business line
        business_line_project = self.dt_api.create_project(
            name=business_line_name,
            description=f"Business Line: {business_line_name} (District: {district_name})",
            classifier="APPLICATION",
            parent_uuid=district_uuid,
            tags=[
                f"business_line:{business_line_name}",
                f"district:{district_name}",
                "hierarchy:business_line",
            ],
        )
        print(
            f"Created business line: {business_line_name} under {district_name} ({business_line_project['uuid']})"
        )

        # Inherit ACLs from district (parent)
        self._inherit_acls_from_parent(district_uuid, business_line_project["uuid"])

        # Set business line specific ACLs
        if metadata:
            self._set_project_acls(business_line_project["uuid"], "business_line", metadata)

        return business_line_project

    def _get_or_create_project(
        self, business_line_uuid: str, project_name: str, version: str, metadata: Dict
    ) -> Dict:
        """Get or create a project under a business line"""
        try:
            # Look for existing project with same name under business line
            children = self.dt_api.get_project_children(business_line_uuid)
            for child in children:
                if child["name"] == project_name:
                    # Found existing project, check if version exists
                    try:
                        existing_version = self.dt_api.get_project_by_name_version(
                            project_name, version
                        )
                        if existing_version:
                            print(f"Project {project_name} version {version} already exists")
                            return existing_version
                    except:
                        pass

                    # Version doesn't exist, clone latest version
                    latest_version = self._get_latest_project_version(
                        project_name, business_line_uuid
                    )
                    if latest_version:
                        print(
                            f"Cloning {project_name} from version {latest_version['version']} to {version}"
                        )
                        cloned_project = self.dt_api.clone_project(
                            project_uuid=latest_version["uuid"],
                            version=version,
                            include_audit_history=True,
                            include_policy_violations=True,
                        )

                        # Note: ACLs are automatically inherited from the source project during cloning
                        # However, we may want to add any new project-specific ACLs from metadata
                        if cloned_project and "teams" in metadata:
                            self._set_project_acls(cloned_project["uuid"], "project", metadata)

                        return cloned_project
        except Exception as e:
            print(f"Error checking existing project: {e}")

        # Create new project
        tags = [
            f"project:{project_name}",
            f"business_line:{metadata['business_line']}",
            f"district:{metadata['district']}",
            "hierarchy:project",
        ]

        if metadata.get("gitlab_project_id"):
            tags.append(f"gitlab_project_id:{metadata['gitlab_project_id']}")
        if metadata.get("branch"):
            tags.append(f"branch:{metadata['branch']}")

        # Add custom tags
        if metadata.get("tags"):
            tags.extend(metadata["tags"])

        description = f"Project: {project_name} v{version}\n"
        description += f"Business Line: {metadata['business_line']}\n"
        description += f"District: {metadata['district']}\n"
        if metadata.get("gitlab_project_id"):
            description += f"GitLab Project ID: {metadata['gitlab_project_id']}\n"
        if metadata.get("commit_sha"):
            description += f"Commit SHA: {metadata['commit_sha']}\n"
        if metadata.get("branch"):
            description += f"Branch: {metadata['branch']}\n"

        project = self.dt_api.create_project(
            name=project_name,
            version=version,
            description=description,
            classifier="APPLICATION",
            parent_uuid=business_line_uuid,
            tags=tags,
        )
        print(f"Created new project: {project_name} v{version} ({project['uuid']})")

        # Inherit ACLs from business line (parent)
        self._inherit_acls_from_parent(business_line_uuid, project["uuid"])

        # Set project-specific ACLs
        self._set_project_acls(project["uuid"], "project", metadata)

        return project

    def _get_latest_project_version(
        self, project_name: str, business_line_uuid: str
    ) -> Optional[Dict]:
        """Get the latest version of a project under a business line"""
        try:
            children = self.dt_api.get_project_children(business_line_uuid)
            project_versions = [child for child in children if child["name"] == project_name]

            if not project_versions:
                return None

            # Sort by version (simple string sort, could be enhanced for semantic versioning)
            project_versions.sort(key=lambda x: x.get("version", ""), reverse=True)
            return project_versions[0]
        except:
            return None

    def upload_sbom_with_hierarchy(self, sbom_file_path: str, metadata: Dict) -> Dict:
        """
        Upload SBOM with proper hierarchical project management
        """
        try:
            # Step 1: Ensure district exists
            district = self._get_or_create_district(metadata["district"], metadata)

            # Step 2: Ensure business line exists under district
            business_line = self._get_or_create_business_line(
                district["uuid"], metadata["business_line"], metadata["district"], metadata
            )

            # Step 3: Get or create project version
            project = self._get_or_create_project(
                business_line["uuid"], metadata["project_name"], metadata["version"], metadata
            )

            # Step 4: Upload SBOM to the project
            upload_result = self.dt_api.upload_sbom(
                project_uuid=project["uuid"], sbom_file_path=sbom_file_path
            )

            return {
                "success": True,
                "message": f"SBOM uploaded successfully for {metadata['project_name']} v{metadata['version']}",
                "project_uuid": project["uuid"],
                "district": district["name"],
                "business_line": business_line["name"],
                "project": project["name"],
                "version": project["version"],
                "upload_result": upload_result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to upload SBOM for {metadata['project_name']} v{metadata['version']}",
            }

    def get_hierarchy(self, district: str, business_line: Optional[str] = None) -> Dict:
        """Get project hierarchy for a district/business line"""
        try:
            # Get district (don't create if it doesn't exist for hierarchy queries)
            projects = self.dt_api.get_projects_by_tag(f"district:{district}")
            if not projects:
                return {"error": f"District '{district}' not found"}
            district_project = projects[0]

            hierarchy = {
                "district": {
                    "name": district_project["name"],
                    "uuid": district_project["uuid"],
                    "business_lines": [],
                }
            }

            # Get business lines under district
            business_lines = self.dt_api.get_project_children(district_project["uuid"])

            for bl in business_lines:
                bl_data = {"name": bl["name"], "uuid": bl["uuid"], "projects": []}

                if not business_line or bl["name"] == business_line:
                    # Get projects under business line
                    projects = self.dt_api.get_project_children(bl["uuid"])

                    # Group projects by name (different versions)
                    project_groups = {}
                    for project in projects:
                        name = project["name"]
                        if name not in project_groups:
                            project_groups[name] = []
                        project_groups[name].append(
                            {
                                "name": project["name"],
                                "version": project.get("version", "latest"),
                                "uuid": project["uuid"],
                                "description": project.get("description", ""),
                            }
                        )

                    bl_data["projects"] = project_groups

                hierarchy["district"]["business_lines"].append(bl_data)

            return hierarchy

        except Exception as e:
            return {"error": str(e)}

    def get_project_versions(
        self, district: str, business_line: str, project_name: str
    ) -> List[Dict]:
        """Get all versions for a specific project"""
        try:
            # Get business line
            district_project = self._get_or_create_district(district)
            business_line_project = self._get_or_create_business_line(
                district_project["uuid"], business_line, district
            )

            # Get all versions of the project
            children = self.dt_api.get_project_children(business_line_project["uuid"])
            versions = [
                {
                    "name": child["name"],
                    "version": child.get("version", "latest"),
                    "uuid": child["uuid"],
                    "created": child.get("created"),
                    "lastBomImport": child.get("lastBomImport"),
                }
                for child in children
                if child["name"] == project_name
            ]

            # Sort by version
            versions.sort(key=lambda x: x["version"], reverse=True)
            return versions

        except Exception as e:
            return [{"error": str(e)}]


if __name__ == "__main__":
    load_dotenv()

    # Basic test of API connectivity
    DT_URL = os.getenv("DT_URL", "http://127.0.0.1:8080")
    DT_API_KEY = os.getenv("DT_API_KEY", "")

    if not DT_API_KEY:
        print("ERROR: DT_API_KEY environment variable not set.")
        print("Please set your Dependency-Track API key in the .env file or environment.")
        exit(1)

    print(f"Testing connection to Dependency-Track at {DT_URL}")

    try:
        api = DependencyTrackAPI(DT_URL, DT_API_KEY)
        hierarchy_manager = ProjectHierarchyManager(api)

        # Test basic connectivity
        projects = api.get_projects()
        print(f"✅ Successfully connected to Dependency-Track")
        print(f"Found {len(projects)} existing projects")

        # Test hierarchy functionality
        print("\n🏗️ Testing hierarchy management...")
        test_metadata = {
            "district": "Test District",
            "business_line": "Test Business Line",
            "project_name": "test-project",
            "version": "1.0.0-test",
            "gitlab_project_id": "999",
            "commit_sha": "abc123def456",
            "branch": "main",
            "tags": ["test", "api-validation"],
        }

        # Test hierarchy creation (without actual SBOM upload)
        district = hierarchy_manager._get_or_create_district(test_metadata["district"])
        business_line = hierarchy_manager._get_or_create_business_line(
            district["uuid"], test_metadata["business_line"], test_metadata["district"]
        )

        print(f"✅ Hierarchy test completed:")
        print(f"  District: {district['name']} ({district['uuid']})")
        print(f"  Business Line: {business_line['name']} ({business_line['uuid']})")

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("Please check your DT_URL and DT_API_KEY configuration.")

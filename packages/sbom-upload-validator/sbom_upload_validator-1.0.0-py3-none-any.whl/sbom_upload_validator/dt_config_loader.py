#!/usr/bin/env python3
"""
Dependency-Track Hierarchy Configuration Loader

Loads and validates YAML configuration for initializing Dependency-Track
hierarchical structures. Provides utilities for federal network customization.
"""

import yaml
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import re
from .dt_api_utils import DependencyTrackAPI, ProjectHierarchyManager


class DTConfigLoader:
    """Loads and validates Dependency-Track hierarchy configuration"""

    def __init__(self, config_path: str = "dt_hierarchy_config.yaml"):
        """
        Initialize configuration loader

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = None
        self._load_config()

    def _load_config(self):
        """Load and parse YAML configuration file"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)

            self._validate_config()
            print(f"[OK] Configuration loaded from {self.config_path}")

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise Exception(f"Failed to load configuration: {e}")

    def _validate_config(self):
        """Validate required configuration sections"""
        required_sections = ["metadata", "hierarchy", "teams"]

        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate hierarchy structure
        hierarchy = self.config["hierarchy"]
        if not isinstance(hierarchy, dict) or not hierarchy:
            raise ValueError("Hierarchy section must be a non-empty dictionary")

        for district_name, district_config in hierarchy.items():
            if "business_lines" not in district_config:
                raise ValueError(f"District '{district_name}' missing business_lines")

            for bl_name, bl_config in district_config["business_lines"].items():
                if "projects" not in bl_config:
                    raise ValueError(f"Business line '{bl_name}' missing projects")

    def get_metadata(self) -> Dict:
        """Get configuration metadata"""
        return self.config.get("metadata", {})

    def get_settings(self) -> Dict:
        """Get global settings"""
        return self.config.get("settings", {})

    def get_districts(self) -> List[str]:
        """Get list of district names"""
        return list(self.config["hierarchy"].keys())

    def get_district_config(self, district_name: str) -> Optional[Dict]:
        """Get configuration for a specific district"""
        return self.config["hierarchy"].get(district_name)

    def get_business_lines(self, district_name: str) -> List[str]:
        """Get list of business line names for a district"""
        district_config = self.get_district_config(district_name)
        if not district_config:
            return []
        return list(district_config.get("business_lines", {}).keys())

    def get_business_line_config(self, district_name: str, bl_name: str) -> Optional[Dict]:
        """Get configuration for a specific business line"""
        district_config = self.get_district_config(district_name)
        if not district_config:
            return None
        return district_config.get("business_lines", {}).get(bl_name)

    def get_projects(self, district_name: str, bl_name: str) -> List[Dict]:
        """Get list of projects for a business line"""
        bl_config = self.get_business_line_config(district_name, bl_name)
        if not bl_config:
            return []
        return bl_config.get("projects", [])

    def get_team_info(self, team_uuid: str) -> Optional[str]:
        """Get team name/description for a UUID"""
        return self.config.get("teams", {}).get(team_uuid)

    def get_version_template(self, template_name: str) -> Optional[Dict]:
        """Get version template configuration"""
        return self.config.get("version_templates", {}).get(template_name)

    def get_project_config(self, project_name: str) -> Optional[Dict]:
        """Get specific project configuration overrides"""
        return self.config.get("project_configurations", {}).get(project_name)

    def resolve_teams(self, team_list: List[str]) -> List[str]:
        """
        Resolve team references to actual team UUIDs

        Args:
            team_list: List of team UUIDs or references

        Returns:
            List of resolved team UUIDs
        """
        resolved_teams = []
        teams_config = self.config.get("teams", {})

        for team_ref in team_list:
            # If it's already a UUID format, use as-is
            if re.match(r"^[a-f0-9-]{36}$", team_ref):
                resolved_teams.append(team_ref)
            # If it's in teams config, use the key (UUID)
            elif team_ref in teams_config:
                resolved_teams.append(team_ref)
            else:
                print(f"[WARNING] Team reference '{team_ref}' not found in teams config")
                # Include anyway for manual resolution later
                resolved_teams.append(team_ref)

        return resolved_teams

    def build_project_metadata(self, district_name: str, bl_name: str, project: Dict) -> Dict:
        """
        Build complete project metadata from configuration

        Args:
            district_name: District name
            bl_name: Business line name
            project: Project configuration dict

        Returns:
            Complete metadata dict for project creation
        """
        district_config = self.get_district_config(district_name)
        bl_config = self.get_business_line_config(district_name, bl_name)
        project_config = self.get_project_config(project["name"])
        settings = self.get_settings()

        # Build base metadata
        metadata = {
            "district": district_name,
            "business_line": bl_name,
            "project_name": project["name"],
            "version": "1.0.0",  # Default version
            "description": project.get("description", ""),
        }

        # Collect tags from all levels
        tags = []

        # Global default tags
        default_tags = settings.get("default_tags", {})
        tags.extend(default_tags.get("district", []))
        tags.extend(default_tags.get("business_line", []))
        tags.extend(default_tags.get("project", []))

        # District-level tags
        if district_config:
            tags.extend(district_config.get("tags", []))

        # Business line-level tags
        if bl_config:
            tags.extend(bl_config.get("tags", []))

        # Project-level tags
        tags.extend(project.get("tags", []))

        # Project-specific configuration tags
        if project_config:
            tags.extend(project_config.get("additional_tags", []))

        metadata["tags"] = list(set(tags))  # Remove duplicates

        # Collect teams
        teams = []

        # Global default teams
        default_teams = settings.get("default_teams", {})
        teams.extend(default_teams.get("district_level", []))
        teams.extend(default_teams.get("business_line_level", []))
        teams.extend(default_teams.get("project_level", []))

        # District-level teams
        if district_config:
            teams.extend(district_config.get("teams", []))

        # Business line-level teams
        if bl_config:
            teams.extend(bl_config.get("teams", []))

        # Project-level teams
        teams.extend(project.get("teams", []))

        metadata["district_teams"] = self.resolve_teams(teams)
        metadata["business_line_teams"] = []
        metadata["project_teams"] = []

        return metadata

    def get_project_versions(self, project_name: str) -> List[str]:
        """
        Get versions that should be created for a project

        Args:
            project_name: Name of the project

        Returns:
            List of version strings to create
        """
        project_config = self.get_project_config(project_name)

        if project_config and "version_template" in project_config:
            template_name = project_config["version_template"]
            template = self.get_version_template(template_name)
            if template:
                return template.get("versions", ["1.0.0"])

        # Default to single version
        return ["1.0.0"]

    def export_summary(self) -> Dict:
        """Export configuration summary for review"""
        summary = {
            "metadata": self.get_metadata(),
            "total_districts": len(self.get_districts()),
            "districts": {},
        }

        total_business_lines = 0
        total_projects = 0

        for district_name in self.get_districts():
            business_lines = self.get_business_lines(district_name)
            district_summary = {
                "business_lines": len(business_lines),
                "business_line_names": business_lines,
                "projects": {},
            }

            total_business_lines += len(business_lines)

            for bl_name in business_lines:
                projects = self.get_projects(district_name, bl_name)
                project_names = [p["name"] for p in projects]
                district_summary["projects"][bl_name] = {
                    "count": len(projects),
                    "names": project_names,
                }
                total_projects += len(projects)

            summary["districts"][district_name] = district_summary

        summary["total_business_lines"] = total_business_lines
        summary["total_projects"] = total_projects

        return summary


def main():
    """Test configuration loader"""
    try:
        # Load configuration
        config_loader = DTConfigLoader()

        # Print summary
        print("\n[INFO] Configuration Summary:")
        print("=" * 50)

        summary = config_loader.export_summary()
        metadata = summary["metadata"]

        print(f"Version: {metadata.get('version', 'N/A')}")
        print(f"Description: {metadata.get('description', 'N/A')}")
        print(f"Last Updated: {metadata.get('last_updated', 'N/A')}")
        print()

        print(f"Total Districts: {summary['total_districts']}")
        print(f"Total Business Lines: {summary['total_business_lines']}")
        print(f"Total Projects: {summary['total_projects']}")
        print()

        # District breakdown
        for district_name, district_info in summary["districts"].items():
            print(f"[DISTRICT] {district_name}")
            print(f"   Business Lines: {district_info['business_lines']}")
            for bl_name, bl_info in district_info["projects"].items():
                print(f"   [BL] {bl_name}: {bl_info['count']} projects")
                for project_name in bl_info["names"][:3]:  # Show first 3
                    versions = config_loader.get_project_versions(project_name)
                    print(f"      - {project_name} ({len(versions)} versions)")
                if bl_info["count"] > 3:
                    print(f"      ... and {bl_info['count'] - 3} more")
            print()

        print("[OK] Configuration validation completed successfully!")

    except Exception as e:
        print(f"[ERROR] Configuration validation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

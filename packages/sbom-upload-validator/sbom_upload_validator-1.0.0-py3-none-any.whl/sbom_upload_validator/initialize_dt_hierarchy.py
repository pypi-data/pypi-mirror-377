#!/usr/bin/env python3
"""
Dependency-Track Hierarchy Initialization Script

Reads YAML configuration and initializes the complete hierarchical structure
in Dependency-Track. Designed for federal network deployment and customization.

Usage:
    python initialize_dt_hierarchy.py [--config config.yaml] [--dry-run] [--district DISTRICT]
"""

import argparse
import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv
from .dt_config_loader import DTConfigLoader
from .dt_api_utils import DependencyTrackAPI, ProjectHierarchyManager


class DTHierarchyInitializer:
    """Initialize Dependency-Track hierarchy from configuration"""

    def __init__(self, config_path: str, dt_api: DependencyTrackAPI, dry_run: bool = False):
        """
        Initialize hierarchy initializer

        Args:
            config_path: Path to YAML configuration file
            dt_api: Dependency-Track API client
            dry_run: If True, only simulate operations without making changes
        """
        self.config_loader = DTConfigLoader(config_path)
        self.dt_api = dt_api
        self.hierarchy_manager = ProjectHierarchyManager(dt_api)
        self.dry_run = dry_run

        self.created_districts = {}
        self.created_business_lines = {}
        self.created_projects = {}

        if dry_run:
            print("🔍 DRY RUN MODE: No actual changes will be made")
        print()

    def initialize_complete_hierarchy(self, district_filter: Optional[str] = None):
        """
        Initialize complete hierarchy from configuration

        Args:
            district_filter: If specified, only initialize this district
        """
        print("🏗️ Initializing Dependency-Track Hierarchy")
        print("=" * 60)

        summary = self.config_loader.export_summary()
        metadata = summary["metadata"]

        print(f"Configuration: {metadata.get('description', 'N/A')}")
        print(f"Version: {metadata.get('version', 'N/A')}")
        print(f"Districts to process: {len(summary['districts'])}")
        if district_filter:
            print(f"Filter: Only processing district '{district_filter}'")
        print()

        # Process each district
        districts = self.config_loader.get_districts()
        if district_filter:
            districts = [d for d in districts if d == district_filter]
            if not districts:
                raise ValueError(f"District '{district_filter}' not found in configuration")

        total_operations = 0

        for district_name in districts:
            print(f"🏢 Processing District: {district_name}")
            print("-" * 40)

            try:
                district_ops = self._initialize_district(district_name)
                total_operations += district_ops
                print(f"✅ District '{district_name}' completed ({district_ops} operations)")

            except Exception as e:
                print(f"❌ Failed to initialize district '{district_name}': {e}")
                if not self.dry_run:
                    print("   Continuing with next district...")

            print()

        # Summary
        print("📊 Initialization Summary")
        print("=" * 30)
        print(f"Districts created: {len(self.created_districts)}")
        print(f"Business Lines created: {len(self.created_business_lines)}")
        print(f"Projects created: {len(self.created_projects)}")
        print(f"Total operations: {total_operations}")

        if self.dry_run:
            print("\n🔍 This was a DRY RUN - no actual changes were made")
        else:
            print("\n✅ Hierarchy initialization completed!")

    def _initialize_district(self, district_name: str) -> int:
        """Initialize a single district with all its business lines and projects"""
        operations_count = 0

        # Get district configuration
        district_config = self.config_loader.get_district_config(district_name)
        if not district_config:
            raise ValueError(f"District configuration not found: {district_name}")

        # Create district (SuperParent)
        if not self.dry_run:
            # Build metadata for district creation
            metadata = {
                "district": district_name,
                "business_line": "N/A",  # Not applicable for district level
                "project_name": district_name,
                "version": "1.0.0",
                "description": district_config.get("description", ""),
                "tags": district_config.get("tags", []),
                "district_teams": self.config_loader.resolve_teams(
                    district_config.get("teams", [])
                ),
            }

            district_project = self.hierarchy_manager._get_or_create_district(
                district_name, metadata
            )
            self.created_districts[district_name] = district_project
            print(f"   📁 District: {district_name} ({district_project['uuid']})")
        else:
            print(f"   📁 District: {district_name} (dry-run)")

        operations_count += 1

        # Process business lines
        business_lines = self.config_loader.get_business_lines(district_name)
        for bl_name in business_lines:
            bl_ops = self._initialize_business_line(district_name, bl_name)
            operations_count += bl_ops

        return operations_count

    def _initialize_business_line(self, district_name: str, bl_name: str) -> int:
        """Initialize a single business line with all its projects"""
        operations_count = 0

        # Get business line configuration
        bl_config = self.config_loader.get_business_line_config(district_name, bl_name)
        if not bl_config:
            raise ValueError(f"Business line configuration not found: {bl_name}")

        # Create business line (Parent)
        if not self.dry_run:
            district_project = self.created_districts[district_name]

            # Build metadata for business line creation
            metadata = {
                "district": district_name,
                "business_line": bl_name,
                "project_name": bl_name,
                "version": "1.0.0",
                "description": bl_config.get("description", ""),
                "tags": bl_config.get("tags", []),
                "business_line_teams": self.config_loader.resolve_teams(bl_config.get("teams", [])),
            }

            bl_project = self.hierarchy_manager._get_or_create_business_line(
                district_project["uuid"], bl_name, district_name, metadata
            )
            self.created_business_lines[f"{district_name}::{bl_name}"] = bl_project
            print(f"     📂 Business Line: {bl_name} ({bl_project['uuid']})")
        else:
            print(f"     📂 Business Line: {bl_name} (dry-run)")

        operations_count += 1

        # Process projects
        projects = self.config_loader.get_projects(district_name, bl_name)
        for project in projects:
            project_ops = self._initialize_project(district_name, bl_name, project)
            operations_count += project_ops

        return operations_count

    def _initialize_project(self, district_name: str, bl_name: str, project: Dict) -> int:
        """Initialize a single project with all its versions"""
        operations_count = 0
        project_name = project["name"]

        # Get versions for this project
        versions = self.config_loader.get_project_versions(project_name)

        for version in versions:
            if not self.dry_run:
                bl_project = self.created_business_lines[f"{district_name}::{bl_name}"]

                # Build complete metadata for project
                metadata = self.config_loader.build_project_metadata(
                    district_name, bl_name, project
                )
                metadata["version"] = version

                # Create project version
                project_version = self.hierarchy_manager._get_or_create_project(
                    bl_project["uuid"], project_name, version, metadata
                )

                project_key = f"{district_name}::{bl_name}::{project_name}::{version}"
                self.created_projects[project_key] = project_version

                print(f"       📄 Project: {project_name} v{version} ({project_version['uuid']})")
            else:
                print(f"       📄 Project: {project_name} v{version} (dry-run)")

            operations_count += 1

        return operations_count

    def validate_existing_hierarchy(self) -> Dict:
        """Validate existing hierarchy against configuration"""
        print("🔍 Validating existing hierarchy against configuration...")

        validation_results = {
            "districts": {"missing": [], "existing": [], "extra": []},
            "business_lines": {"missing": [], "existing": [], "extra": []},
            "projects": {"missing": [], "existing": [], "extra": []},
        }

        # Get existing structure from Dependency-Track
        try:
            # Check districts
            config_districts = set(self.config_loader.get_districts())

            for district_name in config_districts:
                try:
                    existing_projects = self.dt_api.get_projects_by_tag(f"district:{district_name}")
                    if existing_projects:
                        validation_results["districts"]["existing"].append(district_name)
                    else:
                        validation_results["districts"]["missing"].append(district_name)
                except:
                    validation_results["districts"]["missing"].append(district_name)

            # Print validation summary
            print("\n📊 Validation Results:")
            print(
                f"Districts - Existing: {len(validation_results['districts']['existing'])}, "
                f"Missing: {len(validation_results['districts']['missing'])}"
            )

            if validation_results["districts"]["missing"]:
                print("  Missing Districts:")
                for district in validation_results["districts"]["missing"]:
                    print(f"    • {district}")

        except Exception as e:
            print(f"❌ Validation failed: {e}")

        return validation_results

    def generate_init_summary(self) -> str:
        """Generate a summary report of what will be initialized"""
        summary = self.config_loader.export_summary()

        report = []
        report.append("Dependency-Track Hierarchy Initialization Plan")
        report.append("=" * 50)
        report.append("")

        metadata = summary["metadata"]
        report.append(f"Configuration: {metadata.get('description', 'N/A')}")
        report.append(f"Version: {metadata.get('version', 'N/A')}")
        report.append(f"Last Updated: {metadata.get('last_updated', 'N/A')}")
        report.append("")

        report.append(f"Total Districts: {summary['total_districts']}")
        report.append(f"Total Business Lines: {summary['total_business_lines']}")
        report.append(f"Total Projects: {summary['total_projects']}")
        report.append("")

        # Detailed breakdown
        for district_name, district_info in summary["districts"].items():
            district_config = self.config_loader.get_district_config(district_name)
            report.append(f"🏢 District: {district_name}")
            report.append(f"   Description: {district_config.get('description', 'N/A')}")
            report.append(f"   Tags: {', '.join(district_config.get('tags', []))}")
            report.append(f"   Business Lines: {district_info['business_lines']}")

            for bl_name, bl_info in district_info["projects"].items():
                bl_config = self.config_loader.get_business_line_config(district_name, bl_name)
                report.append(f"   📂 {bl_name}")
                report.append(f"      Description: {bl_config.get('description', 'N/A')}")
                report.append(f"      Projects: {bl_info['count']}")

                for project_name in bl_info["names"]:
                    versions = self.config_loader.get_project_versions(project_name)
                    report.append(
                        f"        • {project_name} ({len(versions)} versions: {', '.join(versions)})"
                    )
            report.append("")

        return "\\n".join(report)


def main():
    """Main initialization script"""
    parser = argparse.ArgumentParser(
        description="Initialize Dependency-Track hierarchy from YAML configuration"
    )
    parser.add_argument(
        "--config", "-c", default="dt_hierarchy_config.yaml", help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Simulate operations without making actual changes",
    )
    parser.add_argument("--district", "-d", help="Only initialize specified district")
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate existing hierarchy against configuration",
    )
    parser.add_argument(
        "--summary", "-s", action="store_true", help="Show initialization summary and exit"
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    try:
        # Initialize Dependency-Track API client
        dt_url = os.environ.get("DT_URL")
        dt_api_key = os.environ.get("DT_API_KEY")

        if not dt_url or not dt_api_key:
            print("❌ Error: DT_URL and DT_API_KEY environment variables required")
            return 1

        dt_api = DependencyTrackAPI(dt_url, dt_api_key)

        # Test API connectivity
        try:
            dt_api.get_projects()
            print(f"✅ Connected to Dependency-Track API: {dt_url}")
        except Exception as e:
            print(f"❌ Failed to connect to Dependency-Track API: {e}")
            return 1

        # Initialize hierarchy initializer
        initializer = DTHierarchyInitializer(args.config, dt_api, args.dry_run)

        if args.summary:
            # Show summary and exit
            summary = initializer.generate_init_summary()
            print(summary)
            return 0

        if args.validate:
            # Validate existing hierarchy
            initializer.validate_existing_hierarchy()
            return 0

        # Initialize hierarchy
        initializer.initialize_complete_hierarchy(args.district)

        return 0

    except KeyboardInterrupt:
        print("\\n❌ Initialization cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

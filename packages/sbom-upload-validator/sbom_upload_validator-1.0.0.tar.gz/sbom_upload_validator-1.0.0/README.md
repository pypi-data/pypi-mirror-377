# SBOM Upload Validator

A front-end API service for SBOM uploads to OWASP Dependency-Track, including GitLab pipeline integration.  The service manages hierarchical project structures and version cloning to maintain vulnerability analysis continuity.

## Architecture

The system implements a three-tier hierarchy in Dependency-Track:
- **District/Business Unit** (SuperParent) - Top-level organizational unit.
- **Business Line Applications** (Parent) - Department/division under a district or business unit.
- **Project** (Child) - Actual application, application component or service with versions.

### Key Features

- **Version Management**: New SBOMs create new versions, not new projects.
- **Version Cloning**: Automatically clones from latest version to preserve vulnerability analysis.
- **Rich Metadata**: GitLab integration with project IDs, pipeline IDs, commit SHAs, and custom tags.
- **REST API**: Production-ready endpoints for GitLab CI/CD integration.
- **Hierarchical Organization**: Automatic project structure management using tags and parent relationships.
- **YAML Configuration**: Bulk hierarchy initialization from YAML configuration files.
- **API Authentication**: X-API-Key header authentication with multi-key support.
- **Network Ready**: Pre-configured templates for Organization or Government deployments.

## Quick Start

### Prerequisites

- Python 3.8+
- Access to OWASP Dependency-Track instance
- Dependency-Track API key

### Installation

#### Option 1: PyPI Package (Recommended)

```bash
# Install from PyPI
pip install sbom-upload-validator

# Set environment variables
export DT_URL=http://your-dependency-track-api-url
export DT_API_KEY=your-api-key
export API_KEY_GITLAB=your-sbom-upload-api-key

# Run the service
sbom-validator --host 0.0.0.0 --port 8888
```

#### Option 2: Docker Container (Production Ready)

```bash
# Pull from Docker Hub
docker pull stljim/sbom-upload-validator:latest

# Run container
docker run -p 8888:8888 \
  -e DT_URL=http://your-dependency-track-url \
  -e DT_API_KEY=your-api-key \
  -e API_KEY_GITLAB=your-sbom-upload-api-key \
  stljim/sbom-upload-validator:latest
```

#### Option 3: Source Installation (Development)

```bash
# Clone the repository
git clone https://github.com/StL-Jim/sbom-upload-validator.git
cd sbom-upload-validator

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DT_URL=http://your-dependency-track-api-url
export DT_API_KEY=your-api-key
export API_KEY_GITLAB=your-sbom-upload-api-key

# Run the service
python app.py
```

### Docker Compose (Complete Stack)

```bash
# Start complete development stack
docker compose up -d

# This includes:
# - PostgreSQL database
# - Dependency-Track API server  
# - Dependency-Track frontend
# - SBOM Upload Validator API
```

### CLI Tools (PyPI Package)

The PyPI package includes command-line tools for management:

```bash
# Start the API server
sbom-validator --host 0.0.0.0 --port 8888

# Initialize hierarchy from YAML config
dt-hierarchy-init --config dt_hierarchy_config.yaml --dry-run

# Validate configuration
dt-config-validate
```

## 📡 API Endpoints

### Upload SBOM
```bash
POST /api/v1/sbom/upload
```

Upload SBOM with metadata for GitLab pipeline integration.

**Required Fields:**
- `district` - District name (SuperParent)
- `business_line` - Business line name (Parent)  
- `project_name` - Project name (Child)
- `version` - Project version
- `sbom` - SBOM file (multipart/form-data)

**Optional Fields:**
- `gitlab_project_id` - GitLab project ID
- `gitlab_pipeline_id` - GitLab pipeline ID
- `commit_sha` - Git commit SHA
- `branch` - Git branch (default: main)
- `tags` - Comma-separated custom tags

**Example:**
```bash
curl -X POST http://localhost:8888/api/v1/sbom/upload \
  -H "X-API-Key: your-api-key" \
  -F "district=North America" \
  -F "business_line=Financial Services" \
  -F "project_name=payment-api" \
  -F "version=1.2.3" \
  -F "gitlab_project_id=123" \
  -F "commit_sha=abc123def456" \
  -F "sbom=@/path/to/sbom.json"
```

**Note:** All API endpoints (except `/health`) require authentication via the `X-API-Key` header.

### Get Project Hierarchy
```bash
GET /api/v1/projects/hierarchy?district=<name>&business_line=<name>
```

### Get Project Versions
```bash
GET /api/v1/projects/<project_name>/versions?district=<name>&business_line=<name>
```

### Health Check
```bash
GET /health
```

## 🔗 GitLab CI/CD Integration

Add this to your `.gitlab-ci.yml` for automated SBOM uploads:

```yaml
sbom_upload:
  stage: security
  script:
    - |
      curl -X POST $SBOM_VALIDATOR_URL/api/v1/sbom/upload \
        -H "X-API-Key: $SBOM_VALIDATOR_API_KEY" \
        -F "district=$DISTRICT" \
        -F "business_line=$BUSINESS_LINE" \
        -F "project_name=$CI_PROJECT_NAME" \
        -F "version=$CI_COMMIT_TAG" \
        -F "gitlab_project_id=$CI_PROJECT_ID" \
        -F "gitlab_pipeline_id=$CI_PIPELINE_ID" \
        -F "commit_sha=$CI_COMMIT_SHA" \
        -F "branch=$CI_COMMIT_REF_NAME" \
        -F "sbom=@sbom.json"
  only:
    - tags
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DT_URL` | Dependency-Track server URL | `http://127.0.0.1:8080` | Yes |
| `DT_API_KEY` | Dependency-Track API key | - | Yes |
| `API_KEY_GITLAB` | GitLab pipeline API key | - | Yes |
| `API_KEY_ADMIN` | Admin API key for management | - | No |
| `PORT` | Server port | `8888` | No |
| `FLASK_ENV` | Flask environment | `production` | No |

### Using .env File

Create a `.env` file in the project root:

```bash
DT_URL=http://your-dependency-track-url
DT_API_KEY=your-api-key
API_KEY_GITLAB=your-gitlab-pipeline-key
API_KEY_ADMIN=your-admin-key
PORT=8888
FLASK_ENV=development
```

## 🏗️ Hierarchy Configuration System

### YAML-Based Bulk Initialization

The system supports bulk initialization of organizational hierarchies using YAML configuration files, designed for federal network deployments.

#### Quick Setup

```bash
# 1. Copy the example configuration
cp dt_hierarchy_config.example.yaml dt_hierarchy_config.yaml

# 2. Customize with your team UUIDs and organizational structure
# Edit dt_hierarchy_config.yaml

# 3. Preview what will be created (dry run)
python initialize_dt_hierarchy.py --dry-run

# 4. Initialize the complete hierarchy
python initialize_dt_hierarchy.py
```

#### Federal Network Template

The configuration includes federal-appropriate examples:

- **Technology Operations**: IT infrastructure, cybersecurity, software development
- **Mission Operations**: Command systems, communications, intelligence  
- **Support Services**: HR, finance, facilities management

Each district includes appropriate security and compliance tags:
- Security clearance levels (`clearance:secret`, `clearance:top-secret`)
- FISMA compliance markers (`compliance:fisma-high`)
- Data classification (`data:pii`, `data:classified`)
- Criticality levels (`criticality:critical`, `criticality:high`)

#### Configuration Management Commands

```bash
# Show configuration summary
python initialize_dt_hierarchy.py --summary

# Initialize specific district only  
python initialize_dt_hierarchy.py --district "Technology Operations"

# Validate existing hierarchy against config
python initialize_dt_hierarchy.py --validate

# Test configuration loading
python dt_config_loader.py
```

#### Configuration Structure

```yaml
hierarchy:
  "Your District Name":
    description: "District description"
    tags: ["clearance:secret", "category:technology"]
    teams: ["team-uuid-1", "team-uuid-2"]
    
    business_lines:
      "Your Business Line":
        description: "Business line description"  
        tags: ["function:development"]
        teams: ["bl-team-uuid"]
        
        projects:
          - name: "your-project"
            description: "Project description"
            tags: ["type:application", "criticality:high"]
```

See `dt_hierarchy_config.example.yaml` for a complete federal network template.

## 📦 Distribution Channels

### PyPI Package
[![PyPI version](https://badge.fury.io/py/sbom-upload-validator.svg)](https://pypi.org/project/sbom-upload-validator/)

```bash
pip install sbom-upload-validator
```

**Features:**
- 🚀 CLI tools for server management
- 📚 Library API for custom integrations  
- ⚙️ Configuration validation utilities
- 🏗️ Hierarchy initialization commands

### Docker Hub
[![Docker Pulls](https://img.shields.io/docker/pulls/stljim/sbom-upload-validator)](https://hub.docker.com/r/stljim/sbom-upload-validator)

```bash
docker pull stljim/sbom-upload-validator:latest
```

**Available Tags:**
- `latest` - Latest stable release
- `v1.0.0` - Specific version releases  
- `federal` - Federal network optimized
- `develop` - Development builds

**Multi-Architecture Support:**
- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (ARM 64-bit)

## 🧪 Testing

```bash
# Test API connectivity
python dt_api_utils.py

# Health check
curl http://localhost:8888/health

# View API documentation
open http://localhost:8888
```

## 📊 How It Works

1. **Hierarchy Management**: Service automatically creates District→Business Line→Project structure
2. **Version Detection**: Checks if project version already exists
3. **Smart Cloning**: If project exists but version doesn't, clones latest version preserving vulnerability data
4. **SBOM Upload**: Uploads SBOM to the appropriate project version in Dependency-Track
5. **Metadata Enrichment**: Tags projects with GitLab metadata for easy filtering and reporting

## 🔧 Development

### Project Structure

```
├── app.py                              # Main Flask API application
├── dt_api_utils.py                     # Dependency-Track API client and hierarchy manager
├── dt_config_loader.py                 # YAML configuration loader and validator
├── initialize_dt_hierarchy.py          # Bulk hierarchy initialization script
├── dt_hierarchy_config.yaml            # Main hierarchy configuration file
├── dt_hierarchy_config.example.yaml    # Federal network configuration template
├── templates/
│   └── api_docs.html                   # API documentation page
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Container configuration
├── docker-compose.yml                  # Complete development stack
├── CLAUDE.md                           # Detailed architecture documentation
└── README.md                           # This file
```

### Running in Development Mode

```bash
FLASK_ENV=development python app.py
```

## 📚 Documentation

- **API Documentation**: Visit `/` endpoint for interactive documentation
- **Architecture Guide**: See `CLAUDE.md` for detailed implementation details
- **Dependency-Track API**: Includes complete OpenAPI specification in `openapi.yaml`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Complete API documentation available at the root endpoint
- **Architecture**: See `CLAUDE.md` for implementation details
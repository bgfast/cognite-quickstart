# App Packages Zip Files

This module manages the downloading and storage of GitHub repository zip files for deployment to CDF Files API.

## Purpose

The App Packages Zip Files module provides:
- **Simple downloading** of GitHub repositories as zip files
- **Upload to CDF Files API** for offline access by applications
- **Clean file management** with straightforward naming
- **Easy configuration** through simple YAML file

## Components

### Scripts

#### download_packages.py
Simple script for downloading GitHub repositories as zip files for Cognite Toolkit deployment.

**Features:**
- Downloads GitHub repositories configured in `repositories.yaml`
- Saves zip files with clean names (no timestamps)
- Handles rate limiting and error recovery
- Overwrites existing files (no versioning complexity)
- Optional GitHub token support for private repositories

**Usage:**
```bash
cd scripts/
python download_packages.py
```

#### repositories.yaml
Simple configuration file listing repositories to download.

**Structure:**
```yaml
repositories:
  - url: "https://github.com/owner/repo/archive/refs/heads/branch.zip"
    name: "clean-filename-without-extension"
```

### Files Structure

#### app-packages.CogniteFile.yaml
Simple template for uploading zip files to CDF Files API.

**Basic metadata:**
- Package type: "application-package"
- Upload source: "automated-script"
- Source: "github"

## Usage

### 1. Configure Repositories
Edit `scripts/repositories.yaml` to add or modify repositories:

```yaml
repositories:
  - url: "https://github.com/cognitedata/library/archive/refs/heads/added/pattern-mode-beta.zip"
    name: "cognite-library-pattern-mode-beta"
  - url: "https://github.com/bgfast/cognite-quickstart/archive/refs/heads/main.zip"
    name: "cognite-quickstart-main"

config:
  keep_versions: 5
  cleanup_older_than_days: 30
```

### 2. Set Environment Variables (Optional)
For private repositories, set GitHub authentication:
```bash
export GITHUB_TOKEN="your-github-token"  # Optional for private repos
```

### 3. Download Packages
Execute the download process:
```bash
cd scripts/
python download_packages.py
```

### 4. Deploy with Cognite Toolkit
Use the Cognite Toolkit to upload files to CDF:
```bash
cdf build --env your-env modules/app-packages-zips/
cdf deploy --env your-env modules/app-packages-zips/
```

### 5. Verify Upload
Check CDF Files API to confirm zip files are uploaded.

## File Naming Convention

Files are saved with clean, simple names as specified in the configuration:

Examples:
- `cognite-library-pattern-mode-beta.zip`
- `cognite-quickstart-main.zip`

**Benefits:**
- No timestamps (files are overwritten on each run)
- Predictable filenames for applications
- Simple to reference in code

## Integration

### With Applications
Applications (like the GitHub Repo Deployer Streamlit app) can download these zip files from CDF instead of accessing GitHub directly, providing:
- Faster download speeds within CDF environment
- Reduced GitHub API rate limiting
- Consistent file availability
- Offline capability for air-gapped environments

### With Data Model
This module works with the `app-packages-dm` module to provide:
- Structured metadata storage in CDF
- Package information tracking
- File references and relationships

## Dependencies

- **CDF Project**: With Files API access
- **Python packages**: `requests`, `pyyaml`
- **Environment variables**: CDF authentication credentials (for deployment)
- **Network access**: To GitHub for downloading repositories

## Monitoring

The download script provides detailed logging including:
- Download progress and file sizes
- Success/failure status for each repository
- Rate limiting information
- Error details and recovery suggestions

## Maintenance

### Adding New Repositories
1. Edit `scripts/repositories.yaml`
2. Add new URL and name entries
3. Run the download script
4. Deploy with `cdf build` and `cdf deploy`

### Updating Existing Files
Simply run the download script again - files will be overwritten with the latest versions from GitHub.

### File Management
- Files are overwritten on each run (no versioning)
- Clean up old timestamped files manually if needed
- Monitor CDF Files API for storage usage

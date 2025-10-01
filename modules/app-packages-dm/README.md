# App Packages Data Model

This module defines the data model and spaces for storing app package metadata in CDF.

## Purpose

The App Packages Data Model module provides:
- **Data spaces** for organizing app package metadata
- **Data models** for structured storage of package information
- **Datasets** for proper data governance and access control

## Spaces

### app-packages
Main space for storing app package metadata including:
- Package information (name, version, description)
- Repository details (owner, repo, branch)
- Build and deployment metadata
- Package relationships and dependencies

### app-packages-files
Space for storing file metadata and references including:
- File references to zip files stored in CDF Files
- File metadata (size, checksum, upload date)
- File relationships to packages
- Download statistics and usage tracking

## Usage

This module should be deployed before the `app-packages-zips` module as it provides the foundational data model for storing package metadata.

## Dependencies

- CDF project with appropriate permissions
- Data modeling capabilities enabled
- Access to create spaces and datasets

## Related Modules

- `app-packages-zips`: Stores the actual zip files referenced by this data model
- `github-repo-deployer`: Consumes data from these spaces for package deployment

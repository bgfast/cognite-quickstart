# File Upload Fix - October 5, 2025

## Problem
Files uploaded via `cdf deploy` were creating data model instances with `uploaded: False`, meaning the actual file content was never uploaded to CDF Files API.

## Root Cause
The `app-packages-zips` module was missing critical configuration files required by Cognite Toolkit to properly upload files to a data model space:

### Missing Files
1. ❌ `data_sets/app-packages-dataset.DataSet.yaml` - DataSet definition

**Note**: The space definition already exists in the separate `app-packages-dm` module, which should be deployed first.

## Solution
Created the missing configuration by comparing with working `valhall_dm` module structure:

### Created DataSet Configuration
**File:** `data_sets/app-packages-dataset.DataSet.yaml`
```yaml
externalId: app-packages-dataset
name: App Packages Dataset
description: Dataset for storing application package zip files and metadata
```

### CogniteFile Template (Correct Format)
**File:** `files/app-packages.CogniteFile.yaml`
```yaml
- space: 'app-packages'
  externalId: $FILENAME
  name: $FILENAME
  mimeType: application/zip
```

**Important**: Do NOT add `dataSetExternalId` to this file! The `CogniteFile` view schema does not support this property. The DataSet is defined separately for governance purposes but is not a property of file instances.

## How Cognite Toolkit Works with Files

When uploading files to a data model space, the toolkit requires:

1. **Space Definition** (in separate `app-packages-dm` module)
   - Defines the data model space where instances will be created
   - Must be deployed BEFORE the files module
   
2. **DataSet Definition** (`data_sets/*.DataSet.yaml`)
   - Defines the dataset for organizing and controlling access
   - Provides governance but is NOT referenced in file instances
   
3. **File Template** (`files/*.CogniteFile.yaml`)
   - Defines properties: `space`, `externalId`, `name`, `mimeType`
   - Do NOT add `dataSetExternalId` - not supported by CogniteFile view

**Without proper configuration**, the toolkit will:
- ✅ Create data model instances (metadata)
- ❌ NOT upload actual file content
- Result: `uploaded: False` in Files API

## Module Architecture

This project uses a **two-module architecture**:

- **`app-packages-dm`**: Data model foundation (spaces, schemas, datasets)
- **`app-packages-zips`**: Actual file storage (zip files)

**Deployment Order**:
1. First: `cdf deploy modules/app-packages-dm/` (creates infrastructure)
2. Then: `cdf deploy modules/app-packages-zips/` (uploads files)

## Next Steps

1. **Ensure `app-packages-dm` is deployed first**:
   ```bash
   cdf build --env your-env modules/app-packages-dm/
   cdf deploy --env your-env modules/app-packages-dm/
   ```

2. **Delete old files with `uploaded: False`**:
   - Use the `hw-transformations` module's transformation to clean up
   - Or manually delete via CDF UI

3. **Redeploy the files module**:
   ```bash
   cdf build --env your-env modules/app-packages-zips/
   cdf deploy --env your-env modules/app-packages-zips/
   ```

3. **Verify upload**:
   - Check CDF Files API - files should show `uploaded: True`
   - Streamlit app should now find and download all mini zips

## Reference
Working example: `/Users/brent.groom@cognitedata.com/p/cognite-samples-1/cog-demos/modules/common/valhall_dm/`

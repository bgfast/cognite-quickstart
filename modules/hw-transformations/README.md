# Hello World: Transformations

## Overview

This module demonstrates how to use **CDF Transformations** to perform operations on data model instances. It includes examples of querying and deleting instances from the CogniteCore data model.

## 🎯 What You'll Learn

- How to query data models using `cdf_data_models()` function
- How to create DELETE transformations for data model instances
- Proper syntax for data model transformations
- How to target specific spaces and views

## 📋 Included Transformations

### 1. Delete Unuploaded Files
**File**: `delete-unuploaded-files.sql`  
**Purpose**: Remove CogniteFile instances that have `uploaded = false`

This transformation demonstrates:
- DELETE operations on data model instances
- Filtering by properties (`uploaded = false`)
- Targeting a specific space (`app-packages`)

**Configuration**:
- Data Model: `CogniteCore` (in `cdf_cdm` space)
- View: `CogniteFile`
- Version: `v1`
- Target Space: `app-packages`
- Action: `delete`

### 2. Query Files
**File**: `query-files.sql`  
**Purpose**: List all files in the app-packages space with metadata

This is a read-only query example showing:
- How to SELECT from data models
- Accessing multiple properties
- Filtering by space
- Ordering results

## 🚀 Deployment

### Prerequisites
- The `app-packages-dm` module must be deployed first (creates the space and data model)
- Files must exist in the `app-packages` space

### Deploy the Module

```bash
# Build the module
cdf build --env=hw-transformations

# Preview changes
cdf deploy --env=hw-transformations --dry-run

# Deploy
cdf deploy --env=hw-transformations
```

## 📖 Understanding the Syntax

### The `cdf_data_models()` Function

```sql
cdf_data_models(space, data_model, version, view)
```

**Parameters**:
1. **space**: Where the data model is defined (e.g., `cdf_cdm`)
2. **data_model**: The data model name (e.g., `CogniteCore`)
3. **version**: The data model version (e.g., `v1`)
4. **view**: The specific view or container (e.g., `CogniteFile`)

**Example**:
```sql
FROM cdf_data_models("cdf_cdm", "CogniteCore", "v1", "CogniteFile")
```

### DELETE Transformation Configuration

For DELETE operations, the YAML configuration must include:

```yaml
destination:
  type: instances
  dataModel:
    space: cdf_cdm              # Where the data model is defined
    externalId: CogniteCore     # Data model name
    version: v1                 # Data model version
    destinationType: nodes      # Or edges
  instanceSpace: app-packages   # Where instances to delete are located
action: delete                  # DELETE action
```

## 🔍 How to Use

### Running the Delete Transformation

1. **Preview** what will be deleted:
   ```bash
   # Run the query-files.sql to see all files
   # Check which have uploaded = false
   ```

2. **Run the transformation** in CDF UI:
   - Go to **Integrate** → **Transformations**
   - Find "HW: Delete Unuploaded Files"
   - Click **Run**
   - Review the preview
   - Confirm deletion

3. **Or run via CLI**:
   ```bash
   # This requires the transformation to be deployed first
   # Then you can trigger it via API or CLI
   ```

### Testing the Query

You can test the query transformation in the CDF UI:
- Go to **Integrate** → **Transformations**
- Create a new transformation
- Paste the `query-files.sql` content
- Click **Preview** to see results

## ⚠️ Important Notes

### DELETE Operations
- **Always preview first** - DELETE operations are permanent!
- Use specific WHERE clauses to avoid deleting everything
- Test your query with SELECT before changing to DELETE
- Consider backing up data before running DELETE transformations

### Data Model Syntax
- The function is `cdf_data_models()` (plural), not `cdf_data_model`
- All 4 parameters are required
- The space in the function is where the **data model** is defined
- The `instanceSpace` in YAML is where the **instances** are located

### Common Errors

**Error**: `Could not resolve 'cdf_data_model' to a table-valued function`  
**Fix**: Use `cdf_data_models` (plural)

**Error**: Wrong number of parameters  
**Fix**: Ensure all 4 parameters are provided: space, data_model, version, view

**Error**: No instances deleted  
**Fix**: Check that `instanceSpace` in YAML matches the space in your WHERE clause

## 🎓 Learning Path

1. **Start with query-files.sql** - Understand how to read from data models
2. **Examine the results** - See what data is available
3. **Modify the WHERE clause** - Practice filtering
4. **Try the DELETE transformation** - Learn how to remove instances
5. **Create your own transformations** - Apply to your use cases

## 📚 Related Modules

- **app-packages-dm**: Creates the data model and space used in these examples
- **app-packages-zips**: Uploads files that can be queried/deleted
- **hw-function**: Another Hello World module showing CDF Functions

## 🤝 Use Cases

### Data Cleanup
- Remove incomplete uploads
- Delete test data
- Clean up failed imports

### Data Validation
- Query instances to verify data quality
- Find instances missing required properties
- Identify duplicates

### Data Migration
- Delete old instances before reimporting
- Clean up deprecated data structures
- Prepare spaces for new data models

## 📝 Next Steps

After mastering these examples, you can:
- Create transformations for your own data models
- Implement scheduled cleanup jobs
- Build data validation pipelines
- Automate data quality checks

---

**Ready to try it?** Deploy the module and run your first transformation! 🚀

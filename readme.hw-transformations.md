# Hello World: Transformations

Learn how to use CDF Transformations to query and modify data model instances.

## 🎯 What This Module Demonstrates

- **Query data models** using the `cdf_data_models()` function
- **Delete instances** from data models using transformations
- **Proper syntax** for data model operations
- **Best practices** for transformation configuration

## 🚀 Quick Start

### 1. Deploy the Module

```bash
cdf build --env=hw-transformations
cdf deploy --env=hw-transformations --dry-run
cdf deploy --env=hw-transformations
```

### 2. View the Transformations

Go to **Integrate** → **Transformations** in CDF and find:
- **HW: Delete Unuploaded Files** - Example DELETE transformation

### 3. Run a Transformation

1. Select the transformation
2. Click **Preview** to see what will be affected
3. Click **Run** to execute

## 📖 What's Included

### Transformations

1. **delete-unuploaded-files.sql**
   - Deletes CogniteFile instances with `uploaded = false`
   - Demonstrates DELETE operations on data models
   - Targets the `app-packages` space

2. **query-files.sql**
   - Queries all files in the `app-packages` space
   - Read-only example for learning

### Configuration Files

- **module.toml** - Module metadata
- **config.hw-transformations.yaml** - Deployment configuration
- **hw-transformations-dataset.DataSet.yaml** - Dataset for transformations

## 🔍 Key Concepts

### The `cdf_data_models()` Function

```sql
SELECT * FROM cdf_data_models(space, data_model, version, view)
```

**Example**:
```sql
FROM cdf_data_models("cdf_cdm", "CogniteCore", "v1", "CogniteFile")
```

### DELETE Transformation YAML

```yaml
destination:
  type: instances
  dataModel:
    space: cdf_cdm              # Where data model is defined
    externalId: CogniteCore     # Data model name
    version: v1
    destinationType: nodes
  instanceSpace: app-packages   # Where instances are located
action: delete
```

## ⚠️ Important Notes

- **Always preview before running DELETE transformations**
- DELETE operations are permanent
- Test queries with SELECT before using DELETE
- Use specific WHERE clauses to avoid deleting everything

## 📚 Learn More

See the full README in `modules/hw-transformations/README.md` for:
- Detailed syntax explanations
- Common errors and solutions
- Use cases and examples
- Learning path

## 🎓 Prerequisites

- **app-packages-dm** module must be deployed (creates the data model)
- Some files should exist in the `app-packages` space to query/delete

## 🤝 Related Modules

- **hw-function** - Hello World Functions example
- **hw-neat** - Hello World NEAT data modeling example
- **app-packages-dm** - Creates the data model used in examples

---

**Ready to learn transformations?** Deploy and explore! 🚀

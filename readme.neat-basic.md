# NEAT Basic Module

A comprehensive NEAT (Network Extraction and Analysis Tool) implementation for Cognite Data Fusion, featuring Excel-based data modeling, automated YAML generation, and a Streamlit interface for data management.

## 🎯 Overview

The NEAT Basic module demonstrates how to:
- Define data models in Excel using NEAT
- Generate CDF Toolkit-compatible YAML files automatically
- Deploy data models to Cognite Data Fusion
- Manage data through a user-friendly Streamlit interface
- Test and validate your NEAT implementation

## 📁 Module Structure

```
modules/neat-basic/
├── data_models/
│   ├── NeatBasic.xlsx                    # Excel data model definition (source of truth)
│   └── data_models/                      # NEAT-generated YAML files
│       ├── containers/
│       │   └── NeatBasic.container.yaml  # Generated container definition
│       ├── views/
│       │   └── NeatBasic.view.yaml       # Generated view definition
│       ├── EDM-COR-ALL-NEAT.space.yaml  # Generated space definition
│       └── HWNeatDM.datamodel.yaml      # Generated data model definition
├── streamlit/
│   ├── neat-basic/                       # Streamlit app for data management
│   │   ├── main.py                       # Main application
│   │   ├── data_modeling.py              # CDF data modeling wrapper
│   │   └── requirements.txt              # Python dependencies
│   ├── neat-basic.Streamlit.yaml         # Streamlit app configuration
│   └── README.md                         # Streamlit app documentation
├── generate_edm_yaml_files.py            # NEAT YAML generation script
├── test_neat_basic.py                    # Comprehensive test suite
├── sample_data_generator.py              # Sample data generation
├── integration_test.py                   # Integration testing
└── README.md                             # Module documentation
```

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have NEAT installed:
```bash
pip install cognite-neat
```

### 2. Generate YAML Files from Excel

```bash
# Navigate to the module
cd modules/neat-basic

# Generate YAML files from Excel model
python generate_edm_yaml_files.py
```

### 3. Deploy to CDF

```bash
# Build the module
cdf build --env neat-basic

# Deploy with dry-run first
cdf deploy --env neat-basic --dry-run

# Deploy to CDF
cdf deploy --env neat-basic
```

### 4. Access the Streamlit App

After deployment, the "NEAT Basic" app will be available in your CDF project under the Streamlit section.

## 📊 Data Model

### Excel Definition (`NeatBasic.xlsx`)

The data model is defined in Excel with the following structure:
- **Space**: `EDM-COR-ALL-NEAT`
- **Container**: `NeatBasic`
- **Properties**:
  - `newString` (Text): Main data property for storing string values

### Generated YAML Files

NEAT automatically generates CDF Toolkit-compatible YAML files:
- **Space**: Defines the data model namespace
- **Container**: Defines the data structure and properties
- **View**: Defines the queryable interface
- **Data Model**: Defines the overall model configuration

## 🔧 Streamlit Interface

The NEAT Basic Streamlit app provides three main modes:

### 1. Create New Instance
- Form-based interface for creating individual instances
- Input validation and error handling
- Real-time feedback and success notifications

### 2. View Existing Instances
- Browse and search existing data
- Advanced filtering capabilities
- Export data to CSV
- Pagination and sorting

### 3. Bulk Import
- Upload CSV files for batch data creation
- Progress tracking and error reporting
- Validation and rollback capabilities
- Template download for proper formatting

## 🧪 Testing Suite

### Run All Tests
```bash
# Navigate to module
cd modules/neat-basic

# Run comprehensive test suite
python test_neat_basic.py
```

### Test Categories

1. **Space Tests**: Verify space deployment and configuration
2. **Container Tests**: Validate container structure and properties
3. **View Tests**: Test view deployment and queryability
4. **CRUD Tests**: Test create, read, update, delete operations
5. **Data Validation**: Verify data constraints and validation rules
6. **Integration Tests**: End-to-end workflow testing

### Sample Data Generation
```bash
# Generate sample data for testing
python sample_data_generator.py
```

## ⚙️ Configuration

### Environment Configuration (`config.neat-basic.yaml`)

Key configuration parameters:
- **Environment**: `bgfast` (development)
- **Validation Type**: `dev`
- **Selected Modules**: `modules/neat-basic`

### NEAT Variables
- `neat_basic_space`: Space name for NEAT data
- `neat_basic_container`: Container name
- `neat_basic_view`: View name
- `neat_basic_dataset`: Dataset for data organization

## 🔄 NEAT Workflow

### 1. Design Phase
1. Define your data model in `NeatBasic.xlsx`
2. Specify properties, types, and relationships
3. Configure validation rules and constraints

### 2. Generation Phase
```bash
python generate_edm_yaml_files.py
```
- Reads Excel file
- Generates YAML files in `data_models/` directory
- Validates generated files

### 3. Deployment Phase
```bash
cdf build --env neat-basic
cdf deploy --env neat-basic --dry-run
cdf deploy --env neat-basic
```

### 4. Testing Phase
```bash
python test_neat_basic.py
```

### 5. Usage Phase
- Access Streamlit app in CDF
- Create and manage data instances
- Monitor and validate data quality

## 📋 CSV Import Format

For bulk data import, use this CSV structure:

```csv
external_id,new_string
neat_item_001,Sample data value 1
neat_item_002,Sample data value 2
neat_item_003,Sample data value 3
```

**Required Columns**:
- `external_id`: Unique identifier for each instance
- `new_string`: String value for the newString property

## 🛠️ Customization

### Extending the Data Model

1. **Update Excel File**: Modify `NeatBasic.xlsx` with new properties
2. **Regenerate YAML**: Run `generate_edm_yaml_files.py`
3. **Update Streamlit**: Modify forms in `streamlit/neat-basic/main.py`
4. **Update Tests**: Add tests for new properties in `test_neat_basic.py`

### Adding New Properties

Example: Adding a `description` property
1. Add column in Excel: `description | Text | Optional description`
2. Regenerate YAML files
3. Update Streamlit forms:
   ```python
   description = st.text_area("Description", help="Optional description")
   properties = {
       "newString": new_string,
       "description": description
   }
   ```

## 🔍 Troubleshooting

### Common Issues

1. **NEAT Import Error**
   ```bash
   pip install cognite-neat
   ```

2. **YAML Generation Fails**
   - Check Excel file format
   - Verify NEAT syntax in Excel
   - Check file permissions

3. **Deployment Errors**
   - Run dry-run first: `cdf deploy --env neat-basic --dry-run`
   - Check authentication: `source cdfenv.sh && cdfenv bgfast`
   - Verify configuration in `config.neat-basic.yaml`

4. **Streamlit App Issues**
   - Check app logs in CDF
   - Verify data model deployment
   - Test authentication

### Debug Commands

```bash
# Check build status
ls -la build/

# Verbose deployment
cdf deploy --env neat-basic -v

# Test NEAT generation
python -c "import cognite.neat; print('NEAT available')"
```

## 📚 Documentation Links

- **NEAT Documentation**: [NEAT Installation Guide](https://cognite-neat.readthedocs-hosted.com/en/latest/gettingstarted/installation.html)
- **CDF Toolkit**: [Cognite Toolkit Documentation](https://developer.cognite.com/dev/guides/toolkit/)
- **Streamlit**: [Streamlit Documentation](https://docs.streamlit.io/)

## 🔐 Security & Access

- **Authentication**: OAuth with CDF project credentials
- **Access Control**: Respects CDF access management
- **Data Security**: All operations through secure CDF APIs
- **Audit Trail**: All changes logged in CDF

## 📞 Support

For issues or questions:

1. **Check Logs**: Review CDF deployment and app logs
2. **Verify Setup**: Ensure NEAT and authentication are configured
3. **Test Locally**: Run tests and Streamlit app locally first
4. **Documentation**: Refer to NEAT and CDF Toolkit documentation

## 🎉 Success Criteria

Your NEAT Basic module is working correctly when:

- ✅ Excel file generates valid YAML files
- ✅ Data model deploys successfully to CDF
- ✅ All tests pass in the test suite
- ✅ Streamlit app loads and connects to CDF
- ✅ You can create, view, and manage data instances
- ✅ Bulk import works with CSV files

## 🚀 Next Steps

Once NEAT Basic is working:

1. **Extend the Model**: Add more properties and relationships
2. **Advanced Analytics**: Build dashboards and reports
3. **Integration**: Connect with other CDF resources
4. **Automation**: Set up CI/CD for model updates
5. **Production**: Deploy to production environment

---

**Version**: 1.03  
**Last Updated**: October 2025  
**Compatibility**: NEAT 0.x, CDF Toolkit 1.x, Streamlit 1.x

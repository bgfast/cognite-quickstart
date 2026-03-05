# NEAT Basic Streamlit App

This directory contains a comprehensive Streamlit application for managing the NEAT Basic data model.

## 🔧 NEAT Basic (`hw-neat`)

A complete interface for **managing data** in your NEAT Basic data model.

### Features:
- **Create New Instances**: Form-based interface for creating individual NeatBasic instances
- **View Existing Instances**: Browse and search existing data with filtering capabilities
- **Bulk Import**: Upload CSV files to create multiple instances at once
- **Data Validation**: Built-in validation and error handling
- **Export Options**: Download data as CSV files
- **Search & Filter**: Advanced search capabilities with real-time filtering

### Usage Modes:
1. **Create New Instance**: Fill out a form to create a single NeatBasic instance
2. **View Existing Instances**: Browse, search, and export existing data
3. **Bulk Import**: Upload a CSV file with columns `external_id` and `new_string`

## 🚀 Deployment

### Local Development

Run the apps locally for development:

```bash
# Navigate to the streamlit directory
cd modules/hw-neat/streamlit

# Install dependencies
pip install -r requirements.txt

# Run the NEAT Basic app
cd hw-neat
streamlit run main.py
```

### CDF Deployment

Deploy to Cognite Data Fusion using the toolkit:

```bash
# Build the project (includes Streamlit apps)
cdf build --env hw-neat

# Deploy to CDF
cdf deploy --env hw-neat
```

The app will be available in your CDF project under the Streamlit section as "NEAT Basic".

## 🔧 Configuration

### Environment Variables

The app uses the following configuration:
- **CDF_PROJECT**: Your CDF project name (default: "bgfast")
- **CDF_CLUSTER**: Your CDF cluster (default: "bluefield")
- **Authentication**: Uses OAuth with IDP settings from your environment

### Data Model Configuration

The app is configured to work with:
- **Space**: `EDM-COR-ALL-NEAT` (from NEAT-generated space)
- **Container**: `NeatBasic` (from NEAT-generated container)
- **Properties**: `newString` (main data property)

## 📋 CSV Import Format

For bulk import in the NEAT Basic app, use this CSV format:

```csv
external_id,new_string
neat_item_001,Sample data value 1
neat_item_002,Sample data value 2
neat_item_003,Sample data value 3
```

Required columns:
- `external_id`: Unique identifier for each instance
- `new_string`: String value for the newString property


## 🛠️ Customization

To customize the app for your specific NEAT model:

1. **Update Space/Container IDs**: Modify the `space_id` in the app configuration
2. **Add Properties**: Extend the forms to include additional properties from your NEAT model
3. **Custom Validation**: Add domain-specific validation rules
4. **Styling**: Customize the Streamlit interface with your branding

## 🔐 Security

- App uses OAuth authentication with your CDF project
- All data operations respect CDF access controls
- No sensitive data is stored locally
- Authentication tokens are handled securely by the Cognite SDK

## 📞 Support

For issues or questions:
1. Check the app logs in CDF for deployment issues
2. Verify your NEAT data model is properly deployed
3. Ensure authentication is configured correctly
4. Test with the NEAT testing suite first

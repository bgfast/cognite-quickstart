# Cognite Quickstart Project

This project is set up with the Live Weather Data module from the Cognite samples repository.

## Overview

This project includes:
- **Live Weather Data Module**: A comprehensive data integration module that collects real-time temperature data from the Valhall oil platform using hosted REST extractors
- **Foundation Module**: Basic CDF setup and access management
- **Valhall Data Model**: Core data model for industrial assets
- **Offshore Oil & Gas Industry Model**: Industry-specific data model
- **Analytics & Monitoring**: Operations summarizer, pipeline monitor, and super emitter
- **Streamlit Applications**: Time series annotation, work package generator, and hardware canvas

## Setup Instructions

### 1. Environment Configuration

1. **Use your existing environment file from `~/envs`**:
   ```bash
   source ~/envs/your-env-file.sh
   ```

2. **Or copy the template and customize**:
   ```bash
   cp cdfenv.sh cdfenv.local.sh
   # Edit cdfenv.local.sh with your actual CDF project details
   source cdfenv.local.sh
   ```

   Required environment variables:
   - `CDF_PROJECT`: Your CDF project name
   - `CDF_CLUSTER`: Your CDF cluster
   - `IDP_CLIENT_ID` and `IDP_CLIENT_SECRET`: Your IDP credentials
   - Other required environment variables

### 2. Deploy the Project

1. **Build the project**:
   ```bash
   cdf build
   ```

2. **Deploy to CDF**:
   ```bash
   cdf deploy
   ```

### 3. Verify Deployment

After deployment, you can verify the components in the CDF UI:

#### A) Extraction Pipeline (Hosted Connector)
1. Navigate to **Data Integration** → **Extraction pipelines** → **Hosted extractors** tab
2. Look for `valhall_rest_source` (visible in the list with throughput: 1223 datapoints p/hr)
3. Click on `valhall_rest_source` to see job details and configuration
4. Verify: Status shows "Connected" and "Currently running" with 100.00% uptime

#### B) Data Workflow
1. Navigate to **Data Integration** → **Data workflows**
2. Look for `wf_live_weather_data_valhall` (description: "Live weather data transformation for valhall")
3. Click on the workflow to see execution history and status
4. Verify: Workflow is processing data after hosted extractor completes

#### C) Data Explorer
1. Navigate to **Data Explorer** → **Time series** tab
2. Search for `valhall_temperature`
3. Verify: Time series exists with temperature data

#### D) Main Search UI
1. Navigate to **Search** (main search interface)
2. Search for `valhall`
3. Filter by **Time series** (should show 1 result)
4. Results: `valhall_temperature` with description "valhall temperature", source unit "degC", and preview chart

## Project Structure

```
cognite-quickstart/
├── config.all.yaml                    # Main configuration file
├── cdfenv.sh                         # Environment variables template
├── README.md                         # This file
└── modules/
    ├── admin/
    │   ├── module.toml              # Admin module configuration
    │   ├── README.md               # Admin module documentation
    │   └── github-repo-deployer/   # GitHub Repo to CDF Deployer
    │       ├── module.toml         # Deployer module configuration
    │       ├── README.md          # Deployer documentation
    │       └── streamlit/         # Streamlit application
    │           ├── GitHubRepoDeployer.Streamlit.yaml
    │           └── github-repo-deployer/
    │               ├── main.py
    │               ├── requirements.txt
    │               └── run.sh
    ├── common/
    │   ├── foundation/               # Foundation module
    │   └── valhall_dm/              # Valhall data model
    └── in-development/
        └── live_weather_data/        # Live weather data module
            ├── hosted_extractors/    # REST extractor configuration
            ├── transformations/      # Data transformation logic
            ├── workflows/           # Workflow definitions
            └── README.md           # Module documentation
```

## Key Features

### Live Weather Data Module
- **Real-time Data Collection**: Hourly temperature data from Valhall oil platform
- **REST API Integration**: Uses Open-Meteo API for weather data
- **Data Processing**: Transforms raw API data into structured time series
- **Asset Association**: Links temperature data to platform assets
- **Historical Data**: Collects 90 days of historical data

### GitHub Repo to CDF Deployer (Streamlit App)
- **Two access modes**: Public repositories (no GitHub account needed) and Private repositories (requires GitHub authentication)
- **Download any GitHub repository** as a ZIP file
- **Extract and process** the downloaded files
- **Build** the project using `cdf build`
- **Deploy** to CDF using `cdf deploy`
- **Branch selection** - choose from available repository branches
- **Debug mode** for detailed logging and troubleshooting

#### Running the Streamlit App
The GitHub Repo Deployer is now properly integrated as a Cognite module. To use it:

1. **Deploy the module** to your CDF project:
   ```bash
   cdf build && cdf deploy
   ```

2. **Access the app** from the CDF UI under Streamlit applications

3. **Or run locally** for development:
   ```bash
   cd modules/admin/github-repo-deployer/streamlit/github-repo-deployer
   ./run.sh
   # or
   streamlit run main.py
   ```

### Data Flow
```
Open-Meteo API → Hosted Extractor → Data Mapping → Destination → Workflow → Transformation → Time Series
```

## Customization

### Changing Location
To use a different location instead of Valhall:

1. **Edit `config.all.yaml`**:
   ```yaml
   variables:
     default_location: your_location  # Change from "valhall"
   ```

2. **Update API parameters in `modules/in-development/live_weather_data/hosted_extractors/rest.Job.yaml`**:
   ```yaml
   config:
     query: {
       "latitude": "YOUR_LATITUDE",
       "longitude": "YOUR_LONGITUDE", 
       "hourly": "temperature_2m",
       "past_days": "90"
     }
   ```

3. **Update asset association in transformation SQL** if needed

## Dependencies

- **Foundation Module**: Required for basic CDF setup
- **Valhall Data Model**: Required for asset associations
- **CDF Authentication**: Requires valid IDP credentials

## Usage Examples

### Accessing Temperature Data via CDF Client
```python
from cognite.client import CogniteClient

client = CogniteClient()

# Get temperature time series
ts = client.time_series.retrieve(external_id="valhall_temperature")

# Get recent temperature data
data = client.time_series.data.retrieve(
    external_id="valhall_temperature",
    start="1d-ago",
    end="now"
)
```

### Using in Streamlit Applications
```python
import streamlit as st
from cognite.client import CogniteClient

client = CogniteClient()

# Display current temperature
data = client.time_series.data.retrieve(
    external_id="valhall_temperature",
    start="1h-ago",
    end="now"
)

if data:
    latest_temp = data[0].value
    st.metric("Valhall Temperature", f"{latest_temp}°C")
```

## Troubleshooting

### Check Hosted Extractor Status
- Navigate to **Data Integration** → **Extraction pipelines** → **Hosted extractors**
- Verify `valhall_rest_source` shows "Connected" and "Currently running"
- Check throughput and last modified timestamps

### Check Workflow Execution
- Navigate to **Data Integration** → **Data workflows**
- Verify `wf_live_weather_data_valhall` is executing successfully
- Check execution history for any errors

### Check Time Series Data
- Navigate to **Search** → search for `valhall` → filter by **Time series**
- Verify `valhall_temperature` exists with recent data
- Check preview chart shows temperature variation over time

### Common Issues
- **API Failures**: Hosted extractor will retry on next scheduled run
- **Authentication Issues**: Check IDP credentials in configuration
- **Data Processing Errors**: Workflow will abort and retry with exponential backoff
- **Asset Association Issues**: Verify data model is deployed

## Performance Considerations

- **Data Volume**: ~24 data points per day per location
- **Storage**: Minimal impact on CDF storage
- **API Limits**: Open-Meteo API has generous rate limits
- **Processing**: Lightweight transformations with minimal compute impact

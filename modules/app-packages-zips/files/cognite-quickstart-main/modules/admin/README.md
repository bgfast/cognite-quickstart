# Admin Module

Administrative tools for CDF environment management.

## Components

### GitHub Repo Deployer
A Streamlit application that downloads files from public GitHub repositories and deploys them using the Cognite toolkit.

**Features:**
- Download any public GitHub repository as a ZIP file
- Extract and process the downloaded files
- Build the project using `cdf build`
- Deploy to CDF using `cdf deploy`
- Branch selection from available repository branches
- Debug mode for detailed logging and troubleshooting

**Usage:**
1. Deploy this module to your CDF project
2. Access the GitHub Repo Deployer from the CDF UI
3. Configure repository details and deploy

**Supported Repositories:**
- Cognite samples (`cognitedata/cognite-samples`)
- Cognite modules (various repositories)
- Custom Cognite toolkit projects
- Any repository with `config.all.yaml` or similar configuration files

# GitHub Repo to CDF Deployer

A Streamlit application that downloads files from public GitHub repositories and deploys them using the Cognite toolkit.

## Features

- **Download any GitHub repository** (public or private) as a ZIP file
- **GitHub OAuth authentication** for private repository access
- **Extract and process** the downloaded files
- **Build** the project using `cdf build`
- **Deploy** to CDF using `cdf deploy`
- **Branch selection** - choose from available repository branches
- **Debug mode** for detailed logging and troubleshooting

## Usage

1. **Deploy this module** to your CDF project using the Cognite toolkit
2. **Access the Streamlit app** from the CDF UI
3. **Configure the repository**:
   - Enter the GitHub repository owner (e.g., `cognitedata`)
   - Enter the repository name (e.g., `cognite-samples`)
   - Click "Load Branches" to see available branches
   - Select the desired branch
4. **Deploy**:
   - Click "Download Repository & Deploy"
   - The app will automatically download, extract, build, and deploy

## Supported Repositories

This tool works with any GitHub repository (public or private) that contains Cognite toolkit configuration files, including:

- **Cognite samples** (`cognitedata/cognite-samples`)
- **Cognite modules** (various repositories)
- **Custom Cognite toolkit projects**
- **Any repository with `config.all.yaml` or similar configuration files**
- **Private repositories** (with GitHub OAuth authentication)

## Requirements

- **Cognite toolkit** (`cdf`) must be available in the deployment environment
- **CDF authentication** must be configured
- **GitHub OAuth App** (for private repository access)

## GitHub OAuth Setup

To enable private repository access, you need to set up GitHub OAuth:

### 1. Create a GitHub OAuth App

1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: `CDF GitHub Deployer`
   - **Homepage URL**: `http://localhost:8501`
   - **Authorization callback URL**: `http://localhost:8501`
4. Click "Register application"
5. Note down the **Client ID** and **Client Secret**

### 2. Set Environment Variables

```bash
export GITHUB_CLIENT_ID=your_client_id_here
export GITHUB_CLIENT_SECRET=your_client_secret_here
export GITHUB_REDIRECT_URI=http://localhost:8501
```

### 3. Required Scopes

The OAuth app will request the following scopes:
- `repo` - Full control of private repositories

## Troubleshooting

### Common Issues

- **"Cognite toolkit not found"**: The toolkit must be installed in the deployment environment
- **"CDF client not available"**: CDF authentication must be configured
- **"Build failed"**: Check if the repository contains valid Cognite configuration
- **"Deploy failed"**: Verify CDF project permissions and configuration

### Debug Mode

Enable debug mode in the sidebar to see:
- Detailed logging information
- CDF client connection status
- File extraction paths
- Build and deploy output

## Example Usage

1. **Deploy Cognite samples**:
   - Owner: `cognitedata`
   - Repository: `cognite-samples`
   - Branch: `main`

2. **Deploy a specific module**:
   - Owner: `cognitedata`
   - Repository: `cog-demos`
   - Branch: `main`

3. **Deploy your own project**:
   - Owner: `your-username`
   - Repository: `your-cognite-project`
   - Branch: `main`

## Security Notes

- This tool only works with **public repositories**
- No authentication is required for downloading public repositories
- CDF authentication is handled through the deployment environment
- Temporary files are automatically cleaned up after deployment

## Limitations

- Only supports public GitHub repositories
- Requires Cognite toolkit to be available in the deployment environment
- Requires valid CDF authentication
- Build and deploy operations have timeouts (5 min build, 10 min deploy)
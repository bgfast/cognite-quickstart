# All Environment Configuration

## Overview
This configuration (`config.all.yaml`) is the **default and comprehensive** environment setup for the Cognite Quickstart project. It includes all modules and is designed for production or full-featured deployments.

## Environment Details
- **Environment Name**: `all`
- **Target**: Production/Full deployment
- **Modules Included**: All available modules
- **Validation Type**: Development (with production readiness)

## What's Included
- **Admin Modules**: GitHub repo deployer, administrative tools
- **Common Modules**: Foundation data, Valhall data model
- **Development Modules**: Live weather data, experimental features

## Use Cases
- **Production deployments** with full feature set
- **Complete development environment** setup
- **Comprehensive testing** of all modules
- **Full-stack demonstrations**

## Key Features
- ✅ All administrative tools
- ✅ Complete data foundation
- ✅ Weather data integration
- ✅ Full Valhall data model
- ✅ All transformations and workflows

## Deployment Notes
- This is the **recommended configuration** for most users
- Includes all available functionality
- Suitable for both development and production
- Requires full CDF project permissions

## Environment Variables Required
- `CDF_PROJECT`: Target CDF project
- `CDF_CLUSTER`: CDF cluster URL
- `CDF_URL`: CDF API endpoint
- Authentication credentials (API key or OAuth2)

## Next Steps
1. Ensure all required environment variables are set
2. Verify CDF project permissions
3. Deploy using `cdf deploy --env all`
4. Monitor deployment logs for any issues

#!/bin/bash

# CDF Environment Configuration
# Copy this file to cdfenv.sh and fill in your actual values
# Source this file before running cdf commands: source cdfenv.sh

# CDF Project Configuration
export CDF_PROJECT="your-cdf-project-name"
export CDF_CLUSTER="your-cdf-cluster"

# IDP Authentication Configuration
export IDP_CLIENT_ID="your-idp-client-id"
export IDP_CLIENT_SECRET="your-idp-client-secret"
export IDP_SCOPES="https://${CDF_CLUSTER}.cognitedata.com/.default"
export IDP_TENANT_ID="your-tenant-id"
export IDP_TOKEN_URL="https://login.microsoftonline.com/${IDP_TENANT_ID}/oauth2/v2.0/token"

# Function Configuration
export FUNCTION_CLIENT_ID="your-function-client-id"
export FUNCTION_CLIENT_SECRET="your-function-client-secret"
export TRANSFORMATION_CLIENT_ID="your-transformation-client-id"
export TRANSFORMATION_CLIENT_SECRET="your-transformation-client-secret"

# User Configuration
export USER_IDENTIFIER="your-user-identifier"
export SUPERUSER_SOURCEID_ENV="your-superuser-sourceid"

# Public Data Configuration (if using public data)
export TENANT_PUBLICDATA="your-publicdata-tenant"
export CLI_ID_PUBLICDATA="your-publicdata-client-id"
export CLI_SECRET_PUBLICDATA="your-publicdata-client-secret"
export CLUSTER_PUBLICDATA="your-publicdata-cluster"

echo "CDF environment variables loaded for project: ${CDF_PROJECT}"
echo "Cluster: ${CDF_CLUSTER}"
echo "To deploy: cdf build && cdf deploy"

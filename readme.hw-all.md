# Hello World Complete Demo Set

A comprehensive collection of Hello World examples demonstrating Cognite Data Fusion development patterns with Functions, Streamlit, and NEAT data modeling.

## 🎯 Overview

This configuration deploys a complete set of Hello World modules that demonstrate:

1. **Function + Streamlit Integration** (`hw-function`)
   - How to call Cognite Functions from Streamlit
   - Complete request/response cycle
   - Real-time status and logging

2. **NEAT Data Modeling** (`hw-neat`)
   - Excel-based data model design
   - Automated YAML generation
   - CRUD operations via Streamlit
   - Testing and validation

## 📦 Included Modules

### 1. Hello World Function (`hw-function`)

**Purpose**: Demonstrates the fundamental pattern for Function-Streamlit integration

**Components**:
- Simple Cognite Function that receives input and returns a greeting
- Streamlit app with interactive UI
- Real-time status updates and logs
- Full response visualization

**Use Case**: Learn how to build interactive applications that leverage server-side Functions

**Documentation**: See `readme.hw-function.md`

### 2. Hello World NEAT (`hw-neat`)

**Purpose**: Demonstrates Excel-based data modeling with NEAT and CDF integration

**Components**:
- Excel data model definition (`HWNeatBasic.xlsx`)
- Automated YAML generation script
- Streamlit app for data management (Create, Read, Update, Delete)
- Comprehensive test suite
- Sample data generator

**Use Case**: Learn how to design, deploy, and manage custom data models in CDF

**Documentation**: See `readme.hw-neat.md`

## 🚀 Quick Start

### Option A: Deploy Everything

Deploy all Hello World modules at once:

```bash
# Build all modules
cdf build --config config.all-hw.yaml

# Deploy to CDF
cdf deploy --config config.all-hw.yaml
```

### Option B: Deploy Individual Modules

Deploy modules one at a time:

```bash
# Deploy just the function demo
cdf build --config config.hw-function.yaml
cdf deploy --config config.hw-function.yaml

# Deploy just the NEAT demo
cdf build --config config.hw-neat.yaml
cdf deploy --config config.hw-neat.yaml
```

## 📚 Learning Path

### For Beginners

1. **Start with hw-function**
   - Simplest example
   - Learn basic Function-Streamlit pattern
   - Understand request/response flow
   - See real-time logs and status

2. **Then explore hw-neat**
   - More complex data modeling
   - Learn NEAT workflow
   - Understand data model deployment
   - Practice CRUD operations

### For Experienced Developers

Both modules together demonstrate:
- Complete application development patterns
- Data modeling best practices
- Testing and validation strategies
- Production-ready code structure

## 🎓 What You'll Learn

### From hw-function Module

- ✅ Creating Cognite Functions
- ✅ Calling Functions from Streamlit
- ✅ Handling asynchronous execution
- ✅ Displaying real-time status and logs
- ✅ Error handling and user feedback
- ✅ Structured response formats

### From hw-neat Module

- ✅ Designing data models in Excel
- ✅ Generating CDF-compatible YAML
- ✅ Deploying data models to CDF
- ✅ Building CRUD interfaces
- ✅ Testing data model implementations
- ✅ Managing sample data

## 🔧 Configuration

### Environment Variables Required

```bash
# CDF Connection
export CDF_PROJECT=your-project
export CDF_CLUSTER=your-cluster

# Authentication
export IDP_CLIENT_ID=your-client-id
export IDP_CLIENT_SECRET=your-client-secret
export IDP_SCOPES=your-scopes
export IDP_TENANT_ID=your-tenant-id
export IDP_TOKEN_URL=your-token-url

# Functions
export FUNCTION_CLIENT_ID=your-function-client-id
export FUNCTION_CLIENT_SECRET=your-function-client-secret

# User Identity
export USER_IDENTIFIER=your-email@example.com
export SUPERUSER_SOURCEID_ENV=your-source-id
```

### Configuration Files

- **`config.all-hw.yaml`**: Deploys all Hello World modules together
- **`config.hw-function.yaml`**: Deploys only the Function demo
- **`config.hw-neat.yaml`**: Deploys only the NEAT demo

## 📁 Project Structure

```
cognite-quickstart/
├── config.all-hw.yaml           # Configuration for all Hello World modules
├── config.hw-function.yaml      # Configuration for Function module only
├── config.hw-neat.yaml          # Configuration for NEAT module only
├── readme.hw-all.md             # This file
├── readme.hw-function.md        # Function module documentation
├── readme.hw-neat.md            # NEAT module documentation
├── docs/
│   └── requirements.hw.md       # Complete requirements and checklist
└── modules/
    ├── hw-function/             # Function + Streamlit demo
    │   ├── functions/
    │   │   └── hello-world-function/
    │   │       └── handler.py
    │   └── streamlit/
    │       └── hello-world/
    │           └── main.py
    └── hw-neat/                 # NEAT data modeling demo
        ├── data_models/
        │   ├── HWNeatBasic.xlsx # Excel source (manually maintained)
        │   └── data_models/     # Generated YAML files
        ├── generate_edm_yaml_files.py
        ├── test_neat_data_model.py
        └── streamlit/
            └── hw-neat/
                └── main.py
```

## 🎯 Use Cases

### Educational

- **Training**: Onboard new developers to CDF development
- **Workshops**: Hands-on exercises for learning patterns
- **Reference**: Template code for common scenarios

### Development

- **Prototyping**: Quick start for new projects
- **Testing**: Validate deployment pipelines
- **Patterns**: Reference implementations for best practices

### Production

- **Templates**: Starting point for real applications
- **Patterns**: Proven approaches for common needs
- **Structure**: Module organization examples

## ✅ Verification

After deployment, verify everything works:

### 1. Check Deployed Resources

```bash
# List deployed Functions
cdf functions list

# List deployed Streamlit apps
cdf streamlit list

# List deployed data models
cdf data-models list
```

### 2. Test Function Module

1. Open "Hello World Function Demo" in CDF
2. Enter a name
3. Click "Call Hello World Function"
4. Verify you see:
   - ✅ Success message
   - ✅ Greeting response
   - ✅ Function logs
   - ✅ Metadata

### 3. Test NEAT Module

1. Open "Hello World NEAT" app in CDF
2. Try creating a new instance
3. View existing instances
4. Verify data model is deployed:
   ```bash
   # Check space exists
   cdf spaces list | grep hw-neat
   
   # Check data model exists
   cdf data-models list | grep HWNeatDM
   ```

## 🐛 Troubleshooting

### Deployment Fails

```bash
# Check build directory
ls -la build/

# Verbose deployment
cdf deploy --config config.all-hw.yaml -v

# Dry run first
cdf deploy --config config.all-hw.yaml --dry-run
```

### Function Not Working

1. Check function exists: Navigate to CDF → Functions
2. Check logs: Click on function → View logs
3. Verify authentication is configured

### Streamlit App Issues

1. Check app status: CDF → Streamlit
2. View app logs: Click on app → Logs
3. Verify data model is deployed (for NEAT app)

### NEAT Generation Issues

```bash
# Check NEAT installation
pip show cognite-neat

# Test NEAT import
python -c "import cognite.neat; print('NEAT OK')"

# Regenerate YAML
cd modules/hw-neat
python generate_edm_yaml_files.py
```

## 🔄 Update Workflow

### When to Regenerate NEAT YAML

If you modify `HWNeatBasic.xlsx`:

```bash
cd modules/hw-neat
python generate_edm_yaml_files.py
cdf build --config config.hw-neat.yaml
cdf deploy --config config.hw-neat.yaml
```

### When to Update Function Code

If you modify `handler.py`:

```bash
cdf build --config config.hw-function.yaml
cdf deploy --config config.hw-function.yaml
```

## 📊 Module Comparison

| Feature | hw-function | hw-neat |
|---------|-------------|---------|
| **Complexity** | Simple | Moderate |
| **Components** | Function + Streamlit | Data Model + Streamlit |
| **Use Case** | Function integration | Data modeling |
| **Prerequisites** | None | NEAT installed |
| **Time to Deploy** | 5 minutes | 10 minutes |
| **Best For** | Learning Functions | Learning data models |

## 🎉 Success Criteria

Your Hello World deployment is successful when:

### hw-function Module
- ✅ Function deploys and appears in CDF
- ✅ Streamlit app loads in CDF
- ✅ Function call completes successfully
- ✅ Response displays with greeting
- ✅ Logs show function execution

### hw-neat Module
- ✅ Data model deploys to CDF
- ✅ Space, container, and views created
- ✅ Streamlit app loads
- ✅ Can create new instances
- ✅ Can view and manage data
- ✅ Tests pass successfully

## 🚀 Next Steps

After mastering these Hello World modules:

1. **Extend the Examples**
   - Add more complex logic to functions
   - Enhance data models with relationships
   - Create more sophisticated UIs

2. **Build Real Applications**
   - Apply patterns to real use cases
   - Integrate with your data sources
   - Deploy to production

3. **Explore Advanced Features**
   - Scheduled functions
   - Data model transformations
   - Advanced Streamlit components
   - Integration with external systems

## 📖 Additional Resources

- **Cognite Developer Portal**: [developer.cognite.com](https://developer.cognite.com)
- **NEAT Documentation**: [cognite-neat.readthedocs-hosted.com](https://cognite-neat.readthedocs-hosted.com)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **CDF Toolkit**: [CDF Toolkit Guide](https://developer.cognite.com/dev/guides/toolkit/)

## 💬 Support

For questions or issues:

1. Check module-specific README files
2. Review `docs/requirements.hw.md` for detailed requirements
3. Consult Cognite Developer Portal
4. Review function logs in CDF UI

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Modules Included**: hw-function, hw-neat  
**Compatibility**: CDF Toolkit 1.x, Python 3.11, Streamlit 1.28+

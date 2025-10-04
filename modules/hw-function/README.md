# Hello World Function + Streamlit Demo

This module demonstrates how a Cognite Function and Streamlit app work together.

## Components

### 1. Cognite Function (`hello-world-function`)
- **Location**: `functions/hello-world-function/handler.py`
- **Purpose**: Simple function that receives a name and returns a greeting
- **Input**: `{"name": "Your Name"}`
- **Output**: JSON response with greeting, timestamp, and metadata

### 2. Streamlit App (`hello-world-streamlit`)
- **Location**: `streamlit/hello-world/main.py`
- **Purpose**: Web interface to call the function and display results
- **Features**:
  - Input form for name
  - Function call button
  - Real-time status updates
  - Live function logs
  - Full response display

## How It Works

```
User Input (Streamlit)
       ↓
  Call Function
       ↓
Cognite Function Executes
       ↓
  Return Response
       ↓
Display Results (Streamlit)
```

## Usage

### Deploy the Module
```bash
cdf build modules/hw-function
cdf deploy --interactive
```

### Access the Streamlit App
1. Navigate to your Cognite project
2. Go to Streamlit apps
3. Open "Hello World Function Demo"
4. Enter a name and click "Call Hello World Function"

## Pattern Overview

This module demonstrates the standard pattern for Function-Streamlit integration:

1. **Function Handler** (`handler.py`):
   - Receives `client` (CogniteClient) and `data` (input parameters)
   - Processes the request
   - Returns structured JSON response
   - Logs progress to function logs

2. **Streamlit App** (`main.py`):
   - Uses `CogniteClient()` to connect
   - Calls function with `client.functions.call()`
   - Polls for status with `client.functions.calls.retrieve()`
   - Gets logs with `client.functions.calls.get_logs()`
   - Displays response to user

## Key Features

- ✅ Simple, clear example
- ✅ Full request/response cycle
- ✅ Real-time status updates
- ✅ Live function logs
- ✅ Error handling
- ✅ Structured response format

## Files

```
modules/hw-function/
├── module.toml                              # Module metadata
├── README.md                                # This file
├── data_sets/
│   └── hw-function-dataset.DataSet.yaml     # Dataset definition
├── functions/
│   ├── hello-world-function.Function.yaml   # Function configuration
│   └── hello-world-function/
│       ├── handler.py                       # Function code
│       └── requirements.txt                 # Function dependencies
└── streamlit/
    ├── HelloWorld.Streamlit.yaml            # Streamlit app configuration
    └── hello-world/
        ├── main.py                          # Streamlit app code
        └── requirements.txt                 # Streamlit dependencies
```

## Extending This Pattern

Use this as a template for more complex function-streamlit integrations:

1. **More Complex Functions**:
   - Add data processing
   - Call other CDF APIs
   - Perform calculations
   - Run workflows

2. **Enhanced Streamlit UI**:
   - Multiple input forms
   - Data visualization
   - File uploads
   - Advanced error handling

3. **Real-World Use Cases**:
   - Data validation
   - Report generation
   - Batch processing
   - API integrations

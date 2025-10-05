# Hello World Function Demo

A simple demonstration of how Cognite Functions and Streamlit apps work together to create interactive data applications.

## 🎯 Overview

This module demonstrates the fundamental pattern for integrating Cognite Functions with Streamlit:
- **User Input**: Collect data through a Streamlit web interface
- **Function Call**: Invoke a Cognite Function with the input data
- **Processing**: Function executes and returns structured results
- **Display**: Streamlit shows the full response with logs and metadata

## 📁 Module Structure

```
modules/hw-function/
├── module.toml                              # Module metadata
├── README.md                                # Module documentation
├── data_sets/
│   └── hw-function-dataset.DataSet.yaml     # Dataset definition
├── functions/
│   ├── hello-world-function.Function.yaml   # Function configuration
│   └── hello-world-function/
│       ├── handler.py                       # Function code (handle function)
│       └── requirements.txt                 # Function dependencies
└── streamlit/
    ├── HelloWorld.Streamlit.yaml            # Streamlit app configuration
    └── hello-world/
        ├── main.py                          # Streamlit app code
        └── requirements.txt                 # Streamlit dependencies
```

## 🚀 Quick Start

### 1. Deploy the Module

```bash
# Build the module
cdf build --config config.hw-function.yaml

# Deploy to CDF
cdf deploy --config config.hw-function.yaml
```

### 2. Access the Streamlit App

1. Navigate to your Cognite project
2. Go to **Streamlit** apps section
3. Open **"Hello World Function Demo"**
4. Enter a name and click **"Call Hello World Function"**

## 💡 How It Works

### Function Handler (`handler.py`)

```python
def handle(client, data):
    """
    Function receives:
    - client: CogniteClient instance
    - data: Input dictionary (e.g., {"name": "World"})
    
    Function returns:
    - JSON response with greeting, timestamp, and metadata
    """
    name = data.get("name", "World")
    return {
        "greeting": f"Hello, {name}!",
        "message": "Response from Cognite Function",
        "timestamp": datetime.now().isoformat(),
        "metadata": {...}
    }
```

### Streamlit App (`main.py`)

```python
# 1. Get cached CogniteClient
client = get_cognite_client()

# 2. Call the function
call_result = client.functions.call(
    external_id="hello-world-function",
    data={"name": name}
)

# 3. Wait for completion
call_status = client.functions.calls.retrieve(
    function_external_id="hello-world-function",
    call_id=call_result.id
)

# 4. Get response and display
response = result.get_response()
st.success(response["greeting"])
```

## 🔑 Key Concepts

### 1. Function Configuration
- **Runtime**: Python 3.11
- **Resources**: 0.25 CPU, 0.5 GB memory (minimal for hello world)
- **Handler**: The `handle(client, data)` function is the entry point

### 2. Data Flow
```
User Input (Streamlit)
       ↓
  Call Function (client.functions.call)
       ↓
Function Executes (handle function)
       ↓
  Return Response (JSON)
       ↓
Display Results (Streamlit UI)
```

### 3. Response Format
The function returns structured JSON:
```json
{
  "greeting": "Hello, World!",
  "message": "This is a response from a Cognite Function",
  "timestamp": "2025-10-04T10:30:00",
  "metadata": {
    "python_version": "3.11.x",
    "project": "your-project",
    "function_id": "hello-world-function"
  },
  "success": true
}
```

## 📊 Features Demonstrated

### Function Features
- ✅ Receiving input parameters
- ✅ Accessing CogniteClient in functions
- ✅ Logging to function logs
- ✅ Returning structured JSON responses
- ✅ Including metadata and timestamps

### Streamlit Features
- ✅ Cached CogniteClient for performance
- ✅ Interactive user input forms
- ✅ Function call with error handling
- ✅ Real-time status updates
- ✅ Live function logs display
- ✅ Formatted response visualization
- ✅ Collapsible sections for details

## 🎓 Learning Objectives

After exploring this module, you'll understand:

1. **Function Basics**
   - How to structure a Cognite Function
   - The `handle(client, data)` function signature
   - How to return JSON responses

2. **Streamlit Integration**
   - How to call functions from Streamlit
   - How to poll for function status
   - How to retrieve and display results

3. **Best Practices**
   - Caching CogniteClient for performance
   - Structured error handling
   - User-friendly status feedback
   - Comprehensive logging

## 🔧 Customization Examples

### Extend the Function

Add more processing to the handler:

```python
def handle(client, data):
    name = data.get("name", "World")
    language = data.get("language", "en")
    
    greetings = {
        "en": f"Hello, {name}!",
        "es": f"¡Hola, {name}!",
        "fr": f"Bonjour, {name}!",
        "de": f"Guten Tag, {name}!"
    }
    
    return {
        "greeting": greetings.get(language, greetings["en"]),
        "language": language,
        "success": True
    }
```

### Enhance the Streamlit UI

Add more input fields:

```python
name = st.text_input("Enter your name:", value="World")
language = st.selectbox("Choose language:", 
                        options=["en", "es", "fr", "de"],
                        format_func=lambda x: {
                            "en": "English",
                            "es": "Spanish", 
                            "fr": "French",
                            "de": "German"
                        }[x])

if st.button("Call Function"):
    data = {"name": name, "language": language}
    # ... call function with data
```

## 🐛 Troubleshooting

### Function Not Found
```
Error: Function 'hello-world-function' not found
```
**Solution**: Ensure you've deployed the module:
```bash
cdf deploy --config config.hw-function.yaml
```

### Function Call Timeout
```
Error: Function call timed out
```
**Solution**: Check function logs in CDF UI under Functions → hello-world-function

### Connection Issues
```
Error: Failed to connect to Cognite
```
**Solution**: Verify your authentication is configured correctly

## 📚 Next Steps

Once you understand this pattern, explore:

1. **More Complex Functions**
   - Process CDF data (time series, assets, files)
   - Call external APIs
   - Perform calculations and analytics

2. **Advanced Streamlit**
   - Add data visualization (charts, graphs)
   - Implement file uploads
   - Create multi-page apps

3. **Real-World Use Cases**
   - Data validation and quality checks
   - Report generation
   - Batch processing workflows
   - Integration with external systems

## 📖 Related Documentation

- **Module Documentation**: `modules/hw-function/README.md`
- **Cognite Functions**: [Functions Documentation](https://developer.cognite.com/dev/concepts/resource_types/functions/)
- **Streamlit**: [Streamlit Documentation](https://docs.streamlit.io/)
- **CDF Toolkit**: [Toolkit Documentation](https://developer.cognite.com/dev/guides/toolkit/)

## ✅ Success Checklist

Your deployment is successful when:

- ✅ Function deploys without errors
- ✅ Streamlit app appears in CDF UI
- ✅ App loads and connects to project
- ✅ Entering a name and clicking button triggers function
- ✅ Response displays with greeting message
- ✅ Function logs are visible
- ✅ No errors in console or logs

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Compatibility**: CDF Toolkit 1.x, Python 3.11, Streamlit 1.28+

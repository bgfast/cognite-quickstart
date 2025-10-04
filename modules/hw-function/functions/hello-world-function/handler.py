"""
Hello World Cognite Function
Demonstrates how a Cognite Function works with Streamlit
"""

def handle(client, data):
    """
    Simple hello world function that returns a greeting.
    
    Args:
        client: CogniteClient instance (automatically provided)
        data: Input data from function call (dict with optional 'name' field)
        
    Returns:
        dict: Response with greeting message and metadata
    """
    from datetime import datetime
    import sys
    
    # Get name from input data, or use default
    name = data.get("name", "World") if isinstance(data, dict) else "World"
    
    # Create response
    response = {
        "greeting": f"Hello, {name}!",
        "message": "This is a response from a Cognite Function",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "python_version": sys.version,
            "input_data": data,
            "project": client.config.project,
            "function_id": "hello-world-function"
        },
        "success": True
    }
    
    # Print to function logs
    print(f"🎉 Hello World Function called!")
    print(f"👤 Greeting: {response['greeting']}")
    print(f"📊 Project: {client.config.project}")
    print(f"✅ Response prepared successfully")
    
    return response

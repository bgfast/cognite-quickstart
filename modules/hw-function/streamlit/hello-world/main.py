#!/usr/bin/env python3
"""
Hello World Streamlit App
Demonstrates how to call a Cognite Function from Streamlit and display the response
"""

import streamlit as st
import time
from datetime import datetime

VERSION = "1.0.0"


@st.cache_resource
def get_cognite_client():
    """Initialize and cache CogniteClient"""
    from cognite.client import CogniteClient
    return CogniteClient()


def call_hello_world_function():
    """Call the hello-world function and display results"""
    st.header("👋 Hello World Function Demo")
    st.write("This demo shows how a Streamlit app can call a Cognite Function and display the full response.")
    
    # Input section
    st.subheader("📝 Input")
    name = st.text_input("Enter your name:", value="World", placeholder="Your name here...")
    
    # Call function button
    if st.button("🚀 Call Hello World Function", type="primary"):
        if not name:
            st.error("Please enter a name")
            return
        
        try:
            # Get cached client
            with st.spinner("🔌 Connecting to Cognite..."):
                client = get_cognite_client()
            
            st.success(f"✅ Connected to project: {client.config.project}")
            
            # Call the function
            with st.spinner(f"📞 Calling function with name='{name}'..."):
                call_result = client.functions.call(
                    external_id="hello-world-function",
                    data={"name": name}
                )
            
            st.success(f"✅ Function called! Call ID: {call_result.id}")
            
            # Wait for result with progress
            st.subheader("⏳ Waiting for Response")
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            logs_container = st.container()
            
            max_wait = 60  # 1 minute
            wait_time = 0
            
            while wait_time < max_wait:
                # Get function call status
                call_status = client.functions.calls.retrieve(
                    function_external_id="hello-world-function",
                    call_id=call_result.id
                )
                
                progress = min(wait_time / max_wait, 0.95)
                progress_bar.progress(progress)
                status_placeholder.text(f"Status: {call_status.status} ({wait_time}s)")
                
                # Get logs
                try:
                    logs = client.functions.calls.get_logs(
                        function_external_id="hello-world-function",
                        call_id=call_result.id
                    )
                    
                    if logs:
                        with logs_container:
                            st.subheader("📋 Function Logs")
                            for log in logs:
                                log_msg = log.message if hasattr(log, 'message') else str(log)
                                st.text(log_msg)
                except Exception as log_error:
                    # Logs might not be available yet
                    pass
                
                if call_status.status == "Completed":
                    progress_bar.progress(1.0)
                    status_placeholder.text("✅ Function completed!")
                    
                    # Get the result
                    result = client.functions.calls.retrieve(
                        function_external_id="hello-world-function",
                        call_id=call_result.id
                    )
                    
                    # Display results
                    st.subheader("🎉 Function Response")
                    
                    # Get response data
                    response_data = None
                    if hasattr(result, 'get_response'):
                        response_data = result.get_response()
                    elif hasattr(result, 'response'):
                        response_data = result.response
                    
                    if response_data:
                        # Display the greeting prominently
                        if 'greeting' in response_data:
                            st.success(f"### {response_data['greeting']}")
                        
                        if 'message' in response_data:
                            st.info(response_data['message'])
                        
                        # Show metadata
                        if 'metadata' in response_data:
                            with st.expander("🔍 Response Metadata"):
                                metadata = response_data['metadata']
                                st.write(f"**Project**: {metadata.get('project', 'N/A')}")
                                st.write(f"**Function**: {metadata.get('function_id', 'N/A')}")
                                st.write(f"**Python Version**: {metadata.get('python_version', 'N/A')[:50]}...")
                        
                        # Show full response
                        with st.expander("📦 Full Response Data"):
                            st.json(response_data)
                        
                        st.balloons()  # Celebrate success!
                    else:
                        st.error("❌ No response data received")
                    
                    break
                    
                elif call_status.status == "Failed":
                    st.error(f"❌ Function failed: {call_status}")
                    break
                
                # Wait before checking again
                time.sleep(2)
                wait_time += 2
            
            if wait_time >= max_wait:
                st.error("⏰ Function call timed out")
                
        except Exception as e:
            st.error(f"❌ Error calling function: {e}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())


def show_info():
    """Show information about the demo"""
    st.sidebar.header("ℹ️ About")
    st.sidebar.write(f"**Version**: {VERSION}")
    st.sidebar.write(f"**Function**: hello-world-function")
    st.sidebar.write(f"**Runtime**: Python 3.11")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 How It Works")
    st.sidebar.write("""
    1. **User Input**: Enter a name in the Streamlit app
    2. **Function Call**: App calls the Cognite Function with the name
    3. **Processing**: Function generates a greeting message
    4. **Response**: Function returns structured data
    5. **Display**: Streamlit shows the full response
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Components")
    st.sidebar.write("""
    - **Cognite Function**: `hello-world-function`
    - **Handler**: Simple Python function
    - **Input**: Name from Streamlit form
    - **Output**: JSON response with greeting
    """)


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Hello World Function Demo",
        page_icon="👋",
        layout="wide"
    )
    
    # Show sidebar info
    show_info()
    
    # Main content
    st.title("👋 Hello World: Function + Streamlit")
    st.caption(f"Demo of Cognite Function and Streamlit integration • Version {VERSION}")
    
    st.markdown("---")
    
    # Call function interface
    call_hello_world_function()
    
    # Footer
    st.markdown("---")
    st.caption("💡 **Pattern**: This demonstrates the basic pattern for calling Cognite Functions from Streamlit")


if __name__ == "__main__":
    main()

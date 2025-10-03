#!/usr/bin/env python3
"""
NEAT Data Writer - Streamlit App

This Streamlit app provides an interface for writing data to the NEAT Basic data model.
Users can create and manage NeatBasic instances through a user-friendly web interface.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIError

# Import View class from local data_modeling module
from data_modeling import View

# Initialize NEAT view wrapper for Data Model integration
@st.cache_resource
def get_neat_view(_client):
    """Initialize and return NeatBasic view wrapper."""
    try:
        return View(_client, space="EDM-COR-ALL-NEAT", external_id="NeatBasic")
    except Exception as e:
        st.error(f"Failed to initialize NEAT view: {str(e)}")
        return None

@st.cache_resource
def get_client():
    """Get or create CogniteClient"""
    try:
        # Try SaaS connection first (no parameters needed in SaaS)
        client = CogniteClient()
        return client
    except Exception as e:
        try:
            # Fallback to interactive OAuth for local development
            client = CogniteClient.default_oauth_interactive(
                project=st.secrets.get("CDF_PROJECT", "bgfast"),
                cdf_cluster=st.secrets.get("CDF_CLUSTER", "bluefield")
            )
            return client
        except Exception as e2:
            st.error(f"Failed to connect to CDF: {e2}")
            st.stop()


class NeatDataWriter:
    """Handler for writing data to NEAT Basic data model"""
    
    def __init__(self, client: CogniteClient, neat_view: View):
        """Initialize the data writer"""
        self.client = client
        self.neat_view = neat_view
        self.space_id = "EDM-COR-ALL-NEAT"  # From NEAT-generated space
    
    def create_neat_instance(self, external_id: str, properties: Dict[str, Any]) -> bool:
        """Create a new NeatBasic instance"""
        try:
            self.neat_view.upsert_instance(
                external_id=external_id,
                properties=properties,
                space=self.space_id
            )
            return True
            
        except Exception as e:
            st.error(f"Failed to create instance: {e}")
            return False
    
    def get_existing_instances(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get existing NeatBasic instances"""
        try:
            instances = self.neat_view.list_instances(space=self.space_id, limit=limit)
            return instances
            
        except Exception as e:
            st.error(f"Failed to fetch instances: {e}")
            return []


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="NEAT Data Writer v1.01",
        page_icon="✏️",
        layout="wide"
    )
    
    st.title("✏️ NEAT Data Writer")
    st.markdown("Create and manage data in your NEAT Basic data model")
    st.caption("Version 1.01 - Enhanced with proper data modeling patterns")
    
    # Initialize client and view
    client = get_client()
    neat_view = get_neat_view(_client=client)
    
    if not neat_view:
        st.error("❌ Failed to initialize NEAT view. Please check your data model deployment.")
        st.stop()
    
    # Initialize data writer
    writer = NeatDataWriter(client, neat_view)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    mode = st.sidebar.radio(
        "Select Mode:",
        ["Create New Instance", "View Existing Instances", "Bulk Import"]
    )
    
    if mode == "Create New Instance":
        create_instance_form(writer)
    elif mode == "View Existing Instances":
        view_existing_instances(writer)
    elif mode == "Bulk Import":
        bulk_import_form(writer)


def create_instance_form(writer: NeatDataWriter):
    """Form for creating a single instance"""
    st.header("🆕 Create New NEAT Instance")
    
    with st.form("create_instance"):
        col1, col2 = st.columns(2)
        
        with col1:
            external_id = st.text_input(
                "External ID",
                help="Unique identifier for this instance",
                placeholder="e.g., neat_item_001"
            )
            
        with col2:
            new_string = st.text_input(
                "New String",
                help="String value for the newString property",
                placeholder="e.g., Sample data value"
            )
        
        # Additional metadata
        st.subheader("Metadata")
        col3, col4 = st.columns(2)
        
        with col3:
            created_by = st.text_input(
                "Created By",
                value=st.session_state.get("user_name", "streamlit_user"),
                help="Who is creating this instance"
            )
            
        with col4:
            tags = st.text_input(
                "Tags",
                help="Comma-separated tags",
                placeholder="e.g., test, sample, demo"
            )
        
        notes = st.text_area(
            "Notes",
            help="Additional notes about this instance",
            placeholder="Optional notes..."
        )
        
        submitted = st.form_submit_button("Create Instance", type="primary")
        
        if submitted:
            if not external_id:
                st.error("External ID is required")
                return
                
            if not new_string:
                st.error("New String is required")
                return
            
            # Prepare properties
            properties = {
                "newString": new_string
            }
            
            # Add metadata as additional properties if they exist in the model
            # For now, we'll just use the core property
            
            with st.spinner("Creating instance..."):
                success = writer.create_neat_instance(external_id, properties)
                
            if success:
                st.success(f"✅ Successfully created instance: {external_id}")
                st.balloons()
                
                # Show created instance details
                st.info(f"""
                **Created Instance:**
                - External ID: `{external_id}`
                - New String: `{new_string}`
                - Created By: `{created_by}`
                - Tags: `{tags}`
                """)
            else:
                st.error("❌ Failed to create instance")


def view_existing_instances(writer: NeatDataWriter):
    """View existing instances"""
    st.header("📋 Existing NEAT Instances")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        limit = st.number_input("Limit", min_value=1, max_value=1000, value=50)
        refresh = st.button("🔄 Refresh", type="secondary")
    
    if refresh or "instances_data" not in st.session_state:
        with st.spinner("Loading instances..."):
            instances = writer.get_existing_instances(limit)
            st.session_state.instances_data = instances
    
    instances = st.session_state.get("instances_data", [])
    
    if instances:
        st.success(f"Found {len(instances)} instances")
        
        # Convert to DataFrame for display
        df_data = []
        for instance in instances:
            df_data.append({
                'External ID': instance.get('externalId', 'N/A'),
                'New String': instance.get('newString', 'N/A'),
            })
        
        df = pd.DataFrame(df_data)
        
        # Display with search/filter
        search_term = st.text_input("🔍 Search instances", placeholder="Search by External ID or New String...")
        
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            df = df[mask]
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"neat_instances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No instances found. Create some instances first!")


def bulk_import_form(writer: NeatDataWriter):
    """Form for bulk importing instances"""
    st.header("📤 Bulk Import NEAT Instances")
    
    st.markdown("""
    Upload a CSV file with the following columns:
    - `external_id`: Unique identifier for each instance
    - `new_string`: String value for the newString property
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type="csv",
        help="Upload a CSV file with external_id and new_string columns"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate columns
            required_columns = ['external_id', 'new_string']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {missing_columns}")
                return
            
            st.success(f"✅ File loaded successfully! Found {len(df)} rows")
            
            # Preview data
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Import options
            col1, col2 = st.columns(2)
            
            with col1:
                batch_size = st.number_input("Batch Size", min_value=1, max_value=100, value=10)
                
            with col2:
                skip_errors = st.checkbox("Skip errors and continue", value=True)
            
            if st.button("🚀 Start Import", type="primary"):
                import_progress = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                error_count = 0
                errors = []
                
                for i, row in df.iterrows():
                    try:
                        external_id = str(row['external_id'])
                        new_string = str(row['new_string'])
                        
                        properties = {"newString": new_string}
                        
                        success = writer.create_neat_instance(external_id, properties)
                        
                        if success:
                            success_count += 1
                        else:
                            error_count += 1
                            errors.append(f"Row {i+1}: Failed to create {external_id}")
                            
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {i+1}: {str(e)}")
                        
                        if not skip_errors:
                            st.error(f"Import stopped at row {i+1}: {e}")
                            break
                    
                    # Update progress
                    progress = (i + 1) / len(df)
                    import_progress.progress(progress)
                    status_text.text(f"Processing row {i+1}/{len(df)} - Success: {success_count}, Errors: {error_count}")
                    
                    # Small delay to avoid overwhelming the API
                    time.sleep(0.1)
                
                # Final results
                st.success(f"✅ Import completed! Success: {success_count}, Errors: {error_count}")
                
                if errors:
                    st.error("Errors encountered:")
                    for error in errors[:10]:  # Show first 10 errors
                        st.text(error)
                    
                    if len(errors) > 10:
                        st.text(f"... and {len(errors) - 10} more errors")
                
        except Exception as e:
            st.error(f"Failed to process file: {e}")


if __name__ == "__main__":
    main()

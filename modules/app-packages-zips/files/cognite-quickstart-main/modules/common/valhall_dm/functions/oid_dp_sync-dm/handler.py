import datetime
from datetime import timedelta

from cognite.client.credentials import OAuthClientCredentials
from cognite.client import CogniteClient, ClientConfig
from datetime import datetime, timedelta
import requests

def get_secret(api_url, secret_id):
    # Set the headers
    headers = {
        'Accept': 'application/json, text/plain, */*'
    }

    # Make the API request
    try:
        response = requests.get(f"{api_url}?id={secret_id}", headers=headers)
        
        # Raise an error if the request was not successful
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the secretText from the response
        secret_text = data.get("secretText")
        return secret_text
    except requests.exceptions.RequestException as e:
        # Print out the error if the request fails
        print(f"Error fetching secret: {e}")
        return None

def create_cognite_client(tenant_id, client_id, client_secret, cdf_cluster, project, app_name):
    base_url = f"https://{cdf_cluster}.cognitedata.com"
    credentials = OAuthClientCredentials(
        token_url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token", 
        client_id=client_id, 
        scopes=[f"{base_url}/.default"], 
        client_secret=client_secret
    )
    config = ClientConfig(
        client_name=app_name,
        project=project,
        base_url=base_url,
        credentials=credentials,
    )
    return CogniteClient(config)

# Get list of desired time series from a specific CDF
def get_tag_list(cognite_client, external_id_prefix, limit):
    ext2id = {}
    ts = cognite_client.time_series.list(limit=None)
    for t in ts:
        if t.instance_id != None and t.instance_id.space == "valhall-tags":
            ext2id[t.instance_id.external_id] = t.id
    # Return dict of external_id to id
    return ext2id

def sync_tag_data(sourceClient, destClient, tag_list):
    one_month_ago = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
    for ext_id, dest_id in tag_list.items():  # Iterate over tag_list dictionary
        try:
            # For specified destination id, retrieve the latest timestamp from the destination system
            latest_data = destClient.time_series.data.retrieve_latest(id=dest_id)

            # Check if a timestamp was returned; if not, set to one month ago
            if latest_data and latest_data.timestamp:
                latest_timestamp = latest_data.timestamp[0]  # In milliseconds
            else:
                latest_timestamp = one_month_ago

            # Check if the latest timestamp is more than a month in the past
            if latest_timestamp < one_month_ago:
                latest_timestamp = one_month_ago  # Set to one month ago if too old
        except Exception as e:
            # If the tag doesn't exist or retrieval fails, log it and skip to the next tag
            print(f"Error retrieving latest timestamp for tag {dest_id} in destination system. Skipping. Exception: {e}")
            continue

        try:
            # Retrieve data from the source system starting from the latest timestamp
            new_datapoints = sourceClient.time_series.data.retrieve(
                external_id=ext_id,
                start=latest_timestamp
            )
            if not new_datapoints:
                print(f"No datapoints for {ext_id} - moving on.")
                continue
        except Exception as e:
            print(f"Error retrieving data for tag {ext_id} from source system. Skipping. Exception: {e}")
            continue

        try:
            # Insert the new data into the destination system using the destination id
            destClient.time_series.data.insert(
                datapoints=new_datapoints,
                id=dest_id  # Use the destination id for insertion
            )
            print(f"Data successfully synced for tag {ext_id} (dest id: {dest_id}).")
        except Exception as e:
            print(f"Error inserting data for tag {ext_id} (dest id: {dest_id}) into destination system. Exception: {e}")

def backfill_data(sourceClient, destClient, tag_list, backfillStartTime, backfillEndTime, granularity=None):
    for ext_id, dest_id in tag_list.items():
        try:
            retrieve_params = {
                "external_id": ext_id,
                "start": backfillStartTime,
                "end": backfillEndTime
            }
            if granularity:
                retrieve_params.update({"aggregates": "interpolation", "granularity": granularity})
            
            new_datapoints = sourceClient.time_series.data.retrieve(**retrieve_params)
            
            if not new_datapoints:
                print(f"No datapoints for {ext_id} - moving on.")
                continue

            if granularity:  # Aggregates are used
                values = getattr(new_datapoints, 'interpolation', None)
            else:  # Raw data
                values = getattr(new_datapoints, 'value', None)

            if hasattr(new_datapoints, 'timestamp') and values is not None:
                formatted_datapoints = [
                    (ts, val) 
                    for ts, val in zip(new_datapoints.timestamp, values)
                    if val is not None
                ]
            else:
                formatted_datapoints = []  # Avoid insertion if data is invalid    
                
        except Exception as e:
            print(f"Error retrieving data for tag {ext_id} from source system. Skipping. Exception: {e}")
            continue

        try:
            destClient.time_series.data.insert(
                datapoints=formatted_datapoints,
                id=dest_id
            )
            print(f"Data successfully synced for tag {ext_id} (dest id: {dest_id}).")
        except Exception as e:
            print(f"Error inserting data for tag {ext_id} (dest id: {dest_id}) into destination system. Exception: {e}")

def handle(client, data, secrets=None, function_call_info=None):
    """Handler Function to be Run/Deployed
    Args:
        client : Cognite Client (not needed, it's available to it, when deployed)
        data : data needed by function
        secrets : Any secrets it needs
        function_call_info : any other information about function

    Returns:
        response : response or result from the function
    """

    api_url = "https://testclientsecret.azurewebsites.net/secret/"
    secret_id = "OID_API"
    oid_secret = get_secret(api_url, secret_id)

    # Create client that pulls from source CDF
    c_source = create_cognite_client(
        tenant_id="48d5043c-cf70-4c49-881c-c638f5796997",
        client_id="1b90ede3-271e-401b-81a0-a4d52bea3273",
        client_secret=oid_secret,
        cdf_cluster="api",
        project="publicdata",
        app_name="OID-Api"
    )

    tag_dict = get_tag_list(client, external_id_prefix="pi:", limit=500)

    if not data:
        sync_tag_data(sourceClient=c_source, destClient=client, tag_list=tag_dict)
    elif "startTime" in data and "endTime" in data:
        granularity = data.get("granularity")  # Get granularity if present, otherwise None

        backfill_data(
            sourceClient=c_source,
            destClient=client,
            tag_list=tag_dict,
            backfillStartTime=data["startTime"],
            backfillEndTime=data["endTime"],
            granularity=granularity  # Pass granularity (None if not present)
        )
    else:
        print("Invalid inputs provided - must define startTime and endTime as integers, string, or datetime if you want to backfill data.")

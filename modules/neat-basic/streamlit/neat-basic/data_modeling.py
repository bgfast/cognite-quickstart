from cognite.client import CogniteClient
from cognite.client.data_classes.data_modeling import ViewId, NodeApply, NodeOrEdgeData
from cognite.client.data_classes.filters import Prefix, ContainsAny, Equals
from cognite.client.exceptions import CogniteAPIError

class View:
    """A wrapper class for Cognite Data Modeling Views to simplify common operations."""

    def __init__(self, client: CogniteClient, space: str, external_id: str):
        """
        Initialize the View wrapper.

        Args:
            client (CogniteClient): The Cognite client instance.
            space (str): The space of the view.
            external_id (str): The external ID of the view.
        """
        self.client = client
        self.space = space
        self.external_id = external_id

        # Get the latest version of the view
        view_id = ViewId(self.space, self.external_id)
        view_list = self.client.data_modeling.views.retrieve(view_id)
        if not view_list:
            raise ValueError(f"No view found with external_id {self.external_id} in space {self.space}")
        self.view = max(view_list, key=lambda v: v.created_time)
        self.version = self.view.version

    def get_properties(self):
        """Return a list of property names in the view."""
        return list(self.view.properties.keys())

    def get_instance(self, external_id: str, space: str):
        """
        Retrieve properties of a single instance.

        Args:
            external_id (str): External ID of the instance.
            space (str): Space of the instance.

        Returns:
            dict: Dictionary of properties, including 'externalId'.
        """
        result = self.client.data_modeling.instances.retrieve(nodes=[(space, external_id)], sources=[self.view.as_id()])
        
        if result.nodes:
            props = result.nodes[0].properties.get(self.view.as_id(), {})
            props["externalId"] = external_id
            return props
        return {}

    def search_instances(self, external_id_prefix: str, space: str):
        """
        Search for instances by external ID prefix.

        Args:
            external_id_prefix (str): Prefix to search for.
            space (str): Space to limit search to.

        Returns:
            list[tuple]: List of (space, external_id) tuples.
        """
        filter_ = Prefix(["node", "externalId"], external_id_prefix)
        result = self.client.data_modeling.instances.list(
            instance_type="node",
            filter=filter_,
            space=space,
            sources=[self.view.as_id()],
            limit=-1
        )
        return [(inst.space, inst.external_id) for inst in result]

    def list_instances(self, space: str, limit: int = 100):
        """
        List instances in the view.

        Args:
            space (str): Space to limit search to.
            limit (int): Maximum number of instances to return.

        Returns:
            list[dict]: List of instance dictionaries with properties.
        """
        result = self.client.data_modeling.instances.list(
            instance_type="node",
            space=space,
            sources=[self.view.as_id()],
            limit=limit
        )
        
        instances = []
        for inst in result:
            props = inst.properties.get(self.view.as_id(), {})
            props["externalId"] = inst.external_id
            props["space"] = inst.space
            instances.append(props)
        
        return instances

    def delete_instances(self, external_ids: list[str], space: str):
        """
        Delete multiple instances by external IDs.

        Args:
            external_ids (list[str]): External IDs of the instances to delete.
            space (str): Space of the instances.
        """
        if not external_ids:
            return
        nodes = [(space, external_id) for external_id in external_ids]
        self.client.data_modeling.instances.delete(nodes=nodes)

    def upsert_instance(self, external_id: str, properties: dict, space: str, clear_existing: bool = False):
        """
        Upsert an instance with given properties.

        Args:
            external_id (str): External ID of the instance.
            properties (dict): Properties to set.
            space (str): Space of the instance.
            clear_existing (bool): If True, clear existing properties before upsert.
        """
        if clear_existing:
            props = properties
        else:
            result = self.client.data_modeling.instances.retrieve(nodes=[(space, external_id)], sources=[self.view.as_id()])
            if result.nodes:
                current_props = result.nodes[0].properties.get(self.view.as_id(), {})
                current_props.update(properties)
                props = current_props
            else:
                props = properties
        
        node = NodeApply(
            space=space,
            external_id=external_id,
            sources=[NodeOrEdgeData(source=self.view.as_id(), properties=props)]
        )
        self.client.data_modeling.instances.apply(nodes=[node])

    def count_instances(self, space: str):
        """
        Count total instances in the view.

        Args:
            space (str): Space to count instances in.

        Returns:
            int: Number of instances.
        """
        result = self.client.data_modeling.instances.list(
            instance_type="node",
            space=space,
            sources=[self.view.as_id()],
            limit=1  # We just need to know if any exist
        )
        
        # For a proper count, we'd need to paginate through all results
        # This is a simplified version that gets a reasonable estimate
        total_result = self.client.data_modeling.instances.list(
            instance_type="node",
            space=space,
            sources=[self.view.as_id()],
            limit=-1  # Get all (be careful with large datasets)
        )
        
        return len(total_result)

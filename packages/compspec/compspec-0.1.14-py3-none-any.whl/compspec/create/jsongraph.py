__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2024, Vanessa Sochat"
__license__ = "MIT"


# A json graph is JGF or "json graph format"
# This is intended to create subsystems or similar for a scheduler

import json


class JsonGraph:
    def __init__(self, name):
        """
        Create a new json graph. This is intended to be used as a base class
        for child classes that generate JGF. They should implement generate()

        name:      should be the name of the subsystem (e.g., ior)
        subsystem: is the *type* of subsystem (e.g., io or spack)
        """
        # This is typically a subsystem or resource name
        self.name = name
        self.counter = 0
        self.nodes = {}
        self.edges = []
        self.metadata = {}

        # Keep track of count for each type
        self.resource_counts = {}

    def render(self):
        """
        Render serializes the dict to json
        """
        return json.dumps(self.to_dict(), indent=4)

    def to_dict(self, metadata=None):
        """
        Render generates the artifact, adding all unique schemas and compatibility sections
        """
        metadata = self.metadata or {}
        g = {"graph": {"nodes": self.nodes, "edges": self.edges}}
        if metadata:
            g["metadata"] = metadata
        return g

    @property
    def next_count(self):
        count = self.counter
        self.counter += 1
        return count

    def next_resource_count(self, name):
        """
        Get the next count for a resource type
        """
        if name not in self.resource_counts:
            self.resource_counts[name] = 0
        count = self.resource_counts[name]
        self.resource_counts[name] += 1
        return count

    def add_node(
        self,
        typ,
        parent=None,
        exclusive=False,
        size=1,
        rank=0,
        path=None,
        idx=None,
        count=None,
        attributes=None,
    ):
        """
        Add a node to the graph.
        """
        # Ensure the parent ends in trailing slash, if defined
        parent = parent or ""
        if parent != "" and not parent.endswith("/"):
            parent = f"{parent}/"

        # This is the global graph counter
        if idx is None:
            idx = self.next_count

        # This is the resource count
        if count is None:
            count = self.next_resource_count(typ)
        containment = {"paths": path}

        # The label is the subsystem name plus global identifier
        label = f"{typ}{idx}"

        # The containment also has the count of the resource
        if path is None:
            containment = {"paths": f"/{self.name}0/{parent}{typ}{count}"}
        metadata = {
            "type": typ,
            "basename": typ,
            # This is the count of the resource
            "name": f"{typ}{count}",
            # The id is the global graph id
            "id": idx,
            # Unique id within the resource?
            "uniq_id": count,
            "containment": containment,
            "size": size,
            "unit": "",
            "rank": rank,
            "exclusive": exclusive,
        }
        # We add metadata with an attribute prefix to prevent conflict
        if attributes:
            metadata["attributes"] = attributes

        new_node = {"metadata": metadata, "label": label}
        self.nodes[label] = new_node
        return new_node

    def add_edge(self, source, target, relation="contains", metadata=None):
        """
        Add an edge with a specific kind of relationship
        """
        metadata = (
            metadata if metadata is not None else {"name": {"containment": relation}}
        )
        new_edge = {
            "source": source,
            "target": target,
        }
        if metadata:
            new_edge["metadata"] = metadata

        self.edges.append(new_edge)

    def add_bidirectional_edge(self, source, target):
        """
        Add a bidirectional edge.
        """
        self.add_edge(source, target, "contains")
        self.add_edge(target, source, "in")

    def generate_root(self, attributes=None, typ=None):
        """
        Generate the root cluster node
        """
        idx = self.next_count
        return self.add_node(
            typ=typ or self.name,
            path=f"/{self.name}{idx}",
            idx=idx,
            attributes=attributes,
        )

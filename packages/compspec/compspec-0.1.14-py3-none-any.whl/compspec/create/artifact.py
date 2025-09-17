__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2024, Vanessa Sochat"
__license__ = "MIT"


import json

artifact_version = "0.0.0"


def generate(plugin, name, attributes):
    """
    Given a plugin and attributes, generate an artifact.
    """
    # Create a new compatibility spec
    compat = Compatibility(
        namespace=plugin.namespace, version=plugin.version, schema=plugin.schema
    )

    # Add all attributes
    for key, value in attributes.items():
        compat.add_attribute(key, value)

    # Generate the artifact
    artifact = Artifact(name=name)
    artifact.add_compatibility_group(compat)
    return artifact


class Compatibility:
    def __init__(self, namespace, schema, version):
        """
        Create a new compatibility to add to an artifact.
        """
        self.namespace = namespace
        self.schema = schema
        self.version = version
        self.attrs = {}

    @property
    def uid(self):
        """
        A UID is determined by the namespace and version.
        """
        return f"{self.namespace}-{self.version}"

    def add_attribute(self, key, value):
        """
        Add key value pairs.

        They will automatically be namespaced under the namespace.
        """
        self.attrs[key] = value

    def to_dict(self):
        """
        to_dict converts the compatibility spec to a dictionary.
        """
        return {
            "name": self.namespace,
            "version": self.version,
            "attributes": self.attrs,
        }


class Artifact:
    def __init__(self, name):
        """
        Create a new artifact for a namespace
        """
        self.name = name

        # Compatibility groups are rendered into the artifact
        # They have their group with metadata attributes and a schema
        # We namespace them now by version
        self.compats = {}

    def add_compatibility_group(self, group):
        self.compats[group.uid] = group

    def header(self):
        return {
            "version": artifact_version,
            "kind": "CompatibilitySpec",
            "metadata": {"name": self.name, "schemas": {}},
            "compatibilities": [],
        }

    def render(self):
        """
        Render serializes the dict to json
        """
        return json.dumps(self.to_dict(), indent=4)

    def to_dict(self):
        """
        Render generates the artifact, adding all unique schemas and compatibility sections
        """
        result = self.header()
        for _, compat in self.compats.items():
            result["metadata"]["schemas"][compat.namespace] = compat.schema
            result["compatibilities"].append(compat.to_dict())
        return result

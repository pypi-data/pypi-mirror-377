__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2024, Vanessa Sochat"
__license__ = "MIT"

jgf_v2 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://jsongraphformat.info/v2.1/json-graph-schema.json",
    "title": "JSON Graph Schema",
    "oneOf": [
        {
            "type": "object",
            "properties": {"graph": {"$ref": "#/definitions/graph"}},
            "additionalProperties": False,
            "required": ["graph"],
        },
        {
            "type": "object",
            "properties": {
                "graphs": {"type": "array", "items": {"$ref": "#/definitions/graph"}}
            },
            "additionalProperties": False,
        },
    ],
    "definitions": {
        "graph": {
            "oneOf": [
                {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string"},
                        "label": {"type": "string"},
                        "directed": {"type": ["boolean"], "default": True},
                        "type": {"type": "string"},
                        "metadata": {"type": ["object"]},
                        "nodes": {
                            "type": "object",
                            "additionalProperties": {"$ref": "#/definitions/node"},
                        },
                        "edges": {
                            "type": ["array"],
                            "items": {"$ref": "#/definitions/edge"},
                        },
                    },
                },
                {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string"},
                        "label": {"type": "string"},
                        "directed": {"type": ["boolean"], "default": True},
                        "type": {"type": "string"},
                        "metadata": {"type": ["object"]},
                        "nodes": {
                            "type": "object",
                            "additionalProperties": {"$ref": "#/definitions/node"},
                        },
                        "hyperedges": {
                            "type": ["array"],
                            "items": {"$ref": "#/definitions/directedhyperedge"},
                        },
                    },
                },
                {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string"},
                        "label": {"type": "string"},
                        "directed": {"type": ["boolean"], "enum": [False]},
                        "type": {"type": "string"},
                        "metadata": {"type": ["object"]},
                        "nodes": {
                            "type": "object",
                            "additionalProperties": {"$ref": "#/definitions/node"},
                        },
                        "hyperedges": {
                            "type": ["array"],
                            "items": {"$ref": "#/definitions/undirectedhyperedge"},
                        },
                    },
                    "required": ["directed"],
                },
            ]
        },
        "node": {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "metadata": {"type": "object"},
                "additionalProperties": False,
            },
        },
        "edge": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "id": {"type": "string"},
                "source": {"type": "string"},
                "target": {"type": "string"},
                "relation": {"type": "string"},
                "directed": {"type": ["boolean"], "default": True},
                "label": {"type": "string"},
                "metadata": {"type": ["object"]},
            },
            "required": ["source", "target"],
        },
        "directedhyperedge": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "id": {"type": "string"},
                "source": {"type": "array", "items": {"type": "string"}},
                "target": {"type": "array", "items": {"type": "string"}},
                "relation": {"type": "string"},
                "label": {"type": "string"},
                "metadata": {"type": ["object"]},
            },
            "required": ["source", "target"],
        },
        "undirectedhyperedge": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "id": {"type": "string"},
                "nodes": {"type": "array", "items": {"type": "string"}},
                "relation": {"type": "string"},
                "label": {"type": "string"},
                "metadata": {"type": ["object"]},
            },
            "required": ["nodes"],
        },
    },
}

from .plugin import PluginBase
from .registry import PluginRegistry

# Only do this once
registry = None


def get_plugin_registry():
    global registry
    if registry is None:
        registry = PluginRegistry()
        registry.discover()
    return registry

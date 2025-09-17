plugin_registry = None


def add_plugin_parsers(subparser):
    """
    Dynamically add discovered plugin parsers.
    """
    global plugin_registry
    from . import get_plugin_registry

    plugin_registry = get_plugin_registry()
    for _, plugin in plugin_registry.plugins.items():
        plugin.add_arguments(subparser)

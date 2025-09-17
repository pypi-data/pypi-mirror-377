class PluginBase:
    """
    A base for a compspec plugin
    """

    def __init__(self, name):
        self.name = name
        # description should be on the class

    def add_arguments(self, subparser):
        """
        Add arguments for the plugin to show up in argparse

        This is added by the plugin class
        """
        pass

    def extract(self, args, extra):
        """
        The extract interface allows for extraction of metadata into an artifact.
        """
        raise NotImplementedError(
            f"The {self.name} plugin is missing an 'extract' function"
        )

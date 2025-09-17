#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022-2024, Vanessa Sochat"
__license__ = "MIT"

import json

import compspec.create.artifact as artifacts
import compspec.utils as utils


def main(args, extra):
    """
    Run an extraction. This can be converted to a proper function
    if needed.
    """
    from compspec.plugin.parser import plugin_registry

    # This raises an error if not found
    plugin = plugin_registry.get_plugin(args.extract)

    # Generate / extract based on the plugin type
    # Likely we want to better define these
    attributes = plugin.extract(args, extra)
    if getattr(plugin, "plugin_type", "") == "generic":
        return output_generic(attributes, args.outfile)
    return extract_artifact(plugin, args, attributes)


def output_generic(result, outfile):
    """
    A generic extraction expects some dump of json
    """
    if outfile:
        utils.write_json(result, outfile)
    else:
        print(json.dumps(result, indent=4))


def extract_artifact(plugin, args, attributes):
    """
    Extract a Compatibility artifact.
    """
    # Run extraction for an artifact
    artifact = artifacts.generate(plugin, args.name, attributes)
    if args.outfile:
        utils.write_json(artifact.to_dict(), args.outfile)
    else:
        print(artifact.render())

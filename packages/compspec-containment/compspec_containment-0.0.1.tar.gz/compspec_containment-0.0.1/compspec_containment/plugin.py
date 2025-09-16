import argparse
import logging

from compspec.create.jsongraph import JsonGraph
from compspec.plugin import PluginBase

import compspec_containment.defaults as defaults

logger = logging.getLogger("compspec-containment")


def get_resource_graph():
    """
    Wrapper function to get resource graph

    Primarily so import of plugin does not error with ImportError
    """
    # Allow error to trigger here - should be caught by calling function
    import flux
    import flux.kvs
    from fluxion.resourcegraph.V1 import FluxionResourceGraphV1

    handle = flux.Flux()
    rlite = flux.kvs.get(handle, "resource.R")
    return FluxionResourceGraphV1(rlite)


class ContainmentGraph(JsonGraph):
    pass


class Plugin(PluginBase):
    """
    The containment subsystem extractor plugin
    """

    # These metadata fields are required (and checked for)
    description = "containment subsystem"
    namespace = defaults.namespace
    version = defaults.spec_version
    plugin_type = "generic"

    def add_arguments(self, subparser):
        """
        Add arguments for the plugin to show up in argparse
        """
        plugin = subparser.add_parser(
            self.name,
            formatter_class=argparse.RawTextHelpFormatter,
            description=self.description,
        )
        # Ensure these are namespaced to your plugin
        plugin.add_argument(
            "cluster",
            help="Cluster name for top level of graph",
        )

    def detect(self):
        """
        Detect checks for import of Flux and generation of the graph.

        If we can do this, we likely have a Flux instance.
        """
        try:
            get_resource_graph()
            return True
        except ImportError:
            return False

    def extract(self, args, extra):
        """
        Search a spack install for installed software
        """

        # Create the containment graph
        g = ContainmentGraph("cluster")
        g.metadata["type"] = "containment"
        g.metadata["name"] = args.cluster
        g.metadata["install_name"] = args.name

        # The root node is the cluster, although we don't use it from here"
        g.generate_root()

        # Get the R-lite spec to convert to JGF.
        jgf = get_resource_graph()
        jgf.set_metadata(g.metadata)

        # Generate a dictionary with custom metadata
        return jgf.to_JSON()

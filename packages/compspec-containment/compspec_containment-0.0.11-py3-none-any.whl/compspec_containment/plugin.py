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
    # Create the containment graph (this checks flux imports, etc.)
    g = ContainmentGraph("cluster")
    g.metadata["type"] = "containment"
    return g


class ContainmentGraph(JsonGraph):
    """
    The containment graph generates the Fluxion JGF V1
    and converts to V2.
    """

    def __init__(self, *args, **kwargs):
        """
        Init ensures we can import and derive requirements.
        """
        super().__init__(*args, **kwargs)
        import flux
        from fluxion.resourcegraph.V1 import FluxionResourceGraphV1

        self.handle = flux.Flux()

        # By default generate JGFv1.
        self.GraphClass = FluxionResourceGraphV1
        self.generate_jgf_v1()

    def generate_jgf_v1(self):
        """
        Call functions to generate JGF V1
        """
        import flux.kvs

        rlite = flux.kvs.get(self.handle, "resource.R")
        self.jgfv1 = self.GraphClass(rlite)
        self.to_jgfv2()

    def to_jgfv2(self):
        """
        Convert the graph from version 1 to version 2.
        """
        for node in self.jgfv1.get_nodes():
            # Node metadata has type and paths
            m = node.get_metadata()
            self.add_node(
                m["type"],
                path=m["paths"],
                idx=node.get_id(),
                count=m.get("id"),
                rank=m.get("rank"),
            )

        for edge in self.jgfv1.get_edges():
            self.add_edge(
                source=edge.get_source(),
                target=edge.get_target(),
                metadata={},
            )
        return self.to_dict()


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
        # Get the R-lite spec to convert to JGF.
        g = get_resource_graph()
        g.metadata["name"] = args.cluster
        g.metadata["install_name"] = args.name

        # We need to convert from V1 to V2
        return g.to_jgfv2()

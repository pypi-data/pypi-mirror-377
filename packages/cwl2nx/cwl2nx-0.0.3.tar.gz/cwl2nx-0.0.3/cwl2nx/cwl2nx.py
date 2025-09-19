import networkx as nx
import yaml
from cwl_utils.parser import Workflow, load_document, cwl_version
from cwl_utils.parser.cwl_v1_0 import LoadingOptions as LoadingOptionsV10
from cwl_utils.parser.cwl_v1_1 import LoadingOptions as LoadingOptionsV11
from cwl_utils.parser.cwl_v1_2 import LoadingOptions as LoadingOptionsV12


DEFAULT_DISPLAY_PARAMS = {
    "step": {"color": "blue", "shape": "o", "size": 500},
    "input": {"color": "green", "shape": "s", "size": 150},
    "output": {"color": "green", "shape": "s", "size": 150},
}


class CWLToNetworkxConnector:
    def __init__(
        self,
        cwl_path: str,
        display_params: dict[
            str, dict[str, str | float | int]
        ] = DEFAULT_DISPLAY_PARAMS,
    ):
        r"""
        Initialize the connector.
        Parse and validate the cwl file, with cwl_utils library.

        Parameters :
        ---

        - cwl_path: path to the cwl file
        - display_params : display parameters for steps, inputs and outputs

            example value for display_params :

                ```
                {
                    "step": {"color": "blue", "shape": "o", "size": 500},
                    "input": {"color": "green", "shape": "s", "size": 150},
                    "output": {"color": "green", "shape": "s", "size": 150},
                }
                ```
            see : https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.display.html

        """
        self.cwl_path = cwl_path
        self.verbose_node_names = True
        self.display_params = display_params

        self.cwl_utils_graph: Workflow = self.parse_and_validate_cwl()
        self.nx_graph: nx.DiGraph = nx.DiGraph()

    def parse_and_validate_cwl(self) -> Workflow:
        r"""
        Parse the cwl in an Workflow object from cwl_utils
        parser submodule.

        Returns :
        ---
        The Workflow object from cwl_utils library, validated.
        """
        try:
            with open(self.cwl_path, "rt") as f:
                raw_yaml = yaml.safe_load(f)
            self.cwl_version = cwl_version(raw_yaml)

            loading_options = None
            match self.cwl_version:
                case "v1.0":
                    loading_options = LoadingOptionsV10(no_link_check=True)
                case "v1.1":
                    loading_options = LoadingOptionsV11(no_link_check=True)
                case "v1.2":
                    loading_options = LoadingOptionsV12(no_link_check=True)
                case _:
                    raise ValueError(
                        f"Unexcpected cwl_version in cwl file : {self.cwl_version}"
                    )

            parsed_cwl = load_document(raw_yaml, loadingOptions=loading_options)
            # add a proper label for each step
            for each_step in parsed_cwl.steps:
                if self.verbose_node_names:
                    each_step.label = each_step.id
                else:
                    each_step.label = each_step.id.split("/")[-1]

        except Exception:
            raise Exception(f"Could not parse and validate the cwl file.")
        else:
            return parsed_cwl

    def convert_to_networkx(self, datasets_as_nodes: bool = False) -> nx.DiGraph:
        r"""
        Convert the cwl_utils.parser.Workflow in a networkx graph.

        Parameters :
        ---
            - datasets_as_nodes : boolean, whether to have a node for each input
                and output datasets, or to represent them with edges between steps.

        Returns :
        ---
        The networkx DiGraph associated with the cwl, where :
            - input and output datasets are displayed as small squares,
            - steps are displayed as circles.
        """
        color_step = self.display_params["step"]["color"]
        shape_step = self.display_params["step"]["shape"]
        size_step = self.display_params["step"]["size"]

        color_input = self.display_params["input"]["color"]
        shape_input = self.display_params["input"]["shape"]
        size_input = self.display_params["input"]["size"]

        color_output = self.display_params["output"]["color"]
        shape_output = self.display_params["output"]["shape"]
        size_output = self.display_params["output"]["size"]

        for each_step in self.cwl_utils_graph.steps:
            self.nx_graph.add_node(each_step.id)
            self.nx_graph.nodes[each_step.id]["color"] = color_step
            self.nx_graph.nodes[each_step.id]["shape"] = shape_step
            self.nx_graph.nodes[each_step.id]["size"] = size_step
            self.nx_graph.nodes[each_step.id]["label"] = each_step.id.split("/")[-1]
            self.nx_graph.nodes[each_step.id]["cwl"] = {
                "source_object": each_step,
                "node_type": "step",
            }

            for each_input in each_step.in_:
                self.nx_graph.add_node(each_input.source)
                self.nx_graph.nodes[each_input.source]["color"] = color_input
                self.nx_graph.nodes[each_input.source]["shape"] = shape_input
                self.nx_graph.nodes[each_input.source]["size"] = size_input
                self.nx_graph.nodes[each_input.source]["label"] = (
                    each_input.source.split("/")[-1]
                )
                self.nx_graph.nodes[each_input.source]["cwl"] = {
                    "source_object": each_input,
                    "node_type": "input",
                }
                self.nx_graph.add_edge(each_input.source, each_step.id)

            for each_output in each_step.out:
                self.nx_graph.add_node(each_output)
                self.nx_graph.nodes[each_output]["color"] = color_output
                self.nx_graph.nodes[each_output]["shape"] = shape_output
                self.nx_graph.nodes[each_output]["size"] = size_output
                self.nx_graph.nodes[each_output]["label"] = each_output.split("/")[-1]
                self.nx_graph.nodes[each_output]["cwl"] = {
                    "source_object": each_output,
                    "node_type": "output",
                }
                self.nx_graph.add_edge(each_step.id, each_output)

        if not nx.is_directed_acyclic_graph(self.nx_graph):
            raise Exception(f"The parsed graph is not a DAG (Directed Acyclic Graph).")

        if not datasets_as_nodes:
            self.remove_dataset_nodes()

        return self.nx_graph

    def remove_dataset_nodes(self):
        drop_nodes = []
        for each_node_name in self.nx_graph.nodes:
            this_node = self.nx_graph.nodes[each_node_name]
            if this_node["cwl"]["node_type"] in ["input", "output"]:
                # add an edge between steps
                drop_nodes.append(each_node_name)
                for each_predecessor in self.nx_graph.predecessors(each_node_name):
                    for each_successor in self.nx_graph.successors(each_node_name):
                        self.nx_graph.add_edge(
                            each_predecessor, each_successor, label=this_node["label"]
                        )

        self.nx_graph.remove_nodes_from(drop_nodes)  # drop the input and output nodes

    def display_nx_graph(self) -> None:
        r"""
        Plot the networkx graph. If cwl is not yet converted to networkx,
        it first create the networkx DiGraph.

        Returns :
        ---
        The networkx DiGraph associated with the cwl file.

        """
        if self.nx_graph is None:
            self.convert_to_networkx()
        nx.display(G=self.nx_graph)


if __name__ == "__main__":
    dir = "workflow_example.cwl.yaml"
    display_params = DEFAULT_DISPLAY_PARAMS
    display_params["output"]["color"] = "orange"
    nx_graph = CWLToNetworkxConnector(dir).convert_to_networkx()
    nx.display(nx_graph)

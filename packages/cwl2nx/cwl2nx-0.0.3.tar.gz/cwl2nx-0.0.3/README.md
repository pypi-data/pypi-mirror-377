# CWL2Nx

Lightweight python module to load, validate and visualize CWL (Common Workflow Language) files through networkx graphs.
It uses [cwl_utils](https://github.com/common-workflow-language/cwl-utils) for parsing and validation.

## Installation

```
pip install cwl2nx
```

## Usage

### Straightforward conversion

```python
from cwl2nx import CWLToNetworkxConnector
import networkx as nx
import matplotlib.pyplot as plt

dir = "workflow.yaml"
dag = CWLToNetworkxConnector(dir).convert_to_networkx() # dag is networkx.DiGraph

# one can display the networkx graph hereafter
nx.display(dag)
plt.show()
```

### Usage of Connector

```python
from cwl2nx import CWLToNetworkxConnector
import networkx as nx

dir = "workflow.yaml"
connector = CWLToNetworkxConnector(dir)
connector.convert_to_networkx()
connector.plot_nx_graph()
```

## Example 


![img](example_display.png)

## License

[Apache 2.0](LICENSE-2.0.txt)
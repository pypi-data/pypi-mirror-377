# Compspec Containment

<p align="center">
  <img height="300" src="https://raw.githubusercontent.com/compspec/spec/main/img/compspec-circle.png">
</p>

[![PyPI version](https://badge.fury.io/py/compspec-containment.svg)](https://badge.fury.io/py/compspec-containment)

A compspec (Composition spec) is a specification and model for comparing things. Compspec containment is
a plugin for extraction of the Flux Framework containment subsystem, which means verices (cluster, racks, nodes, sockets, cores, etc) and edges between them that describe relationships (e.g., "contains"). Other cluster types can be added and they will need to have an intermediate translation into a graph. To learn more:

 - [Compspec](https://github.com/compspec/compspec): the Python library that discovers and loads this plugin.

## Usage

Install compspec and the plugin here:

```bash
pip install compspec
pip install compspec-containment
```

In the dev container, try running an extraction for the Flux instance running:

```bash
flux start --test-size=4
compspec extract containment cluster-a
```

To save to file:

```bash
# This extracts a cluster named "a"
compspec extract --outfile containment-subsystem.json containment a
```

You can see the example [example/containment-subsystem.json](example/containment-subsystem.json).

<details>

<summary>compspec-containment output</summary>

```console
{
    "graph": {
        "directed": false,
        "metadata": {
            "type": "containment",
            "name": "a",
            "install_name": "compat-experiment"
        },
        "nodes": [
            {
                "id": "0",
                "metadata": {
                    "type": "cluster",
                    "paths": {
                        "containment": "/cluster0"
                    }
                }
            },
            {
                "id": "1",
                "metadata": {
                    "type": "node",
                    "name": "039b58a80799",
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799"
                    }
                }
            },
            {
                "id": "2",
                "metadata": {
                    "type": "core",
                    "id": 0,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core0"
                    }
                }
            },
            {
                "id": "3",
                "metadata": {
                    "type": "core",
                    "id": 1,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core1"
                    }
                }
            },
            {
                "id": "4",
                "metadata": {
                    "type": "core",
                    "id": 2,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core2"
                    }
                }
            },
            {
                "id": "5",
                "metadata": {
                    "type": "core",
                    "id": 3,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core3"
                    }
                }
            },
            {
                "id": "6",
                "metadata": {
                    "type": "core",
                    "id": 4,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core4"
                    }
                }
            },
            {
                "id": "7",
                "metadata": {
                    "type": "core",
                    "id": 5,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core5"
                    }
                }
            },
            {
                "id": "8",
                "metadata": {
                    "type": "core",
                    "id": 6,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core6"
                    }
                }
            },
            {
                "id": "9",
                "metadata": {
                    "type": "core",
                    "id": 7,
                    "rank": 0,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core7"
                    }
                }
            },
            {
                "id": "10",
                "metadata": {
                    "type": "node",
                    "name": "039b58a80799",
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799"
                    }
                }
            },
            {
                "id": "11",
                "metadata": {
                    "type": "core",
                    "id": 0,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core0"
                    }
                }
            },
            {
                "id": "12",
                "metadata": {
                    "type": "core",
                    "id": 1,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core1"
                    }
                }
            },
            {
                "id": "13",
                "metadata": {
                    "type": "core",
                    "id": 2,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core2"
                    }
                }
            },
            {
                "id": "14",
                "metadata": {
                    "type": "core",
                    "id": 3,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core3"
                    }
                }
            },
            {
                "id": "15",
                "metadata": {
                    "type": "core",
                    "id": 4,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core4"
                    }
                }
            },
            {
                "id": "16",
                "metadata": {
                    "type": "core",
                    "id": 5,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core5"
                    }
                }
            },
            {
                "id": "17",
                "metadata": {
                    "type": "core",
                    "id": 6,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core6"
                    }
                }
            },
            {
                "id": "18",
                "metadata": {
                    "type": "core",
                    "id": 7,
                    "rank": 1,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core7"
                    }
                }
            },
            {
                "id": "19",
                "metadata": {
                    "type": "node",
                    "name": "039b58a80799",
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799"
                    }
                }
            },
            {
                "id": "20",
                "metadata": {
                    "type": "core",
                    "id": 0,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core0"
                    }
                }
            },
            {
                "id": "21",
                "metadata": {
                    "type": "core",
                    "id": 1,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core1"
                    }
                }
            },
            {
                "id": "22",
                "metadata": {
                    "type": "core",
                    "id": 2,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core2"
                    }
                }
            },
            {
                "id": "23",
                "metadata": {
                    "type": "core",
                    "id": 3,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core3"
                    }
                }
            },
            {
                "id": "24",
                "metadata": {
                    "type": "core",
                    "id": 4,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core4"
                    }
                }
            },
            {
                "id": "25",
                "metadata": {
                    "type": "core",
                    "id": 5,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core5"
                    }
                }
            },
            {
                "id": "26",
                "metadata": {
                    "type": "core",
                    "id": 6,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core6"
                    }
                }
            },
            {
                "id": "27",
                "metadata": {
                    "type": "core",
                    "id": 7,
                    "rank": 2,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core7"
                    }
                }
            },
            {
                "id": "28",
                "metadata": {
                    "type": "node",
                    "name": "039b58a80799",
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799"
                    }
                }
            },
            {
                "id": "29",
                "metadata": {
                    "type": "core",
                    "id": 0,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core0"
                    }
                }
            },
            {
                "id": "30",
                "metadata": {
                    "type": "core",
                    "id": 1,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core1"
                    }
                }
            },
            {
                "id": "31",
                "metadata": {
                    "type": "core",
                    "id": 2,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core2"
                    }
                }
            },
            {
                "id": "32",
                "metadata": {
                    "type": "core",
                    "id": 3,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core3"
                    }
                }
            },
            {
                "id": "33",
                "metadata": {
                    "type": "core",
                    "id": 4,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core4"
                    }
                }
            },
            {
                "id": "34",
                "metadata": {
                    "type": "core",
                    "id": 5,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core5"
                    }
                }
            },
            {
                "id": "35",
                "metadata": {
                    "type": "core",
                    "id": 6,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core6"
                    }
                }
            },
            {
                "id": "36",
                "metadata": {
                    "type": "core",
                    "id": 7,
                    "rank": 3,
                    "paths": {
                        "containment": "/cluster0/039b58a80799/core7"
                    }
                }
            }
        ],
        "edges": [
            {
                "source": "0",
                "target": "1"
            },
            {
                "source": "1",
                "target": "2"
            },
            {
                "source": "1",
                "target": "3"
            },
            {
                "source": "1",
                "target": "4"
            },
            {
                "source": "1",
                "target": "5"
            },
            {
                "source": "1",
                "target": "6"
            },
            {
                "source": "1",
                "target": "7"
            },
            {
                "source": "1",
                "target": "8"
            },
            {
                "source": "1",
                "target": "9"
            },
            {
                "source": "0",
                "target": "10"
            },
            {
                "source": "10",
                "target": "11"
            },
            {
                "source": "10",
                "target": "12"
            },
            {
                "source": "10",
                "target": "13"
            },
            {
                "source": "10",
                "target": "14"
            },
            {
                "source": "10",
                "target": "15"
            },
            {
                "source": "10",
                "target": "16"
            },
            {
                "source": "10",
                "target": "17"
            },
            {
                "source": "10",
                "target": "18"
            },
            {
                "source": "0",
                "target": "19"
            },
            {
                "source": "19",
                "target": "20"
            },
            {
                "source": "19",
                "target": "21"
            },
            {
                "source": "19",
                "target": "22"
            },
            {
                "source": "19",
                "target": "23"
            },
            {
                "source": "19",
                "target": "24"
            },
            {
                "source": "19",
                "target": "25"
            },
            {
                "source": "19",
                "target": "26"
            },
            {
                "source": "19",
                "target": "27"
            },
            {
                "source": "0",
                "target": "28"
            },
            {
                "source": "28",
                "target": "29"
            },
            {
                "source": "28",
                "target": "30"
            },
            {
                "source": "28",
                "target": "31"
            },
            {
                "source": "28",
                "target": "32"
            },
            {
                "source": "28",
                "target": "33"
            },
            {
                "source": "28",
                "target": "34"
            },
            {
                "source": "28",
                "target": "35"
            },
            {
                "source": "28",
                "target": "36"
            }
        ]
    }
}
```

</details>



## License

HPCIC DevTools is distributed under the terms of the MIT license.
All new contributions must be made under this license.

See [LICENSE](https://github.com/converged-computing/cloud-select/blob/main/LICENSE),
[COPYRIGHT](https://github.com/converged-computing/cloud-select/blob/main/COPYRIGHT), and
[NOTICE](https://github.com/converged-computing/cloud-select/blob/main/NOTICE) for details.

SPDX-License-Identifier: (MIT)

LLNL-CODE- 842614

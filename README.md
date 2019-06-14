<img align="right" src="logo.svg">

# Practical OCT

(*Image credit: Felix Reidl*)

## Environment Configuration

Practical OCT is implemented in Python and C/C++ (using clang). In addition, it makes use of two
ILP solvers, GLPK and IBM CPLEX, and an additional implementation written in Java.

To build and run Practical OCT, both ILP solvers and the language toolchains for Python, C/C++, and Java
must be available. It is known to support the following language and build tool versions.

| Tool | Version |
| ---- | ------- |
| Python | 3.5.3 |
| Clang | 3.8.1-24 |
| JDK | 1.8.0_162 |
| CPLEX | 12.8 |
| GLPK | 4.61 |

To configure a development environment, first run `make`. The `Makefile` will

* Build a new Python 3.5 virtual environment (local copy of Python 3.5 required)
* Download the source for external solvers used in experiments
* Compile all C/C++ and Java source code (clang and javac required)
* Download and extract all original data files

The installed Python virtual environment can be activated with `source env/bin/activate`. With the Python virtual environment activated, install the CPLEX Python bindings according to the IBM documentation.


## Experiments

See [REPLICABILITY](REPLICABILITY.md) for instructions on reproducing experiments.

## Utilities

### Akiba-Iwata Solver

Solves VertexCover, optionally translating the answer to a solution for OCT.

```
python -m src.akiba_iwata.solver [option [option ...]] <snap-file>
```

| Flag | Values | Description |
| -------- | ------ | ----------- |
| `timeout` | `(0, INF)` | Timeout in seconds. |
| `convert-to-oct` | N/A | Whether or not to convert the answer to OCT. |

Output will be in the format

```
time,size,"certificate"
```

where `time` is the total time in seconds, `size` is the number of vertices in the certificate,
and `certificate` is a Python formatted list of vertices.

### Heuristics Solver

Runs OCT heuristics on an edgelist formatted graph.

```
./src/heuristics/heuristics_solver <timelimit> <edgelist-file>
```

Timelimit is expressed in milliseconds.

Output will be in the format

```
size,time,"certificate"
```

where `size` is the number of vertices in the certificate, `time` is the total time in milliseconds,
and `certificate` is a Python formatted list of vertices.

### Huffner Solver

Solves OCT on a Hüffner formatted graph file.

```
python -m src.huffner.solver [option [option ...]] <huffner-file>
```

| Flag | Values | Description |
| -------- | ------ | ----------- |
| `timeout` | `(0, INF)` | Time limit in seconds. |
| `preprocessing` | `{0, 1, 2}` | Preprocessing level (none, heuristics, heuristics+density). |
| `seed` | `(0, INF)` | Random number generator seed. |
| `htime` | `(0, INF)` | Amount of time, in seconds, to run heuristics for with preprocessing. |

Output will be in the format

```
time,size,"certificate"
```

where `time` is the total time in seconds, `size` is the number of vertices in the certificate,
and `certificate` is a Python formatted list of vertices.

### ILP Solver

The general ILP solver can be used to solve VertexCover and OCT from snap and edgelist files.

```
python -m src.ilp.solver [option [option ...]] <edgelist-file|snap-file>
```

| Flag | Values | Description |
| -------- | ------ | ----------- |
| `formulation` | `VC`, `OCT` | Which problem formulation to solve for. Defaults to `OCT`. |
| `mipgap` | `[0, 1]` | Tolerated gap. Defaults to `0`. |
| `solver` | `CPLEX`, `GLPK` | ILP solver used to compute solution. Defaults to `GLPK`. |
| `threads` | `[0, INF]` | Number of threads used to compute solution. Ignored for GLPK. Defaults to `1`. |
| `timelimit` | `(0, INF)` | Time limit for computation in seconds. GLPK will cast to nearest second. Defaults to `INF`. |
| `convert-to-oct` | `{True, False}` | Whether or not to convert a VC solution to an OCT solution. Defaults to `False`. |

Output will be in the form

```
n = int
m = int
opt = int
time = float
threads = int
mipgap = float
certificate = int int int ...
cuts =
    name: int
    ...
```

## Data Formats

All preprocessed data conforms to one of the following data formats.

### Edgelist

A graph file format. The first line is `n m`, where `n` is the number of vertices and `m` is the
number of edges. All following lines are of the format `u v`, representing an edge between vertices
`u` and `v`.

Edgelist files contain the preprocessed version of the original graph.

### Huffner

A graph file format for Hüffner's algorithm. Contains the following blocks

* `# Graph Name`
* `# Number of Vertices`
* `# Number of Edges`
* `# Vertex Names`
* `# Edges`
* `# EOF`

Each block, except for `EOF`, is followed by the a line or lines containing the data described
in the header. Edges are formatted as `u v` pairs for an edge between vertex `u` and `v`.

### Snap

A graph file format. Starts with the header

```
# Nodes: <int> Edges: <int>
# FromNodeId 	 ToNodeId
```

All subsequent lines are formatted as `u v` to indicate an edge between vertices `u` and `v`.

Snap files contain the VertexCover version of the preprocessed graph.

### Lookup

A preprocessing metadata file used for mapping all preprocessed vertices back to their name in the
original graph. Each line contains a single `vertex name` pair.

### OCT

A preprocessing metadata file that contains the list of vertices that were marked as must be OCT
by preprocessing routines.

### Summary

Summary files are written for `beasley`, `gka`, and `huffner` data. Each file is a CSV formatted
file with the following headers.

| Header | Description |
| ------ | ----------- |
| Dataset | Name of a preprocessed dataset. |
| vertices_removed | Number of vertices removed during preprocessing. |
| edges_removed | Number of edges removed from  |
| oct | Number of vertices labeled as OCT. |
| bipartite | Number of vertices labeled as bipartite. |

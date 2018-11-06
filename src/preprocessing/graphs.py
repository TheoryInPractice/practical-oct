"""A collection of graph operations used in preprocessing."""


import networkx as nx


MAX_NODES = 50


def open_path(path, mode='r'):
    """ Python < 3.6 doesn't support calling open on a Pathlib Path.

    Parameters
    ----------
    path : Path
        Pathlib path to open
    """
    return open(str(path), mode)


def reset_labels(graph):
    """
    Relabel the vertices 0, ..., n-1 and maintain the graph name.
    """
    # convert_node_labels_to_integers will keep all graph attributes, except it
    # modifies the name. So manually store and then restore the name.
    name = graph.graph['name']
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    graph.graph['name'] = name
    return graph


def init_stats(graph):
    """
    Initialize the reduction statistics to zero.
    """
    graph.graph['vertices_removed'] = 0
    graph.graph['edges_removed'] = 0
    graph.graph['oct'] = 0
    graph.graph['bipartite'] = 0
    return graph


def names_in_dir(dir_name, extension):
    """
    Return a sorted list of file names with a particular extension in a
    directory. The extension is not included in the filenames, and files
    starting with underscores are ignored.
    """
    # Find names using glob
    names = [x.name for x in dir_name.glob('[!_]*{}'.format(extension))]
    # Clean up and return
    names = [name.replace(extension, '') for name in names]
    names = sorted(names)
    return names


def read_beasley(input_dir, dataset_name):
    """
    Populate and yield a NetworkX Graph with Beasley's data.
    Nodes are strings and should be relabeled if desired.
    """

    # print("Read Beasley was called on", dataset_name, "in folder", input_dir)

    graph = nx.Graph(name=dataset_name.replace('.txt', ''.format(dataset_name)))
    with open_path(input_dir / dataset_name, 'r') as infile:
        order, size = map(int, infile.readline().split())
        # print("Order, size:", order, size)
        # Beasley vertices are labeled 1, ..., n
        for vertex in list(map(str, range(1, order + 1))):
            graph.add_node(vertex, og_name=str(vertex))

        # Read in edges and convert them to indices
        for _ in range(size):
            line = infile.readline()
            edge = line.strip().split()
            # For consistency with QUBO literature, throw out vertices with
            # zero weight.
            if int(edge[2]) != 0 and (edge[0] != edge[1]):
                graph.add_edge(*edge[0:2])
        # print("Graph:", graph.order(), graph.size())
        graph = init_stats(graph)
        return graph


def read_huffner(input_dir, dataset_name):
    """
    Populate and yield a NetworkX Graph with Huffner's data.
    Nodes are strings and should be relabeled if desired.
    """

    graph = nx.Graph(name=dataset_name.replace('.graph', ''))
    with open_path(input_dir / dataset_name, 'r') as infile:
        # Handle the header
        infile.readline()  # Throw out '# Graph Name'
        infile.readline()  # Throw out graph name
        infile.readline()  # Throw out '# Number of Vertices'
        order = int(infile.readline())
        infile.readline()  # Throw out '# Number of Edges'
        size = int(infile.readline())
        infile.readline()  # Throw out '# Vertex names'

        # Read in vertices
        for _ in range(order):
            vertex = infile.readline().strip()
            graph.add_node(vertex, og_name=vertex)

        # Read in edges and convert them to indices
        infile.readline()  # Throw out '# Edges'
        for _ in range(size):
            edge = infile.readline().split()
            if edge[0] != edge[1]:
                graph.add_edge(*edge)

        graph = init_stats(graph)
        return graph


def read_edgelist(input_dir, dataset_name):
    """
    Populate and yield a NetworkX Graph with edgelist data.
    Nodes are strings and should be relabeled if desired.
    """
    graph = nx.Graph(name=dataset_name.replace('.edgelist', ''))
    with open_path(input_dir / dataset_name, 'r') as infile:
        # Handle the header
        order, size = map(int, infile.readline().split())

        # 'Read in vertices'
        for vertex in list(map(str, range(0, order))):
            graph.add_node(vertex, og_name=str(vertex))

        # Read in edges and convert them to indices
        for _ in range(size):
            edge = infile.readline().split()
            if edge[0] != edge[1]:
                graph.add_edge(*edge)

        graph = init_stats(graph)
        return graph


def write_edgelist(graph, output_dir):
    """
    Write a qubo as an edgelist.
    First line has #vertices #edges.
    Subtract one from edges so they start at 0.
    """
    name = '{}.edgelist'.format(graph.graph['name'])
    with open_path(output_dir / name, 'w') as outfile:
        outfile.write('{} {}\n'.format(graph.order(), graph.size()))
        for edge in graph.edges():
            outfile.write('{} {}\n'.format(*edge))


def write_huffner(graph, output_dir):
    """
    Write a qubo in the style of Huffner's data.
    """
    name = '{}.huffner'.format(graph.graph['name'])
    with open_path(output_dir / name, 'w') as outfile:
        outfile.write('# Graph Name\n{}\n'.format(name))
        outfile.write('# Number of Vertices\n{}\n'.format(graph.order()))
        outfile.write('# Number of Edges\n{}\n'.format(graph.size()))
        outfile.write('# Vertex names\n')
        for vertex in graph.nodes():
            outfile.write('{}\n'.format(vertex))
        outfile.write('# Edges\n')
        for edge in graph.edges():
            outfile.write('{} {}\n'.format(*edge))
        outfile.write('# EOF\n')


def write_snap(graph, output_dir):
    """
    Write a qubo in the style of Akiba-Iwata's snap files.
    """
    name = '{}.snap'.format(graph.graph['name'])
    with open_path(output_dir / name, 'w') as outfile:
        outfile.write('# Nodes: {} Edges: {}\n'.format(graph.order(),
                                                       graph.size()))
        outfile.write('# FromNodeId \t ToNodeId\n')
        for vertex in graph.nodes():
            outfile.write('{} {}\n'.format(vertex, vertex + graph.order()))
        for edge in graph.edges():
            outfile.write('{} {}\n'.format(*edge))
            outfile.write('{} {}\n'.format(
                *map(lambda x: x + graph.order(), edge)))


def convert_oct_set(oct_set, og_names):
    """
    Maps an OCT set on the preprocessed graph to their original vertices.
    """
    try:
        return list(map(lambda x: og_names[x], oct_set))
    except Exception:
        print('Error: OCT set', oct_set)
        print('Error: og_names', og_names)
        print('Problem looking up OCT set')


def load_pre_oct_set(input_dir, filename):
    """
    Reads in .oct file where OCT vertices are preprocessed from the original
    data graph.
    """
    with open_path(input_dir / filename, 'r') as infile:
        return [x.strip() for x in infile.readlines()]


def load_og_name_lookup(input_dir, filename):
    """
    Reads in a .lookup into a dict that maps a relabeled name to an og_name.
    """
    og_names = {}
    with open_path(input_dir / filename, 'r') as infile:
        for line in infile.readlines():
            key, value = line.split()
            og_names[key] = value
    return og_names


def could_be_isomorphic(g1, g2):
    """Check if two graphs could be isomorphic.

    For small graphs, this checks for true isomorphism.
    For large graphs, this uses `networkx.could_be_isomorphic`.
    """

    if g1.number_of_nodes() < MAX_NODES:
        return nx.is_isomorphic(g1, g2)
    else:
        return nx.could_be_isomorphic(g1, g2)

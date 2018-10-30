"""
Reduction routines proposed in
http://theinf1.informatik.uni-jena.de/publications/wernicke-da.pdf
Section 6.3.2, Page 79.

All reduction routines take in and return a NetworkX Graph.

Some reduction rules may add to the OCT set, in which case they will also take
in and return a list oct_set.

If vertices are marked as "not_oct" then there exists an optimal OCT set
that do not include these vertices. This metadata may be used downstream to
speed up iterative compression. *Note that no_oct vertices are still ellgible
for removal with reductions, so reduction rules do not need to consider this
label*
"""

import networkx as nx


def sort_collection_of_sets(collection):
    """
    Subroutine used for removing nondeterminism from NetworkX calls.
    We first map the elements to lists and sort each list, then we sort the
    list of lists.
    """

    return sorted(map(lambda x: sorted(list(x)), collection))


def reduction_rule_1(graph, oct_set):
    """
    Remove any bipartite components.
    """
    changed = False
    # print("Entered RR1")
    # Compute the nodes in a bipartite component
    nodes_to_remove = []
    for subgraph in nx.connected_component_subgraphs(graph):
        if nx.is_bipartite(subgraph):
            changed = True
            nodes_to_remove += subgraph.nodes()

    # Update the graph's preprocessing statistics
    graph.graph['vertices_removed'] += len(nodes_to_remove)

    # Remove the nodes
    graph.remove_nodes_from(nodes_to_remove)
    # print("Exited RR1")
    return changed, graph, oct_set


def reduction_rule_2(graph, oct_set):
    """
    Remove vertices of degree 1.
    Mark degree 2 vertices as "bipartite".

    If the graph was updated then it's possible we created a degree 1 node
    after it was examined, so repeat until no updates.
    """
    # print("Entered RR2")
    # Repeat until no updates are made
    changed = False
    updated = True
    while (updated):
        # In one iteration, identify the degree 1 and degree 2 nodes and
        # mark as detailed above.
        updated = False
        nodes_to_remove = []

        # Removal order doesn't matter as long as we repeat until min degree is
        # 2.
        for node in graph.nodes():
            # print("Looking at node: ", node)
            if graph.degree(node) == 1:
                # The underlying graph will be updated after this loop,
                # so note this by setting updated.
                changed = True
                updated = True
                nodes_to_remove.append(node)
            elif graph.degree(node) == 2:
                # Note that relabeling doesn't change the underlying graph,
                # therefore updated is not set True.

                # Find a lookup table that maps a vertex to its og_name
                og_name_lookup = nx.get_node_attributes(graph, 'og_name')

                # "Re-Add" this vertex, marked as bipartite=True, and make sure
                # it keeps its og_name.
                graph.add_node(node, bipartite=True,
                               og_name=og_name_lookup[node])

        # Update the graph's preprocessing statistics
        graph.graph['vertices_removed'] += len(nodes_to_remove)

        # Timothy: Note
        graph.graph['bipartite'] = len([x for x, y in graph.nodes(data=True) if
                                        'bipartite' in y])
        graph.remove_nodes_from(nodes_to_remove)

    # Sanity check: All "bipartite" nodes should have degree 2
    # assert(len(nx.get_node_attributes(graph, 'bipartite')) ==
    #        len([x for x in graph.nodes() if graph.degree(x) == 2]))

    # print("Exited RR2")
    return changed, graph, oct_set


def reduction_rule_3(graph, oct_set):
    """
    Remove bridges.
    """
    # print("Entered RR3")
    changed = False
    bridges = list(nx.bridges(graph))

    if len(bridges) > 0:
        changed = True
        # Update the graph's preprocessing statistics
        graph.graph['edges_removed'] += len(bridges)

        # Execute the removal
        graph.remove_edges_from(bridges)

    # Sanity check: Shouldn't have any bridges!
    assert(len(list(nx.bridges(graph))) == 0)

    # print("Exited RR3")
    return changed, graph, oct_set


def reduction_rule_4(graph, oct_set):
    """
    Cut-vertices and their resulting components are examined.
    Note: OCT set may be updated.
    """

    # print("Entered RR4")

    # May need to remove multiple cut vertices
    changed = False
    updated = True
    while(updated):
        updated = False

        # Return if no cut vertex
        if graph.order() == 0 or nx.node_connectivity(graph) != 1:
            return changed, graph, oct_set

        # Else find a cut vertex and proceed
        # nx.all_node_cuts returns a "list" of "sets"
        # We know the sets are of size 1
        # So pull out the first set and store its only item in node_v
        node_cuts = sort_collection_of_sets(nx.all_node_cuts(graph, k=1))
        while node_cuts and not updated:
            # Pull off the next cut vertex
            node_v = node_cuts.pop().pop()

            # Compute remaining nodes
            remaining_nodes = set(graph.nodes())
            remaining_nodes.remove(node_v)

            # Range over the resulting components
            components = sort_collection_of_sets(nx.connected_components(
                graph.subgraph(remaining_nodes)))

            while components and not updated:
                component_nodes = set(components.pop())

                # Original component needs to be bipartite
                if nx.is_bipartite(graph.subgraph(component_nodes)):
                    changed = True
                    updated = True

                    # Case 1: Component + v is bipartite
                    component_nodes.add(node_v)
                    if nx.is_bipartite(graph.subgraph(component_nodes)):
                        component_nodes.remove(node_v)

                        # Update the preprocessing statistics
                        graph.graph['vertices_removed'] += len(component_nodes)
                        graph.remove_nodes_from(component_nodes)

                    # Case 2: Only component is bipartite
                    else:
                        # Update the preprocessing statistics
                        graph.graph['oct'] += 1
                        og_name_lookup = nx.get_node_attributes(graph,
                                                                'og_name')
                        oct_set.add(og_name_lookup[node_v])
                        graph.remove_node(node_v)

    # print("Exited RR4")
    return changed, graph, oct_set


def reduction_rule_5(graph, oct_set):
    """
    Paths whose internal vertices have degree 2 can be reduced.
    """

    # print("Entered RR5")
    changed = False

    # path will contain the vertices in this degree-2 path
    path = set()

    # Identify the degree two vertices
    degree_two_nodes = set(filter(lambda node: graph.degree(node) == 2,
                                  graph.nodes()))

    while degree_two_nodes:
        # # print("Starting round with {} as deg-2 nodes".format(degree_two_nodes))
        # Start a new path. We will reduce to a path
        # left_endpoint-right_endpoint (if even) or
        # left_endpoint-root_node-right_endpoint (if odd)
        root_node = degree_two_nodes.pop()
        left_endpoint, right_endpoint = graph.neighbors(root_node)
        path.clear()
        path.add(root_node)

        # Grow the path in the "left" direction. When we exit the while
        # loop, left_endpoint will be the first non-degree-2 vertex at the
        # end of our path.
        last_node = root_node
        while (graph.degree(left_endpoint) == 2 and
               left_endpoint not in path):
            # while loop order is important: We don't want to do these steps if
            # left_endpoint has degree > 2.
            degree_two_nodes.remove(left_endpoint)
            # # print("Added {} to left end of path".format(left_endpoint))
            path.add(left_endpoint)
            # Pick the new neighbor. This filter works because there will be
            # exactly one neighbor not equal to last_node.
            next_node = list(filter(lambda neighbor: neighbor != last_node,
                                    graph.neighbors(left_endpoint)))[0]
            last_node = left_endpoint
            left_endpoint = next_node

        # Grow the path in the "right" direction. Similar to above.
        last_node = root_node
        while (graph.degree(right_endpoint) == 2 and
               right_endpoint not in path):
            # while loop order is important: We don't want to do these steps if
            # right_endpoint has degree > 2.
            degree_two_nodes.remove(right_endpoint)
            # # print("Added {} to right end of path".format(right_endpoint))
            path.add(right_endpoint)
            # Pick the new neighbor. This filter works because there will be
            # exactly one neighbor not equal to last_node.
            next_node = list(filter(lambda neighbor: neighbor != last_node,
                                    graph.neighbors(right_endpoint)))[0]
            last_node = right_endpoint
            right_endpoint = next_node

        # # print("Constructed path:", path)

        # Prevent cycles, they should be handled in RR1
        if left_endpoint in path or right_endpoint in path:
            continue

        # If the path is more than the initial node, reduce such that
        # parity is maintained. Note that the path must be odd or must be even
        # and its endpoints are not adjacent. Also make sure the endpoints are
        # not the same.
        if len(path) > 1 and left_endpoint != right_endpoint and \
            ((len(path) % 1) == 1 or
             (not graph.has_edge(left_endpoint, right_endpoint))):
            changed = True
            # Update the preprocessing statistics
            graph.graph['vertices_removed'] += len(path)

            # Remove the identified path
            og_name_lookup = nx.get_node_attributes(graph, 'og_name')
            graph.remove_nodes_from(path)

            if len(path) % 2:
                # If the path is even, we need to add back in a vertex
                # (root_node) to keep the path partity
                graph.add_node(root_node, og_name=og_name_lookup[root_node])
                graph.add_edge(left_endpoint, root_node)
                graph.add_edge(right_endpoint, root_node)
            else:
                # Otherwise we can simply remove all vertices internal to the
                # path
                graph.add_edge(left_endpoint, right_endpoint)

    # print("Exited RR5")
    return changed, graph, oct_set


def reduction_rule_6(graph, oct_set):
    """
    node cuts of size 2 can be handled.
    """

    # print("Entered RR6")
    # find cut of size 2: {u, v}
    # find vertex sets C1, ..., Cn of connected component in G-{u,v}
    # If Ci is bipartite:
    #   If Ci + {u, v} is bipartite, handle
    #   If Ci + {u} or Ci + {v} is bipartite, handle

    # Loop until no cuts of size 2 remain
    changed = False
    updated = True
    while(updated):
        updated = False

        # If the graph isn't 2-connected or if it's a clique on three vertices,
        # return the graph
        if graph.order() == 0 or \
           nx.node_connectivity(graph) != 2 or \
           graph.order() == 3:
            return changed, graph, oct_set

        # Else find a cut vertex and proceed
        node_u, node_v = list(nx.all_node_cuts(graph, k=2))[0]

        node_cuts = sort_collection_of_sets(nx.all_node_cuts(graph, k=2))
        while node_cuts and not updated:
            node_u, node_v = node_cuts.pop()

            remaining_nodes = set(graph.nodes())
            remaining_nodes.remove(node_u)
            remaining_nodes.remove(node_v)

            component_views = sort_collection_of_sets(
                nx.connected_components(graph.subgraph(remaining_nodes)))

            while component_views and not updated:
                # Find the nodes in a component of G - {u, v}
                component_nodes = set(component_views.pop())

                # The original component needs to be bipartite
                if nx.is_bipartite(graph.subgraph(component_nodes)):

                    # Case 1: Component + u + v is bipartite
                    component_nodes.add(node_u)
                    component_nodes.add(node_v)
                    if nx.is_bipartite(graph.subgraph(component_nodes)):
                        if len(component_nodes) > 3:
                            changed = True
                            updated = True
                            # Replace the component with one of equal parity.
                            # Check this by checking a 2-coloring of the
                            # component: If the neighborhood of {u, v} is one
                            # color then replace with a single new vertex.
                            # Otherwise replace with an edge.
                            # # print("component nodes before coloring:", component_nodes)
                            subgraph = graph.subgraph(component_nodes)
                            # # print("Subgraph: Nodes {} Edges {}".format(subgraph.nodes(), subgraph.edges()))
                            # # print("Connected?", nx.is_connected(graph.subgraph(component_nodes)))
                            coloring = nx.algorithms.bipartite.color(
                                graph.subgraph(component_nodes))

                            component_nodes.remove(node_u)
                            component_nodes.remove(node_v)
                            # # print("Coloring:",coloring)
                            # # print("v: {} u: {}".format(node_v, node_u))
                            if coloring[node_u] == coloring[node_v]:
                                new_midpoint = component_nodes.pop()
                                og_name_lookup = nx.get_node_attributes(
                                    graph, 'og_name')
                                og_name = og_name_lookup[new_midpoint]
                                graph.remove_node(new_midpoint)
                                graph.add_node(new_midpoint, og_name=og_name)
                                graph.add_edge(node_u, new_midpoint)
                                graph.add_edge(node_v, new_midpoint)
                            else:
                                graph.add_edge(node_u, node_v)

                            # In both cases, remove the component
                            # Update the preprocessing statistics
                            graph.graph['vertices_removed'] +=\
                                len(component_nodes)
                            graph.remove_nodes_from(component_nodes)
                        continue

                    # Case 2: Component + u is bipartite
                    component_nodes.remove(node_v)
                    if nx.is_bipartite(graph.subgraph(component_nodes)):
                        changed = True
                        updated = True

                        # Add v to OCT set
                        og_name_lookup = nx.get_node_attributes(graph,
                                                                'og_name')
                        oct_set.add(og_name_lookup[node_v])
                        graph.remove_node(node_v)

                        # Remove this component
                        component_nodes.remove(node_u)
                        graph.remove_nodes_from(component_nodes)

                        # Update preprocessing statistics
                        graph.graph['oct'] += 1
                        graph.graph['vertices_removed'] += len(component_nodes)
                        continue

                    # Case 3: Component + v is bipartite
                    component_nodes.remove(node_u)
                    component_nodes.add(node_v)
                    if nx.is_bipartite(graph.subgraph(component_nodes)):
                        changed = True
                        updated = True

                        # Add u to OCT set
                        og_name_lookup = nx.get_node_attributes(graph,
                                                                'og_name')
                        oct_set.add(og_name_lookup[node_u])
                        graph.remove_node(node_u)

                        # Remove component
                        component_nodes.remove(node_v)
                        graph.remove_nodes_from(component_nodes)

                        # Update preprocessing statistics
                        graph.graph['oct'] += 1
                        graph.graph['vertices_removed'] += len(component_nodes)
                        continue

    # print("Exited RR6")
    return changed, graph, oct_set


def reduction_rule_7(graph, oct_set):
    """
    Certain triangles can be reduced.
    """
    # print("Entered RR7")

    changed = False
    updated = True
    while updated:
        updated = False

        # Find a vertex node_w of degree 2
        degree_two_nodes = sorted(list(filter(
            lambda node: graph.degree(node) == 2, graph.nodes())))

        while degree_two_nodes and not updated:
            node_w = degree_two_nodes.pop()
            # Let node_v, node_u be node_w's neighbors, where deg(v) < deg(u)
            node_v, node_u = sorted(graph.neighbors(node_w),
                                    key=lambda node: graph.degree(node))
            # If there's an edge v-u and v has degree at most 3, we can reduce
            if graph.has_edge(node_v, node_u) and graph.degree(node_v) <= 3:
                changed = True
                updated = True

                # Add u to OCT set
                og_name_lookup = nx.get_node_attributes(graph, 'og_name')
                oct_set.add(og_name_lookup[node_u])

                # Remove all three nodes
                graph.remove_nodes_from([node_w, node_v, node_u])

                # Update preprocessing statistics
                graph.graph['vertices_removed'] += 2
                graph.graph['oct'] += 1

    # print("Exited RR7")
    return changed, graph, oct_set


def reduction_rule_8(graph, oct_set):
    """
    Certain 4-cycles can be reduced.
    """

    # print("Entered RR8")

    changed = False
    updated = True
    while updated:
        updated = False
        # Find a vertex node_w of degree 2
        degree_two_nodes = sorted(list(filter(
            lambda node: graph.degree(node) == 2, graph.nodes())))

        while degree_two_nodes and not updated:
            node_w = degree_two_nodes.pop()
            # Let u, v be w's neighbors, where deg(u) <= deg(v)
            node_u, node_v = sorted(graph.neighbors(node_w),
                                    key=lambda node: graph.degree(node))
            # Must be an induced 4-cycle (e.g. no u-v edge)
            if graph.has_edge(node_u, node_v):
                continue

            neighbors = sorted(list(graph.neighbors(node_u)))
            while neighbors and not updated:
                node_z = neighbors.pop()
                # See pseudocode in Wernicke's paper for details.
                # We do not need to check that the two degree 2 vertices are
                # across from each other because RR5 handles when they are
                # are adjacent.
                if graph.degree(node_z) == 2 and \
                   node_z != node_w and \
                   graph.has_edge(node_z, node_v):
                        changed = True
                        updated = True

                        # Remove and re-add z
                        og_name_lookup = nx.get_node_attributes(graph,
                                                                'og_name')
                        graph.remove_nodes_from([node_z, node_w])
                        graph.add_node(node_z,
                                       og_name = og_name_lookup[node_z])
                        graph.add_edge(node_u, node_z)
                        graph.add_edge(node_v, node_z)

                        # Update preprocessing statistics
                        graph.graph['vertices_removed'] += 1
    # print("Exited RR8")
    return changed, graph, oct_set


def reduction_rule_9(graph, oct_set):
    """
    Certain double-4-cycles can be reduced.
    """

    # print("Entered RR9")
    changed = False
    updated = True
    while updated:
        updated = False

        degree_three_nodes = sorted(list(filter(
            lambda node: graph.degree(node) == 3, graph.nodes())))

        while degree_three_nodes and not updated:
            node_z = degree_three_nodes.pop()
            degree_three_neighbors = sorted(list(filter(
                lambda node: graph.degree(node) == 3,
                graph.neighbors(node_z))))

            while degree_three_neighbors and not updated:
                node_z_prime = degree_three_neighbors.pop()
                # Note: These may be "swapped" from the labels in Wernicke's
                # Fig 6.8, because we don't know which vertex should be
                # labeled node_u, for example. Doesn't matter since we'll
                # try both combinations.
                node_w, node_x = sorted(list(filter(
                    lambda node: node != node_z_prime,
                    graph.neighbors(node_z))))
                node_u, node_v = sorted(list(filter(
                    lambda node: node != node_z,
                    graph.neighbors(node_z_prime))))

                # Check one configuration
                if (graph.has_edge(node_w, node_u) and
                   graph.has_edge(node_x, node_v) and
                   not graph.has_edge(node_w, node_x) and
                   not graph.has_edge(node_u, node_v)):
                    changed = True
                    updated = True
                    graph.remove_nodes_from([node_z, node_z_prime])
                    graph.add_edge(node_u, node_x)
                    graph.add_edge(node_w, node_v)
                    # Update preprocessing statistics
                    graph.graph['vertices_removed'] += 2

                # Check second configuration
                elif (graph.has_edge(node_w, node_v) and
                      graph.has_edge(node_x, node_u) and
                      not graph.has_edge(node_w, node_x) and
                      not graph.has_edge(node_u, node_v)):
                        changed = True
                        updated = True
                        graph.remove_nodes_from([node_z, node_z_prime])

                        # Should be this?:
                        graph.add_edge(node_v, node_x)
                        graph.add_edge(node_w, node_u)

                        # Update preprocessing statistics
                        graph.graph['vertices_removed'] += 2
    # print("Exited RR9")
    return changed, graph, oct_set


def oct_reductions(graph, oct_set):
    # We want to track if anything new happened, so we can repeat the other
    # reductions
    graph_reduced = False

    reductions = [reduction_rule_1, reduction_rule_2, reduction_rule_3,
                  reduction_rule_4, reduction_rule_5, reduction_rule_6,
                  reduction_rule_7, reduction_rule_8, reduction_rule_9]

    index = 0
    # Run each reduction one by one
    while index < len(reductions):
        # Run the "index"th reduction
        changed, graph, oct_set = reductions[index](graph, oct_set)
        # If the graph was changed, rerun the previous reductions
        if changed:
            graph_reduced = True
            index = 0
        # Else continue to the next reduction
        else:
            index += 1

    # Update the number of bipartite vertices, we may have removed some
    # previously marked as bipartite
    graph.graph['bipartite'] = len([x for x, y in graph.nodes(data=True) if
                                    'bipartite' in y])
    return graph_reduced, graph, oct_set


if __name__ == "__main__":
    pass
    # def read_edgelist(filename):
    #     graph = nx.Graph()
    #     with open(filename, "r") as infile:
    #         # Pull the top line from the edgelist
    #         num_vertices, num_edges = map(int, infile.readline().split())
    #
    #         # Add the nodes
    #         for i in range(num_vertices):
    #             graph.add_node(i)
    #
    #         # Add the edges
    #         for line in infile.readlines():
    #             graph.add_edge(*map(int, line.split()))
    #
    #     return graph
    #
    # def sitrep(label, graph, oct_set):
    #         # print("{}: |V|=".format(label), graph.order(),
    #               " |E|=", graph.size(),
    #               " #Components=", nx.number_connected_components(graph),
    #               " #oct= ", len(oct_set),
    #               " #not_oct=", len(nx.get_node_attributes(graph, "label")))
    #
    # # Graph where reduction rule 8 should apply. v and w have degree >=3
    # # and are connected as opposite edges on a 4 cycle.
    # oct_set = []
    # graph = nx.from_edgelist([
    #     ('u', 'v'),
    #     ('u', 'w'),
    #     ('v', 'z'),
    #     ('w', 'z'),
    #     ('v', '1'),
    #     ('w', '2')
    # ])
    #
    # graph.graph['vertices_removed'] = 0
    # graph.graph['edges_removed'] = 0
    # graph.graph['oct'] = 0
    # graph.graph['bipartite'] = 0
    #
    # sitrep('RR8: Should Apply - Before', graph, oct_set)
    # graph = reduction_rule_8(graph)
    # sitrep('RR8: Should Apply - After', graph, oct_set)
    #
    # # Graph where reduction rule 8 should not apply because of an induced
    # # 3 cycle.
    # oct_set = []
    # graph = nx.from_edgelist([
    #     ('u', 'v'),
    #     ('u', 'w'),
    #     ('v', 'z'),
    #     ('w', 'z'),
    #     ('u', 'z')  # Form a 3 cycle by connecting u and z
    # ])
    #
    # graph.graph['vertices_removed'] = 0
    # graph.graph['edges_removed'] = 0
    # graph.graph['oct'] = 0
    # graph.graph['bipartite'] = 0
    #
    # sitrep('RR8: Should Not Apply By 3 Cycle - Before', graph, oct_set)
    # graph = reduction_rule_8(graph)
    # sitrep('RR8: Should Not Apply By 3 Cycle - After', graph, oct_set)
    #
    # oct_set = []
    # graph = nx.from_edgelist([
    #     ('u', 'z1'),
    #     ('z1', 'v'),
    #     ('w', 'z'),
    #     ('z', 'x'),
    #     ('u', 'w'),
    #     ('z1', 'z'),
    #     ('v', 'x')
    # ])
    #
    # graph.graph['vertices_removed'] = 0
    # graph.graph['edges_removed'] = 0
    # graph.graph['oct'] = 0
    # graph.graph['bipartite'] = 0
    #
    # sitrep('RR9: Should Apply - Before', graph, oct_set)
    # graph = reduction_rule_9(graph)
    # sitrep('RR9: Should Apply - After', graph, oct_set)
    #
    # oct_set = []
    # graph = nx.from_edgelist([
    #     ('u', 'z1'),
    #     ('z1', 'v'),
    #     ('w', 'z'),
    #     ('z', 'x'),
    #     ('u', 'w'),
    #     ('z1', 'z'),
    #     ('v', 'x'),
    #     ('w', 'x')  # Connect w and x
    # ])
    #
    # graph.graph['vertices_removed'] = 0
    # graph.graph['edges_removed'] = 0
    # graph.graph['oct'] = 0
    # graph.graph['bipartite'] = 0
    #
    # sitrep('RR9: Should Not Apply By Edge - Before', graph, oct_set)
    # graph = reduction_rule_9(graph)
    # sitrep('RR9: Should Not Apply By Edge - After', graph, oct_set)

    # # Read the dataset into a NetworkX graph
    # DATASET = "data/converted/edgelist/aa41.edgelist"
    # graph = read_edgelist(DATASET)
    # oct_set = []
    #
    # # print("Dataset:", DATASET.split("/")[-1])
    # sitrep("Initially", graph, oct_set)
    #
    # graph = reduction_rule_1(graph)
    # sitrep("After RR1", graph, oct_set)
    #
    # graph = reduction_rule_2(graph)
    # sitrep("After RR2", graph, oct_set)
    #
    # graph = reduction_rule_3(graph)
    # sitrep("After RR3", graph, oct_set)
    #
    # graph, oct_set = reduction_rule_4(graph, oct_set)
    # sitrep("After RR4", graph, oct_set)
    #
    # graph = reduction_rule_5(graph)
    # sitrep("After RR5", graph, oct_set)
    #
    # graph, oct_set = reduction_rule_6(graph, oct_set)
    # sitrep("After RR6", graph, oct_set)
    #
    # graph, oct_set = reduction_rule_7(graph, oct_set)
    # sitrep("After RR7", graph, oct_set)
    #
    # graph = reduction_rule_8(graph)
    # sitrep("After RR8", graph, oct_set)
    #
    # graph = reduction_rule_9(graph)
    # sitrep("After RR9", graph, oct_set)

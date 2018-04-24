#include "Heuristics.hpp"

std::vector<int> max_greedy_bipartite(Graph &graph, int num_seeds)
{

    std::vector<int> best;

    for (int seed = 0; seed < num_seeds; ++seed)
    {
        std::vector<int> result = greedy_bipartite(graph, seed);
        if (result.size() > best.size()) best = result;
    }

    return best;

}

/* Computes two independent sets and returns their union
   Uses min_degree_ind_set */
std::vector<int> greedy_bipartite(Graph &graph, int seed)
{
    srand(seed);
    /* Create two copy graphs to use and two independent set vectors */
    std::vector<int> ind_set1;
    std::vector<int> ind_set2;
    Graph graph1 = graph;
    Graph graph2 = graph;

    /* Construct the first independent set */
    ind_set1 = min_degree_ind_set(graph1);

    /* Remove the first independent set from the second graph */

    for (int vertex : ind_set1)
    {
        graph2.remove_vertex(vertex);
    }

    /* Construct the second independent set */
    ind_set2 = min_degree_ind_set(graph2);

    ind_set1.insert(ind_set1.begin(), ind_set2.begin(), ind_set2.end());
    return ind_set1;
}

/* Computes one ind set by iteratively choosing a min degree vertex */
std::vector<int> min_degree_ind_set(Graph &graph)
{
    std::vector<int> result;

    /* Initialize the currently unused vertices */
    std::set<int> vertices;
    for (int vertex = 0; vertex < graph.get_num_vertices(); ++vertex)
    {
        if (graph.is_active(vertex))
        {
            vertices.insert(vertex);
        }
    }

    while (vertices.size() > 0) {

        /* Choose a random min degree vertex */
        auto min_degree_vertices = graph.get_min_degree_vertices();
        int random_index = rand() % min_degree_vertices.size();
        int chosen_vertex = min_degree_vertices[random_index];

        /* Remove this vertex and its neighbors */
        auto neighbors = graph.get_neighbors(chosen_vertex);
        graph.remove_vertex(chosen_vertex);
        vertices.erase(chosen_vertex);

        for (int neighbor : neighbors)
        {
            graph.remove_vertex(neighbor);
            vertices.erase(neighbor);
        }

        /* Add the chosen vertex to the independent set */
        result.push_back(chosen_vertex);
    }

    return result;
}


std::vector<int> max_greedy_stochastic(Graph &graph, int seeds) {

    std::vector<int> best;

    for (int i = 0; i < seeds; ++i) {
        std::vector<int> result = greedy_stochastic(graph, i);
        if (result.size() > best.size()) best = result;
    }

    return best;

}


/* Computes two independent sets and returns their union
   Uses luby_ind_set
*/
std::vector<int> greedy_stochastic(Graph &graph, int seed) {
    srand(seed);
    /* Create two copy graphs to use and two independent set vectors */
    Graph graph1 = graph;
    Graph graph2 = graph;

    // Independent sets
    std::vector<int> ind_set1;
    // ind_set1.resize(graph.get_num_vertices());
    std::vector<int> ind_set2;
    // ind_set2.resize(graph.get_num_vertices());

    /* Construct the first independent set */
    luby_ind_set(graph1, ind_set1);

    /* Remove the first independent set from the second graph */
    for (std::vector<int>::iterator it = ind_set1.begin(); \
      it != ind_set1.end(); ++it) {
        graph2.remove_vertex(*it);
     }
    /* Construct the second independent set */
    luby_ind_set(graph2, ind_set2);

    // Concat independent sets and return
    ind_set1.insert(ind_set1.begin(), ind_set2.begin(), ind_set2.end());
    return ind_set1;

}

void luby_ind_set(Graph &graph, std::vector<int> &result) {
    // S = new set
    // S' = new set
    // for vertex in vertices:
    //    vertex goes into S with prob 1/2d(v)
    // for vertex in S:
    //    for neighbor in N(vertex):
    //        if neighbor in S && neighbor not in S' && d(vertex) < d(neighbor):
    //           continue ("going to add neighbor")
    //    S'.insert(vertex) ("if we got here, we're good")
    // S' is the "chosen_vertex"

    std::set<int> vertices;
    std::set<int> initial_chosen_vertices;
    std::set<int> chosen_vertices;

    /* Initialize the currently unused vertices */
    /* TODO: Move this internal to the graph class */
    for (int i = 0; i < graph.get_num_vertices(); i++) {
        if (graph.is_active(i)) {
            vertices.insert(i);
        }
    }

    while (vertices.size() > 0) {
        //fprintf(stderr, "Vertices left: %d\n", vertices.size());

        initial_chosen_vertices.clear();
        chosen_vertices.clear();

        /* Select the next vertices to be added to the ind set */
        for (std::set<int>::iterator vertex = vertices.begin();
            vertex != vertices.end(); ++vertex)
        {
            // Add vertex if it has no neighbors, or otherwise with probability 1 / (2 * degree(vertex))
            if (graph.get_degree(*vertex) == 0 ||
                (double) rand() / (RAND_MAX) <= 1.0 / (2 * graph.get_degree(*vertex)))
            {
                initial_chosen_vertices.insert(*vertex);
                //fprintf(stderr, "Selecting vertex %d\n", *vertex);
            }
        }

        /* Resolve any conflicts in the selected set */
        bool keep;
        for (std::set<int>::iterator vertex = initial_chosen_vertices.begin();
            vertex != initial_chosen_vertices.end(); ++vertex) {
            std::set<int> neighbors = graph.get_neighbors(*vertex);

            keep = true;
            for (std::set<int>::iterator neighbor = neighbors.begin();
                neighbor != neighbors.end(); ++neighbor)
            {
                if ( (initial_chosen_vertices.find(*neighbor) != initial_chosen_vertices.end()) \
                    && ( chosen_vertices.find(*neighbor) != chosen_vertices.end() \
                    ||  graph.get_degree(*vertex) < graph.get_degree(*neighbor)) ) {
                        //fprintf(stderr, "Found a conflict: %d, %d\n", *vertex, *neighbor);
                        keep = false;
                        break;
                }
            }
            if (keep) {
                //fprintf(stderr, "Selecting to keep %d\n", *vertex);
                chosen_vertices.insert(*vertex);
            }
        }

        /* Remove the selected vertices and their neighbors from the graph */
        for (std::set<int>::iterator vertex = chosen_vertices.begin();
            vertex != chosen_vertices.end(); ++vertex)
        {
            /* Remove this vertex and its neighbors */
            std::set<int> neighbors = graph.get_neighbors(*vertex);
            graph.remove_vertex(*vertex);
            vertices.erase(*vertex);
            //fprintf(stderr, "Removing vertex %d\n", *vertex);

            for (std::set<int>::iterator neighbor = neighbors.begin(); \
                neighbor != neighbors.end(); ++neighbor) {
                    //fprintf(stderr, "   Removing neighbor %d\n", *neighbor);
                  graph.remove_vertex(*neighbor);
                  vertices.erase(*neighbor);
            }

            /* Add the chosen vertex to the independent set */
            result.push_back(*vertex);
        }
    }
}

/**
 * Perform a greedy two-coloring by traversing the graph using DFS.
 * If at any point some vertex cannot be given a valid color, add it to OCT.
 *
 * @param  input_graph          Input graph.
 * @param  seed                 Random seed.
 * @return                      List of vertices in not in OCT.
 */
std::vector<int> greedy_dfs_bipartite(Graph &input_graph, int seed) {

    // Seed rand
    srand(seed);

    // Copy graph for private modification
    Graph graph(input_graph);

    // Assigned colors. Default everything to 0 = no color
    std::unordered_map<int, int> colors;
    for (int i = 0; i < graph.get_num_vertices(); i++) colors[i] = 0;

    // Initialize all vertices as not visited
    std::set<int> not_visited;
    for (int i = 0; i < graph.get_num_vertices(); i++) not_visited.insert(i);

    // Keep iterating until all vertices are visited.
    // This accounts for disconnected components.
    while (not_visited.size()) {

        // Get random index into not visited set
        long idx = rand() % not_visited.size();

        // Create iterator and advance it
        auto iterator = not_visited.begin();
        std::advance(iterator, idx);

        // Get root vertex at idx using the iterator
        int root = *(iterator);

        // Push to DFS stack
        std::stack<int> vertices;
        vertices.push(root);

        // Start performing DFS
        while (vertices.size()) {

            // Get vertex on top of stack, then pop it off of the stack and
            // delete it from not visited set.
            int vertex = vertices.top();
            vertices.pop();

            // If this vertex was visited by some other branch while it was
            // sitting on the stack, skip. We shouldn't visit twice. Otherwise,
            // remove this vertex from the not visited set.
            if (not_visited.find(vertex) == not_visited.end()) {
                continue;
            }
            else {
                not_visited.erase(vertex);
            }

            // Get all neighbors of vertex
            auto neighbors = graph.get_neighbors(vertex);

            // Whether or not some neighbor has some color
            bool neighbor_colored_1 = false;
            for (auto n : neighbors) {
                if (colors[n] == 1) neighbor_colored_1 = true;
            }
            bool neighbor_colored_2 = false;
            for (auto n : neighbors) {
                if (colors[n] == 2) neighbor_colored_2 = true;
            }

            // Assign color to vertex, or add it to OCT
            if (!neighbor_colored_1) {
                colors[vertex] = 1;
            }
            else if (!neighbor_colored_2) {
                colors[vertex] = 2;
            }
            else {
                graph.remove_vertex(vertex);
            }

            // Push neighbors to stack if they haven't already been visited
            for (auto n : neighbors) {
                if (not_visited.find(n) != not_visited.end()) {
                    vertices.push(n);
                }
            }

        }

    }

    // Return vertices remaining in graph.
    return graph.get_vertices();

}

/**
 * Perform a greedy two-coloring by traversing the graph using BFS.
 * If at any point some vertex cannot be given a valid color, add it to OCT.
 *
 * @param  input_graph          Input graph.
 * @param  seed                 Random seed.
 * @return                      List of vertices not in OCT.
 */
std::vector<int> greedy_bfs_bipartite(Graph &input_graph, int seed) {

    // Seed rand
    srand(seed);

    // Copy graph for private modification
    Graph graph(input_graph);

    // Assigned colors. Default everything to 0 = no color
    std::unordered_map<int, int> colors;
    for (int i = 0; i < graph.get_num_vertices(); i++) colors[i] = 0;

    // Initialize all vertices as not visited
    std::set<int> not_visited;
    for (int i = 0; i < graph.get_num_vertices(); i++) not_visited.insert(i);

    // Keep iterating until all vertices are visited.
    // This accounts for disconnected components.
    while (not_visited.size()) {

        // Get random index into not visited set
        long idx = rand() % not_visited.size();

        // Create iterator and advance it
        auto iterator = not_visited.begin();
        std::advance(iterator, idx);

        // Get root vertex at idx using the iterator
        int root = *(iterator);

        // Push to BFS queue
        std::queue<int> vertices;
        vertices.push(root);

        // Start performing DFS
        while (vertices.size()) {

            // Get vertex on front of queue, then pop it off of the stack and
            // delete it from not visited set.
            int vertex = vertices.front();
            vertices.pop();

            // If this vertex was visited by some other branch while it was
            // sitting on the queue, skip. We shouldn't visit twice. Otherwise,
            // remove this vertex from the not visited set.
            if (not_visited.find(vertex) == not_visited.end()) {
                continue;
            }
            else {
                not_visited.erase(vertex);
            }

            // Get all neighbors of vertex
            auto neighbors = graph.get_neighbors(vertex);

            // Whether or not some neighbor has some color
            bool neighbor_colored_1 = false;
            for (auto n : neighbors) {
                if (colors[n] == 1) neighbor_colored_1 = true;
            }
            bool neighbor_colored_2 = false;
            for (auto n : neighbors) {
                if (colors[n] == 2) neighbor_colored_2 = true;
            }

            // Assign color to vertex, or add it to OCT
            if (!neighbor_colored_1) {
                colors[vertex] = 1;
            }
            else if (!neighbor_colored_2) {
                colors[vertex] = 2;
            }
            else {
                graph.remove_vertex(vertex);
            }

            // Push neighbors to stack if they haven't already been visited
            for (auto n : neighbors) {
                if (not_visited.find(n) != not_visited.end()) {
                    vertices.push(n);
                }
            }

        }

    }

    // Return vertices remaining in graph.
    return graph.get_vertices();

}

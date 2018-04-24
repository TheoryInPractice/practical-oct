#include "Graph.hpp"


Graph::Graph(std::string filename)
{
    std::ifstream infile(filename);
    int num_vertices, num_edges;
    infile >> num_vertices >> num_edges;

    this->num_vertices = num_vertices;
    neighbors.resize(num_vertices);
    vertices_active = std::vector<bool>(num_vertices, true);

    int vertex_1 = -1, vertex_2 = -1;
    while(infile.good())
    {
      infile >> vertex_1 >> vertex_2;
      if (vertex_1 != -1 && vertex_2 != -1) add_edge(vertex_1, vertex_2);
    }
    infile.close();
}

void Graph::add_edge(int vertex_1, int vertex_2)
{
    neighbors.at(vertex_1).insert(vertex_2);
    neighbors.at(vertex_2).insert(vertex_1);
}

bool Graph::has_edge(int vertex_1, int vertex_2)
{
    return neighbors[vertex_1].find(vertex_2) != neighbors[vertex_1].end();
}

void Graph::remove_edge(int vertex_1, int vertex_2)
{
    neighbors.at(vertex_1).erase(vertex_2);
    neighbors.at(vertex_2).erase(vertex_1);
}

void Graph::remove_vertex(int vertex)
{
    if (!is_active(vertex)) {
        return;
    }

    /* Wipe all edges involving this vertex */
    for (auto neighbor : neighbors[vertex])
    {
          neighbors[neighbor].erase(vertex);
    }
    /* May also want to wipe neighbors[vertex]? */
    vertices_active[vertex] = false;
}

int Graph::get_num_vertices()
{
    return num_vertices;
}

int Graph::get_num_edges()
{
    int result = 0;
    for (int vertex = 0; vertex < num_vertices; ++vertex)
    {
        result += neighbors[vertex].size();
    }
    return result / 2;
}

std::set<int> Graph::get_neighbors(int vertex)
{
    return neighbors[vertex];
}

int Graph::get_degree(int vertex)
{
    return neighbors[vertex].size();
}

std::vector<int> Graph::get_min_degree_vertices()
{
    std::vector<int> result;
    result.resize(num_vertices);
    int min_degree = num_vertices;
    for (int i = 0; i < num_vertices; ++i)
    {
        if (vertices_active[i]) {
            int degree = neighbors[i].size();
            if (degree < min_degree) {
                result.clear();
                min_degree = degree;
                result.push_back(i);
            } else if (degree == min_degree)
            {
                result.push_back(i);
            }
        }
    }
    return result;
}

/**
 * Provides a vector containing all vertices currently marked as active.
 *
 * @return Vector of active vertices.
 */
std::vector<int> Graph::get_vertices()
{
    std::vector<int> vertices;
    for (int i = 0; i < get_num_vertices(); i++) {
        if (is_active(i)) vertices.push_back(i);
    }
    return vertices;
}

bool Graph::is_active(int vertex)
{
    return vertices_active[vertex];
}

void Graph::print_stats()
{
    std::cout << "This graph has:" << std::endl;
    std::cout << " - " << num_vertices << " vertices" << std::endl;
    for (int i = 0; i < num_vertices; ++i)
    {
      std::cout << " - Vertex " << i << " has " << neighbors[i].size() << " neighbors" << std::endl;
    }
}

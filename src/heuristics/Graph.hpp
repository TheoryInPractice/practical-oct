#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <cstddef>
#include <set>
#include <vector>
#include <fstream>
#include <string>
#include <iostream>

#include "Debug.hpp"

class Graph {
    int num_vertices;
    std::vector<std::set<int>> neighbors;
    std::vector<bool> vertices_active;

  public:
    Graph(int num_vertices);
    Graph(std::string filename);
    void add_edge(int vertex_1, int vertex_2);
    bool has_edge(int vertex_1, int vertex_2);
    void remove_edge(int vertex_1, int vertex_2);
    void remove_vertex(int vertex);
    std::set<int> get_neighbors(int vertex);
    int get_degree(int vertex);
    int get_num_vertices();
    int get_num_edges();
    std::vector<int> get_min_degree_vertices();
    std::vector<int> get_vertices();
    bool is_active(int vertex);
    void print_stats();
};

#endif

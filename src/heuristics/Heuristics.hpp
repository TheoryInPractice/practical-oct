#ifndef HEURISTICS_HPP
#define HEURISTICS_HPP


#include <algorithm>
#include <random>
#include <utility>
#include <vector>
#include <iostream>
#include <queue>
#include <stack>
#include <unordered_map>
#include <unordered_set>

#include "Debug.hpp"
#include "Graph.hpp"

std::vector<int> max_greedy_bipartite(Graph &graph, int num_seeds);
std::vector<int> greedy_bipartite(Graph &graph, int seed);
std::vector<int> min_degree_ind_set(Graph &graph);
std::vector<int> max_greedy_stochastic(Graph &graph, int seeds);
std::vector<int> greedy_stochastic(Graph &graph, int seed);
void luby_ind_set(Graph &graph, std::vector<int> &result);
std::vector<int> greedy_dfs_bipartite(Graph &graph, int seed);
std::vector<int> greedy_bfs_bipartite(Graph &graph, int seed);

#endif

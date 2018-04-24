#ifndef DEBUG_HPP
#define DEBUG_HPP

#include <algorithm>
#include <string>
#include <vector>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <set>

void print(std::string text);
void print_vector(std::string label, std::unordered_set<int> list);
void print_vector(std::string label, std::vector<int> list);
void print_vector(std::string label, std::vector<std::string> list);
void print_vector(std::string label, std::set<int> list);
void print_vector(std::string label, std::pair<std::vector<int>,
    std::vector<int>> lists);
void print_sorted_vector(std::string label, std::vector<int> list);
void print_sorted_vector(std::string label, std::pair<std::vector<int>,
    std::vector<int>> lists);

void print_hardcode(std::string label, std::vector<int> list);
void print_hardcode(std::string label, std::set<int> list);

#endif

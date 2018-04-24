#include "Debug.hpp"

void print(std::string text)
{
  std::cout << text << std::endl;
}

void print_vector(std::string label, std::unordered_set<int> list)
{
    std::cout << label;
    for (auto item : list)
    {
        std::cout << " " << item;
    }
    std::cout << std::endl;
}


void print_vector(std::string label, std::vector<int> list)
{
    std::cout << label;
    for (auto item : list)
    {
        std::cout << " " << item;
    }
    std::cout << std::endl;
}

void print_vector(std::string label, std::vector<std::string> list)
{
    std::cout << label;
    for (auto item : list)
    {
        std::cout << " " << item;
    }
    std::cout << std::endl;
}

void print_vector(std::string label, std::set<int> list)
{
    std::cout << label;
    for (auto item : list)
    {
        std::cout << " " << item;
    }
    std::cout << std::endl;
}

void print_vector(std::string label, std::pair<std::vector<int>,
    std::vector<int>> lists)
{

    std::cout << label;
    for (auto item : lists.first)
    {
        std::cout << " " << item;
    }
    std::cout << " |";
    for (auto item : lists.second)
    {
        std::cout << " " << item;
    }
    std::cout << std::endl;
}

void print_sorted_vector(std::string label, std::vector<int> list)
{
    std::sort(list.begin(), list.end());
    std::cout << label;
    for (auto item : list)
    {
        std::cout << " " << item;
    }
    std::cout << std::endl;
}

void print_hardcode(std::string label, std::vector<int> list)
{
    std::sort(list.begin(), list.end());
    std::cout << label;
    std::cout << "{";
    for (auto item : list)
    {
        std::cout << " " << item << ",";
    }
    std::cout << "} size: " << list.size();
    std::cout << std::endl;
}

void print_hardcode(std::string label, std::set<int> list)
{
    std::cout << label;
    std::cout << "{";
    for (auto item : list)
    {
        std::cout << " " << item << ",";
    }
    std::cout << "} size: " << list.size();
    std::cout << std::endl;
}

void print_sorted_vector(std::string label, std::pair<std::vector<int>,
    std::vector<int>> lists)
{
    std::sort(lists.first.begin(), lists.first.end());
    std::sort(lists.second.begin(), lists.second.end());

    std::cout << label;
    for (auto item : lists.first)
    {
        std::cout << " " << item;
    }
    std::cout << " |";
    for (auto item : lists.second)
    {
        std::cout << " " << item;
    }
    std::cout << std::endl;
}

#include <array>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <chrono>
#include <sstream>
#include <set>
#include "Debug.hpp"
#include "Ensemble.hpp"
#include "Graph.hpp"
#include "Heuristics.hpp"


// Use standard namespace
using namespace std;


/**
 * Main Function.
 */
int main(int argc, char *argv[])
{

    // Validate arguments
    if (argc != 3) {
        cout << "Usage: heuristic_solver <timelimit> <datafile>" << endl;
        return 1;
    }
    long timeout = stol(argv[1]);
    string data = argv[2];

    // Load graph file
    Graph graph(data);

    // If graph is empty, terminate early
    if (!graph.get_num_vertices()) {
        cout << "0,0,\"[]\"" << endl;
        return 0;
    }

    // Create ensemble solver
    EnsembleSolver ensemble;

    // Compute ensemble
    auto ensemble_result = ensemble.heuristic_solve(graph, timeout);

    // Get results
    auto certificate = get<0>(ensemble_result);
    auto solution_time = get<1>(ensemble_result);

    // Convert certificate to string
    ostringstream certificate_stream;
    certificate_stream << "\"[";
    for (int i = 0; i < certificate.size(); i++) {
        certificate_stream << certificate[i];
        if (i != certificate.size() - 1) certificate_stream << ",";
    }
    certificate_stream << "]\"";

    // Print Results
    cout << certificate.size() << "," << solution_time << "," << certificate_stream.str() << endl;

    // Exit success
    return 0;

}

#ifndef ENSEMBLE_HPP
#define ENSEMBLE_HPP


// Includes
#include <chrono>
#include <iostream>
#include <tuple>
#include <vector>
#include "Graph.hpp"
#include "Heuristics.hpp"


// Use standard namespace
using namespace std;


// Typedefs
typedef chrono::high_resolution_clock Clock;


/**
 * Ensemble solver.
 */
class EnsembleSolver {

    public:
        tuple<vector<int>, long> heuristic_solve(Graph &, long);

};


#endif

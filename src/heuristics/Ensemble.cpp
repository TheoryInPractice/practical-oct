#include "Ensemble.hpp"


/**
 * Run heuristics until reaching timeout. Then return the best result found
 * for each heuristic. Best result is reported as the smallest OCT, the
 * inverse of the result reported by the heuristic functions.
 *
 * @param  timeout  Timeout in milliseconds.
 * @return          Tuple consisting of (oct size, seconds).
 */
tuple<vector<int>, long> EnsembleSolver::heuristic_solve(Graph &graph, long timeout)
{

    // List of solvers
    vector<vector<int> (*)(Graph &, int)> solvers = {
        greedy_bipartite,
        greedy_stochastic,
        greedy_dfs_bipartite,
        greedy_bfs_bipartite
    };

    // Starting index
    int idx = 0;

    // Start seed at 0
    long seed = 0;

    // Initialize results
    vector<int> best;
    long totalTime;

    // Time
    const auto start = Clock::now();

    // While duration is less than timeout
    while (chrono::duration_cast<chrono::milliseconds>(Clock::now() - start).count() < timeout) {

        // Compute greedy bipartite
        auto result = solvers[idx](graph, seed);

        // Record results, and get the current time
        if (result.size() > best.size()) {
            best = result;
            totalTime = chrono::duration_cast<chrono::milliseconds>(Clock::now() - start).count();
        }

        // Increment solver index
        idx = (idx + 1) % solvers.size();

        // Increment seed
        seed++;

    }

    // OCT results
    vector<int> oct, range;

    // Create vector of all vertices
    range.resize(graph.get_num_vertices());
    iota(range.begin(), range.end(), 0);

    // Sort best solutions
    sort(best.begin(), best.end());

    // Compute OCT
    set_difference(
        range.begin(), range.end(),
        best.begin(), best.end(),
        inserter(oct, oct.begin())
    );

    // Return dictionary of results
    return make_tuple(oct, totalTime);

}

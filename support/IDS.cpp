#include "IDS.hpp"
#include "DLS.hpp"

#include <ctime>
#include <algorithm>

SearchResult solveIDS(const Board& startState, const Board& goalState, int maxLimit) {
    SearchResult idsResult;
    
    std::clock_t startTime = std::clock();

    for (int depthLimit = 0; depthLimit < maxLimit; ++depthLimit) {
        SearchResult dlsResult = solveDLS(startState, goalState, depthLimit);

        idsResult.statesRemoved += dlsResult.statesRemoved;

        idsResult.maxFrontierSize = std::max(idsResult.maxFrontierSize, 
                                             dlsResult.maxFrontierSize);

        if (dlsResult.found) {
            idsResult.found = true;
            idsResult.path = dlsResult.path;
            break;
        }
    }

    std::clock_t endTime = std::clock();

    idsResult.cpuTime =
        static_cast<double>(endTime - startTime)
        / CLOCKS_PER_SEC;

    return idsResult;
}
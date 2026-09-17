#include "DLS.hpp"

#include <stack>
#include <ctime>

SearchResult solveDLS(const Board& startState, const Board& goalState, int depthLimit) {
    SearchResult result;

    std::clock_t startTime = std::clock();

    std::stack<Node> frontier;

 Node startNode;
    startNode.board = startState;
    startNode.path = "";
    startNode.depth = 0;
    startNode.previousMove = '\0';

    frontier.push(startNode);

    result.maxFrontierSize = frontier.size();

    while (!frontier.empty()) {
        Node current = frontier.top();
        frontier.pop();
        ++result.statesRemoved;

        if (current.board == goalState) {
            std::clock_t endTime = std::clock();
            result.cpuTime = static_cast<double>(endTime - startTime) / CLOCKS_PER_SEC;
            result.found = true;
            result.path = current.path;
            return result;
        }

        if (current.depth >= depthLimit) {
            continue;
        }

//         Use a one-move puzzle with limit 0: solution should not be found.
// Use the same puzzle with limit 1: solution should be found.
// Use a two-move puzzle with limit 1: solution should not be found.
// Use that puzzle with limit 2: solution should be found.

        for (const Node& child : successors(current)) {
            frontier.push(child);
        }

        if (frontier.size() > result.maxFrontierSize) {
            result.maxFrontierSize = frontier.size();
        }
    }

    std::clock_t endTime = std::clock();

    result.cpuTime =
        static_cast<double>(endTime - startTime)
        / CLOCKS_PER_SEC;

    return result;
}
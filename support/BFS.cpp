#include "BFS.hpp"

#include <queue>
#include <ctime>

SearchResult solveBFS(const Board& startState, const Board& goalState) {
    SearchResult result;

    std::clock_t startTime = std::clock();

    std::queue<Node> frontier;
    
    Node startNode;
    startNode.board = startState;
    startNode.path = "";
    startNode.depth = 0;
    startNode.previousMove = '\0';

    frontier.push(startNode);

    result.maxFrontierSize = frontier.size();

    while (!frontier.empty()) {
        Node current = frontier.front();
        frontier.pop();
        ++result.statesRemoved;

        if (current.board == goalState) {
            std::clock_t endTime = std::clock();
            result.cpuTime = static_cast<double>(endTime - startTime) / CLOCKS_PER_SEC;
            result.found = true;
            result.path = current.path;
            return result;
        }

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

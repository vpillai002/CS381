#include "IDS.hpp"
#include <stack>

SearchResult solveIDS(const Board& startState, const Board& goalState, int maxLimit = 30) {
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

    for (size_t i = 0; i < maxLimit; ++i) {
        
    }

    // while (!frontier.empty()) {
    //     Node current = frontier.top();
    //     frontier.pop();
    //     ++result.statesRemoved;

    //     if (current.board == goalState) {
    //         std::clock_t endTime = std::clock();
    //         result.cpuTime = static_cast<double>(endTime - startTime) / CLOCKS_PER_SEC;
    //         result.found = true;
    //         result.path = current.path;
    //         return result;
    //     }

    //     if (current.depth >= depthLimit) {
    //         continue;
    //     }

    //     for (const Node& child : successors(current)) {
    //         frontier.push(child);
    //     }

    //     if (frontier.size() > result.maxFrontierSize) {
    //         result.maxFrontierSize = frontier.size();
    //     }
    // }

    std::clock_t endTime = std::clock();

    result.cpuTime =
        static_cast<double>(endTime - startTime)
        / CLOCKS_PER_SEC;

    return result;
}

// def ids(start, goal, max_limit=30):
//     # Normalize the boards once for all search iterations.
//     start = tuple(tuple(row) for row in start)
//     goal = tuple(tuple(row) for row in goal)

//     total_expanded = 0
//     max_stack_size = 0
//     start_time = time.perf_counter()

//     # Try every depth from zero through the allowed maximum.
//     for depth_limit in range(max_limit + 1):
//         result = dls(start, goal, depth_limit)
//         total_expanded += result["expanded"]
//         max_stack_size = max(max_stack_size, result["max_stack_size"])

//         # Return the first solution, including totals from all iterations.
//         if result["found"]:
//             result["expanded"] = total_expanded
//             result["max_stack_size"] = max_stack_size
//             result["time_taken"] = time.perf_counter() - start_time
//             return result

//     # No iteration found a solution within max_limit.
//     return {
//         "found": False,
//         "moves": "",
//         "expanded": total_expanded,
//         "max_stack_size": max_stack_size,
//         "time_taken": time.perf_counter() - start_time,
//         "limit": max_limit,
//     }
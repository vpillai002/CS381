#ifndef PUZZLE_H
#define PUZZLE_H

#include <vector>
#include <string>
#include <cstddef>

using Board = std::vector<std::vector<int>>;

struct Node {
    Board board;
    std::string path;
    int depth;
    char previousMove;
};

struct SearchResult {
    bool found = false;
    std::string path;
    std::size_t statesRemoved = 0;
    std::size_t maxFrontierSize = 0;
    double cpuTime = 0.0;
};

std::vector<std::vector<int>> parseBoard(const std::string& input);

// Move letters describe the blank tile's movement.
std::vector<Node> successors(const Node& node);



#endif // PUZZLE_H

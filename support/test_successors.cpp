#include <iostream>
#include "puzzle.hpp"

int main() {
    Board board = {
        {1, 2, 3, 4},
        {5, 0, 6, 8},
        {9, 10, 7, 11},
        {13, 14, 15, 12}
    };

    Node start{board, "", 0, '\0'};

    std::vector<Node> children = successors(start);

    std::cout << "Number of children: "
              << children.size() << "\n";

    for (const Node& child : children) {
        std::cout << "Path: " << child.path
                  << ", depth: " << child.depth
                  << ", previous move: " << child.previousMove
                  << "\n";
    }

    if (!children.empty()) {
        std::vector<Node> grandchildren = successors(children[0]);

        std::cout << "Children of first child: "
                  << grandchildren.size() << "\n";
    }
}
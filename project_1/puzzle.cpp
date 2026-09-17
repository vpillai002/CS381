#include "puzzle.hpp"

#include <iostream>
#include <cctype>
#include <stdexcept>



std::vector<std::vector<int>> parseBoard(const std::string& input) {
    std::vector<std::vector<int>> _board;
    std::vector<int> row;
    std::string number;

    for (char c : input) {
        if (std::isdigit(c)) {
            number += c;
        }
        else {
            if (!number.empty()) {
                int value = std::stoi(number);

                if (value < 0 || value > 15) {
                    throw std::invalid_argument("Input values outside the range 0 - 15.");
                }
                row.push_back(value);
                number.clear();
            }

            if (c == ']' && !row.empty()) {
                _board.push_back(row);
                row.clear();
            }
        }
    }
    return _board;
}

char inverseMove(char move) {
    if (move == 'U') return 'D';
    if (move == 'D') return 'U';
    if (move == 'L') return 'R';
    if (move == 'R') return 'L';

    return '\0';
}

std::vector<Node> successors(const Node& node) {
    std::vector<Node> children;

    std::size_t blankRow = 0;
    std::size_t blankColumn = 0;
    bool foundBlank = false;

    for (std::size_t row = 0; row < node.board.size(); ++row) {
        for (std::size_t column = 0; column < node.board[row].size(); ++column) {
            if (node.board[row][column] == 0) {
                blankRow = row;
                blankColumn = column;
                foundBlank = true;
                break;
            }
        }
        // Exit outer loop when blank found.
        if (foundBlank) {
            break;
        }
    }

    // check for invalid boards.
    if (!foundBlank) {
        return children;
    }

    char forbiddenMove = inverseMove(node.previousMove);

    struct Move {
        int rowChange;
        int colChange;
        char direction;
    };

    std::vector<Move> moves = {
        {-1, 0, 'U'}, // move up
        {1, 0, 'D'}, // move down
        {0, -1, 'L'}, // move left
        {0, 1, 'R'} // move right
    };

    for (const Move& move : moves) {

        int newRow = static_cast<int>(blankRow) + move.rowChange;
        int newCol = static_cast<int>(blankColumn) + move.colChange;

        if (move.direction == forbiddenMove) {
            continue;
        }

        // boundary check
        if (newRow < 0 || newRow >= 4 ||
            newCol < 0 || newCol >= 4) {
                continue;
            }
        
        Node child;

        child.board = node.board;

        std::swap(child.board[blankRow][blankColumn],
            child.board[newRow][newCol]
        );

        child.path = node.path + move.direction;
        child.depth = node.depth + 1;
        child.previousMove = move.direction;

        children.push_back(child);
    }

    return children;
}

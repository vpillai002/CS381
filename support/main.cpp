#include <iostream>
#include <vector>
#include <fstream>
#include <cctype>
#include <stdexcept>

#include "puzzle.hpp"
#include "BFS.hpp"
#include "DLS.hpp"
#include "IDS.hpp"

void printResult(const SearchResult& result) {
    std::cout << std::endl;

    if (result.found) {
        
        std::cout << "Solution Found: " << "\n";

        std::cout << "Number of moves: ";
        std::cout << result.path.size();
        std::cout << "\n";

        std::cout << "Sequence of moves: ";
        std::cout << result.path;
        std::cout << "\n";

    } 
    else {
        
        std::cout << "Solution not found." << "\n";

        std::cout << "Number of moves: ";
        std::cout << 0;
        std::cout << "\n";

        std::cout << "Sequence of moves: "; 
        std::cout << "(none)";
        std::cout << "\n";
    }

    std::cout << "Number of states removed: ";
    std::cout << result.statesRemoved;
    std::cout << "\n";

    std::cout << "Maximum size of the queue (stack): ";
    std::cout << result.maxFrontierSize;
    std::cout << "\n";

    std::cout << "CPU Time: ";
    std::cout << result.cpuTime;
    std::cout << " seconds.";
    std::cout << "\n";
}

int main() {
    
    std::string startingInput;
    std::string goalInput;

    std::cout << "Enter start state: " << std::endl;
    std::getline(std::cin, startingInput);

    std::vector<std::vector<int>> _startState = parseBoard(startingInput);

    for (const auto& r : _startState)
    {
        for (int value : r) 
        {
            std::cout << value << ' ';
        }

        std::cout << std::endl;
    }

    std::cout << "Enter goal state: " << std::endl;
    std::getline(std::cin, goalInput);
    std::vector<std::vector<int>> _goalState = parseBoard(goalInput);

    for (const auto& s : _goalState)
    {
        for (int value : s) 
        {
            std::cout << value << ' ';
        }

        std::cout << std::endl;
    }

    std::cout << "Choose algorithm: " << std::endl;
    std::cout << "1. BFS" << std::endl;
    std::cout << "2. IDS" << std::endl;
    std::cout << "3. BFS & IDS" << std::endl;
    std::cout << "4. DLS" << std::endl;

    int choice = 0;
    std::cin >> choice;

    if (choice == 1) {
        SearchResult result = solveBFS(_startState, _goalState);

        std::cout << "\n";

        std::cout << "=== BFS ===" << "\n\n";

        printResult(result);
    }
    else if (choice == 2) {
        SearchResult result = solveIDS(_startState, _goalState);

        std::cout << "\n";

        std::cout << "=== IDS ===" << "\n\n";

        printResult(result);
    }
    else if (choice ==3) {
        SearchResult bfsResult = solveBFS(_startState, _goalState);

        std::cout << "\n";

        std::cout << "=== BFS ===" << "\n\n";

        printResult(bfsResult);

        SearchResult idsResult = solveIDS(_startState, _goalState, 30);

        std::cout << "\n";

        std::cout << "=== IDS ===" << "\n\n";

        printResult(idsResult);
    }
        else if (choice == 4) {
        int depthLimit;

        std::cout << "\n";

        std::cout << "Enter depth limit: ";

        std::cout << "\n";
        
        std::cin >> depthLimit;
        SearchResult result = solveDLS(_startState, _goalState, depthLimit);

        std::cout << "\n";

        std::cout << "=== DLS ===" << "\n\n";

        printResult(result);
    }
}


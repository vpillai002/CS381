#include "IDS.hpp"

SearchResult solveIDS(const Board& startState, const Board& goalState) {
    SearchResult result;
    
    if (startState == goalState) {
        result.found = true;
    }

    return result;
}
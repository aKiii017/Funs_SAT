#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    int old_score = score(idx);
    int score_limit = 10000;
    constexpr int score_increment = 1;
    int new_score = old_score + score_increment;

    if (new_score > score_limit) {
        rescale_variable_scores();
        old_score = (new_score - score_limit) * 0.75; // Decreases the score by 25%
        new_score = old_score + score_increment;
    }

    score(idx) = new_score;
}

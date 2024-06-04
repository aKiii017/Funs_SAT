#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    int old_score = score(idx);
    int score_inc = 1; // increment by 1 for each bump
    int new_score = old_score + score_inc;
    int score_limit = 10000; // limit for rescaling

    // check if limit has been hit
    if (new_score > score_limit) {
        // rescale scores
        rescale_variable_scores();
        // reset score
        new_score = score_limit;
    }

    // update score
    score(idx) = new_score;
}

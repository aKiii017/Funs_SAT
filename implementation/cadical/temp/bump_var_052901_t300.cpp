#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    double old_score = score(idx), new_score = old_score + score_inc;
    bool rescaled = false;

    // check if incrementation might require rescale, and perform it if necessary
    if (new_score < 0) {
        rescaled = true;
        rescale_variable_scores();
    }

    // re-calculate the new score if rescaling happened
    if (rescaled) {
        old_score = score(idx);
        new_score = old_score + score_inc;
    }

    // update the score
    score(idx) = new_score;
}

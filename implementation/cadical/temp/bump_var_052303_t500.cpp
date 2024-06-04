#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    int old_score = score(idx);
    int score_inc = 5; // the increment value
    int limit = 1000; // the limit score
    int new_score = old_score + score_inc;

    // Check if the increment would cause the score to exceed the limit
    if (new_score > limit) {
        // If so, rescale the scores
        rescale_variable_scores();
        old_score = score(idx);
    }

    // Recalculate the new score after rescaling if necessary
    new_score = old_score + score_inc;

    // Update the score
    score(idx) = new_score;
}

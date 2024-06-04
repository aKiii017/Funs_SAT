#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    double old_score = score(idx), new_score = old_score + score_inc;
    bool rescale_scores = evsids_limit_hit(new_score);

    if(rescale_scores) {
        rescale_variable_scores();
    } else {
        score(idx) = new_score;
    }
}

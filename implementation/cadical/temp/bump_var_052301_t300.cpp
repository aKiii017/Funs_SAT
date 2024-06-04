#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    bool rescale = evsids_limit_hit(score(idx) + score_inc);
    
    if (rescale) 
    {
        rescale_variable_scores();
        // Recalculate scores, as they may have changed during rescaling
        int new_score = score(idx) + score_inc;
        score(idx) = new_score;
    } 
    else 
    {
        score(idx) += score_inc;
    }
}

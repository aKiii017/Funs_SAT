#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
int idx = vidx(lit);
        double& var_score = score(idx);
        double old_score = var_score;
        double new_score = old_score + score_inc;
    
        if (evsids_limit_hit(new_score)) {
            rescale_variable_scores();
    
            var_score = score(idx);
            new_score = var_score + score_inc;
        }
    
        var_score = new_score;
    
        if (scores.contains(idx)) {
            scores.update(idx);
        }
}

#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    const int idx = vidx(lit);
    double& score = stab[idx];
    const double old_score = score;
    const double new_score = old_score + score_inc;

    if (new_score > 1e150) {
        // Rescale scores if necessary
        double max_val = 0.0;
        for (int i : vars) {
            if (stab[i] > max_val) {
                max_val = stab[i];
            }
        }
        if (max_val == 0.0 || new_score / max_val > 0.95) {
            double factor = 1.0 / max_val;
            while (new_score * factor > 1e150) {
                // Reduce the scaling factor if scores are still too large
                factor /= 2.0;
            }
            for (int i : vars) {
                stab[i] *= factor;
            }
            score_inc *= factor;
            score *= factor;
        }
    }
    else {
        score = new_score;
    }

    // Update the score in the priority queue
    if (scores.contains(idx)) {
        scores.update(idx);
    }

}

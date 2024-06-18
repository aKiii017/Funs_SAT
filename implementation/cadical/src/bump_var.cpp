#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    double old_score = stab[idx];
    double new_score = old_score + score_inc;

    // Check if rescaling is necessary
    if (new_score > 1e150) {
        double max_val = 0.0;

        // Find the maximum score
        for (auto i : vars) {
            double score = stab[i];
            if (score > max_val) {
                max_val = score;
            }
        }

        // Check if scores need to be rescaled
        if (max_val == 0.0 || new_score / max_val > 0.95) {
            double factor = 1.0 / max_val;

            // Rescale variable scores
            for (auto i : vars) {
                stab[i] *= factor;
                if (scores.contains(i)) {
                    scores.update(i);
                }
            }

            // Rescale score increment
            score_inc *= factor;
            old_score *= factor;
            new_score = old_score + score_inc;
        }

        // Incremental rescaling
        while (new_score > max_val * 0.95) {
            double factor = 0.5;

            // Rescale variable scores
            for (auto i : vars) {
                stab[i] *= factor;
                if (scores.contains(i)) {
                    scores.update(i);
                }
            }

            // Rescale score increment
            score_inc *= factor;
            old_score *= factor;
            new_score = old_score + score_inc;
        }
    }

    // Update variable score
    stab[idx] = new_score;

    if (scores.contains(idx)) {
        scores.update(idx);
    }
}

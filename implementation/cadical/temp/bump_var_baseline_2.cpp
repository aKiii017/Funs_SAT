#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
  int idx = vidx (lit);
  double old_score = score (idx);
  double new_score = old_score + score_inc;
  if (new_score > 1e150) {
    //Begining of rescaling
    double divider = score_inc;
    for (auto idx : vars) {
      const double tmp = stab[idx];
      if (tmp > divider)
        divider = tmp;
    }
    double factor = 1.0 / divider;
    for (auto idx : vars)
      stab[idx] *= factor;
    score_inc *= factor;
    //End of rescaling
    old_score = score (idx);
    new_score = old_score + score_inc;
  }
  score (idx) = new_score;
  if (scores.contains (idx))
    scores.update (idx);
}

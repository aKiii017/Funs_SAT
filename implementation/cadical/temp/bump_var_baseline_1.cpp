#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
  int idx = vidx (lit);
  double old_score = score (idx);
  double new_score = old_score + score_inc;
  if (new_score > 1e150) {
    rescale_variable_scores ();
    old_score = score (idx);
    new_score = old_score + score_inc;
  }
  score (idx) = new_score;
  if (scores.contains (idx))
    scores.update (idx);
}

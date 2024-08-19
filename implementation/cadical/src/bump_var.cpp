#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
  int idx = vidx (lit);
  double old_score = score (idx);
  double new_score = old_score + score_inc;
  if (evsids_limit_hit (new_score)) {
    rescale_variable_scores ();
    old_score = score (idx);
    new_score = old_score + score_inc;
  }
  score (idx) = new_score;
  if (scores.contains (idx))
    scores.update (idx);
}

#include "EasySAT.hpp"
#include <fstream>

void Solver::bump_var(int var, double coeff) {
const double eps = 1e-100;
    
        activity[var] += var_inc * coeff;
    
        // Check for overflow
        if (activity[var] >= eps) {
            activity[var] = eps;
        } else if (activity[var] <= -eps) {
            activity[var] = -eps;
        }
    
        if (vsids.inHeap(var)) {
            vsids.update(var);
        }
}

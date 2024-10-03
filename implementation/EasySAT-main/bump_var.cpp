#include "EasySAT.hpp"
#include <fstream>

void Solver::bump_var(int var, double coeff) {
double *activity = solver_activity; // activities of variables
        double var_inc = solver_var_inc; // global increment value
    
        activity[var] += var_inc * coeff;
    
        if (activity[var] > 1e100)
        {
            for (int i = 1; i < vars; i++)
            {
                activity[i] *= 1e-100;
            }
            var_inc *= 1e-100;
            activity[var] = 1e100;
        }
    
        if (is_in_heap(var, vsids))
        {
            update_heap(var, activity[var], vsids);
        }
}
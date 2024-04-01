#include "EasySAT.hpp"
#include <fstream>

void Solver::priority(int var, double coeff) {
    /*
    The function is used in SAT solvers to increase the activity of a variable.
    Args:
        var: The variable whose activity is to be changed. 
        coeff: To adjust the coefficient of variable activity. 
    */
    if ((activity[var] += var_inc * coeff) > 1e100) {           // Update score and prevent float overflow
        for (int i = 1; i <= vars; i++) activity[i] *= 1e-100;
        var_inc *= 1e-100;}
    if (vsids.inHeap(var)) vsids.update(var);                 // update heap
}

#include "EasySAT.hpp"
#include <fstream>

void Solver::bump_var(int var, double coeff) {
    if ((activity[var] += var_inc * coeff) > 1e100) {           // Update score and prevent float overflow
        for (int i = 1; i <= vars; i++) activity[i] *= 1e-100;
        var_inc *= 1e-100;}
    if (vsids.inHeap(var)) vsids.update(var);                 // update heap
}

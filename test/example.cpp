#include "EasySAT.hpp"
#include <fstream>
class Solver {};
void Solver::priority(int var, double coeff) {
/*
        The function is used in SAT solvers to increase the activity of a variable.
        Args:
            var: The variable whose activity is to be changed. 
            coeff: To adjust the coefficient of variable activity. 
        */
        if (activity[var] <= 0) {
            activity[var] = var_inc * coeff;
            if (vsids.inHeap(var)) vsids.update(var);                 // update heap
        }
        else {
            for (int i = 1; i <= vars; i++) {
                if (activity[i] > 0 && i != var) {
                    if (activity[i] * coeff < activity[var]){
                        activity[var] *= coeff;
                        if(vsids.inHeap(var)) vsids.update(var); 
                    }
                }
            }
        }
}


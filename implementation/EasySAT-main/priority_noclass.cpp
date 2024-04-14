#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    /*
    The function is used in SAT solvers to increase the activity of a variable.
    Args:
        activity: An array that represents the activity level of variables.
        var_inc: A base increment (default is 1) representing the basic amount by which a variable's activity is increased with each conflict.
        vars: An integer representing the total number of variables.
        vsids: A heap structure (usually a max heap) organized according to the activity levels of variables, used to quickly select the next variable for assignment.
            If the variable var is currently in the heap, then the heap needs to be updated to reflect the change in activity.  
        var: The variable number whose activity is to be increased. 
        coeff: A coefficient for adjusting the amount by which the activity is increased, typically set according to different contexts.
    */
    if ((activity[var] += var_inc * coeff) > 1e100) {           // Update score and prevent float overflow
        for (int i = 1; i <= vars; i++) activity[i] *= 1e-100;
        var_inc *= 1e-100;}
    if (vsids.inHeap(var)) vsids.update(var);                 // update heap
}

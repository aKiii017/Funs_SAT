#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    // Adjust the activity of the variable
    activity[var] *= coeff;
    activity[var] += var_inc;

    // Check if the activity has overflowed and fix the issue
    if (activity[var] > 1e100) {
        for (int i = 0; i < vars; i++) {
            activity[i] *= 1e-100;
        }
        var_inc *= 1e-100;
        coeff /= 1e10;
    }

    // Update the priority queue if the variable is in it
    if (vsids.inHeap(var)) {
        vsids.update(var);
    }

}

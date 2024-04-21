#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    activity[var] *= coeff;
    activity[var] += var_inc;

    if (activity[var] >= 1e100) {
        for (int i = 0; i < vars; i++) {
            activity[i] *= 1e-100;
        }
        var_inc *= 1e-100;
    }

    if (vsids.inHeap(var)) {
        vsids.update(var);
    }
}

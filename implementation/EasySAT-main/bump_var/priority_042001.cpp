#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    static const double MAX_ACTIVITY = 700.0, ACTIVITY_FACTOR = 0.9, DECAY_FACTOR = 0.95, DECAY_THRESHOLD = 0.001;
    double& var_activity = activity[var];

    // Increase the activity of the variable by the coeff
    var_activity += coeff * var_inc;

    // Increase the base increment var_inc if the variable's activity is at the maximum threshold
    if (var_activity >= MAX_ACTIVITY) 
    {
        var_activity = MAX_ACTIVITY;
        for (int i = 0; i < vars; ++i)
            activity[i] *= ACTIVITY_FACTOR;
        var_inc *= ACTIVITY_FACTOR;
    }
    // If the variable's activity is below the decay threshold, reset activity to 0
    else if (var_activity < DECAY_THRESHOLD) 
    {
        activity[var] = 0.0;
        var_inc *= DECAY_FACTOR;
        for (int i = 0; i < vars; ++i)
            activity[i] *= DECAY_FACTOR;
    }

    // Update the variable in the heap
    vsids.update(var);
}

#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    const double max_activity = 1e100, activity_factor = 1e-100, decay_factor = 0.9, decay_threshold = 1e-7;
    double& var_activity = activity[var];

    // Increase the activity of the variable by the coeff
    var_activity += coeff;

    // Increase the base increment var_inc 
    // if the variable's activity is at the maximum threshold
    if (var_activity >= max_activity)
    {
        var_activity = activity_factor * var_activity;
        for (int i = 0; i < vars; ++i)
        {
            activity[i] = activity_factor * activity[i];
        }
        var_inc = activity_factor * var_inc;
    }

    // Decay the activity of the variable and the base increment var_inc 
    // if the variable's activity is below the decay threshold
    if (activity[var] < decay_threshold)
    {
        activity[var] = 0.0;
        var_inc = decay_factor * var_inc;
        for(int i = 0; i < vars; ++i)
        {
            activity[i] = decay_factor * activity[i];
        }
    }

    // Update the variable in the heap
    vsids.update(var);
}

#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    double maxActivity = 700, decayFactor = 0.95, decayThreshold = 0.001, coefficientFactor = 2, activityFactor = 0.9, newActivity;
    double &var_activity = activity[var];

    // Increase the activity of the variable by the coeff and apply coefficient factor
    newActivity = var_activity + coeff * coefficientFactor;
    if(newActivity > maxActivity)
    {
        activity[var] = maxActivity;
        var_inc *= activityFactor;
        var_activity = maxActivity;
        // decay other variables' activity
        for(int i = 0; i < vars; ++i)
        {
            if(i != var)
            {
                activity[i] = max(activity[i] * decayFactor, 0.0);
            }
        }
    }
    else
    {
        activity[var] = newActivity;
        if(var_activity < decayThreshold)
        {
            var_activity = 0.0;
            var_inc *= decayFactor;
            // decay other variables' activity
            for(int i = 0; i < vars; ++i)
            {
                if(i != var)
                {
                    activity[i] = max(activity[i] * decayFactor, 0.0);
                }
            }
        }
    }

    // Update the variable in the heap
    vsids.update(var);
}

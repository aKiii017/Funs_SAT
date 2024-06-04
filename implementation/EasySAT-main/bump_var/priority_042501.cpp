#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    const double maxActivity = 700.0;
    const double decayRate = 0.95;
    const double decayThreshold = 0.001;
    const double activityFactor = 0.9;
    const double coefficientFactor = 2.0;

    double& var_activity = activity[var];
    double newActivity = var_activity + coeff * coefficientFactor;

    // Check if the new activity level exceeds the maximum allowed
    if(newActivity > maxActivity) 
    {
        var_activity = maxActivity;
        var_inc *= activityFactor;

        // Decay all other activity levels except the current one
        for(int i = 0; i < vars; ++i) 
        {
            if(i != var) 
            {
                activity[i] = std::max(activity[i] * decayRate, decayThreshold);
            }
        }
    } 
    else 
    {
        var_activity = newActivity;     // Update activity level

        // If the new activity level is below the decay threshold, decay other activity levels
        if(var_activity < decayThreshold) 
        {
            var_activity = 0.0;
            var_inc *= decayRate;

            for(int i = 0; i < vars; ++i) 
            {
                if(i != var) 
                {
                    activity[i] = std::max(activity[i] * decayRate, decayThreshold);
                }
            }
        }
    }

    // Update the variable in the VSIDS heap
    vsids.update(var);

}

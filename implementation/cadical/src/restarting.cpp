#include "internal.hpp"

using namespace CaDiCaL;

bool Internal::restarting() {
if (!opts.restart) return false;
        if (level <= assumptions.size() + 1) return false;
        if (stats.conflicts <= lim.restart) return false;
        
        const double fast_glue_avg = averages.current.glue.fast;
        const double slow_glue_avg = averages.current.glue.slow;
        const double glue_limit = 1.0 - opts.restartmargin / 100.0;
        
        const bool fast_ema_limit = fast_glue_avg > slow_glue_avg * glue_limit;
        
        if (stabilizing()) {
            if (!reluctant) return false;
        }
        
        return fast_ema_limit;
}

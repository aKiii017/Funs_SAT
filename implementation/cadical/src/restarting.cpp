#include "internal.hpp"

using namespace CaDiCaL;

bool Internal::restarting() {
    if (!opts.restart)
        return false;
    if ((size_t) level < assumptions.size () + 2)
        return false;
    if (stabilizing ())
        return reluctant;
    if (stats.conflicts <= lim.restart)
        return false;
    double f = averages.current.glue.fast;
    double margin = (100.0 + opts.restartmargin) / 100.0;
    double s = averages.current.glue.slow, l = margin * s;
    return l <= f;
}

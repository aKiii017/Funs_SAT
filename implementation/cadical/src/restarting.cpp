#include "internal.hpp"

using namespace CaDiCaL;

bool Internal::restarting() {
if (!opts.restart || stats.conflicts <= lim.restart || level < assumptions.size() + 2 || stabilizing()) {
        return reluctant;
      }
    
      const double fast_ema = averages.current.glue.fast;
      const double slow_ema = averages.current.glue.slow;
      const double slow_limit_margin = opts.restartmargin / 100.0;
    
      if (slow_limit_margin >= 0.5) {
        const double l = fast_ema * (1.0 + slow_limit_margin) / 2.0;
        return fast_ema >= l;
      }
    
      const double slow_limit = slow_ema * slow_limit_margin;
      const double slow_limit_diff = (fast_ema - slow_ema) * slow_limit_margin;
    
      if (slow_limit_diff < 0.0) {
        const double final_slow_limit = std::max(slow_ema + slow_limit_diff / 2.0, fast_ema);
        return fast_ema >= final_slow_limit / 2.0;
      }
    
      const double final_slow_limit = std::max(slow_ema + slow_limit_diff, fast_ema);
      return fast_ema >= final_slow_limit / 2.0;
}



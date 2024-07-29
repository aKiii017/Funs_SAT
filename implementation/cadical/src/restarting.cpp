#include "internal.hpp"

using namespace CaDiCaL;

bool Internal::restarting() {
if (!opts.restart || level < assumptions.size() + 2 || stats.conflicts <= lim.restart || stabilizing()) {
        return false;
      }
    
      double glue_slow_ema = averages.current.glue.slow;
      double glue_fast_ema = averages.current.glue.fast;
      double restart_margin = opts.restartmargin / 100.0;
      double slow_ema_limit = glue_slow_ema * restart_margin;
      double max_ema_limit = glue_slow_ema - slow_ema_limit;
      double final_slow_ema_limit = glue_fast_ema + (glue_slow_ema - glue_fast_ema) * restart_margin;
    
      if (glue_fast_ema >= final_slow_ema_limit) {
        return true;
      }
    
      double slow_ema_diff = glue_slow_ema - glue_fast_ema;
      double ratio = slow_ema_limit / slow_ema_diff;
      double max_ema_limit_ratio = max_ema_limit / slow_ema_diff;
    
      if (glue_fast_ema < slow_ema_limit 
          || max_ema_limit < 0 
          || max_ema_limit_ratio <= ratio 
          || max_ema_limit_ratio * 2 >= ratio 
          || max_ema_limit >= glue_fast_ema * ratio) {
        return true;
      }
    
      return false;
}

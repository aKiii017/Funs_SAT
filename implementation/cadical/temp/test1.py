import re
from typing import Tuple

def _extract_function_names(spec: str) -> Tuple[str, str]:
    # 使用正则表达式匹配函数定义，包括前缀 "Internal::"
    function_pattern = r'\b(Internal::\w+)\s*\('
    
    # 查找所有匹配的函数名称
    matches = re.findall(function_pattern, spec)
    
    # 假设 spec 中只有一个要提取的函数名称
    if matches:
        function_to_evolve = matches[0]
        function_to_run = matches[0]
        return function_to_evolve, function_to_run
    
    # 如果没有找到匹配的函数名称，则返回默认值或处理错误
    return '', ''

# 示例调用
specifications = [r'''
#include "internal.hpp"

using namespace CaDiCaL;

bool Internal::restarting() {
  if (!opts.restart) {
    return false;
  }

  if (stats.conflicts <= lim.restart) {
    return false;
  }

  if (level < assumptions.size() + 2 || stabilizing()) {
    return reluctant;
  }

  const double fast_ema = averages.current.glue.fast;
  const double slow_ema = averages.current.glue.slow;

  double slow_ema_limit = slow_ema * (opts.restartmargin / 100.0);
  double slow_ema_limit_diff = (fast_ema - slow_ema) * (opts.restartmargin / 100.0);

  if (slow_ema_limit_diff < 0.0) {
    slow_ema_limit_diff /= 2.0;
  }

  double final_slow_ema_limit = std::max(slow_ema + slow_ema_limit_diff, fast_ema);
  
  return fast_ema >= final_slow_ema_limit / 2.0;
}


''',
r'''
#include "internal.hpp"

using namespace CaDiCaL;

void Internal::bump_variable_score(int lit) {
    int idx = vidx(lit);
    double old_score = stab[idx];
    double new_score = old_score + score_inc;

    // Check if rescaling is necessary
    if (new_score > 1e150) {
        double max_val = 0.0;

        // Find the maximum score
        for (auto i : vars) {
            double score = stab[i];
            if (score > max_val) {
                max_val = score;
            }
        }

        // Check if scores need to be rescaled
        if (max_val == 0.0 || new_score / max_val > 0.95) {
            double factor = 1.0 / max_val;

            // Rescale variable scores
            for (auto i : vars) {
                stab[i] *= factor;
                if (scores.contains(i)) {
                    scores.update(i);
                }
            }

            // Rescale score increment
            score_inc *= factor;
            old_score *= factor;
            new_score = old_score + score_inc;
        }

        // Incremental rescaling
        while (new_score > max_val * 0.95) {
            double factor = 0.5;

            // Rescale variable scores
            for (auto i : vars) {
                stab[i] *= factor;
                if (scores.contains(i)) {
                    scores.update(i);
                }
            }

            // Rescale score increment
            score_inc *= factor;
            old_score *= factor;
            new_score = old_score + score_inc;
        }
    }

    // Update variable score
    stab[idx] = new_score;

    if (scores.contains(idx)) {
        scores.update(idx);
    }
}
''']

function_to_evolve, function_to_run = _extract_function_names(specifications[1])
print(f'function_to_evolve: {function_to_evolve}, function_to_run: {function_to_run}')

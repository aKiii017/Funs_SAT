# FunSearch Implementation

## 环境

```shell
conda env create -f funsat.yml
```

## 数据集
- SAT competition2024
  https://benchmark-database.de/?track=main_2024
- SAT competition2023
  https://satcompetition.github.io/2023/downloads.html
  
放在`~/Fun_SAT/dataset/`下
## 配置文件

`config.yaml` 

- data_set: 训练集全集
- data_set_eval: 验证集，可以与训练集相同，用size区分
- dataset_size: 训练集size
- eval_dataset_size: 验证集size
- timeout_value: 超时时限
- case_num: 实验编号
- parallel_size: 同时运行的实例数，根据空闲核数确定
- log_name: log的储存地址
- time_list: 不同时限内完成的数目，目前没有实际用途，仅输出用作参考
- script_path: 运行试验sat求解器的脚本地址
```yaml
  # kissat
  '~/Fun_SAT/implementation/kissat/temp/kissat.sh'

  # cadical
  # '~/Fun_SAT/implementation/cadical/temp/cadical.sh'

  # SBVA
  # '~/Fun_SAT/implementation/SBVA/temp/sbva.sh'

  # z3
  # '~/Fun_SAT/implementation/z3/temp/z3.sh'
```
- pattern_starts: 函数起点的pattern
```yaml
  # kissat
  # bump
  - 'void kissat_bump_score_increment\(.*?\)\s*{' 
  # restart
  # - 'bool kissat_restarting\(.*?\)\s*{' 

  # cadical
  # bump
  # - 'void Internal::bump_variable_score\(.*?\)\s*{' 
  # restart
  # - 'bool Internal::restarting\(.*?\)\s*{' 

  # SBVA
  # - 'int Formula::tiebreaking_heuristic\(.*?\)\s*{'

  # z3
  # - 'void solver::inc_activity\(.*?\)\s*{'
```
- file_paths: 要修改的函数地址
```yaml
  # kissat
  # bump
  - '/home/ubuntu/Fun_SAT/implementation/kissat/src/kissat_bump_score_increment.c'  
  # restart
  # - '/home/ubuntu/Fun_SAT/implementation/kissat/src/kissat_restarting.c' 

  # cadical
  # bump
  # - '/home/ubuntu/Fun_SAT/implementation/cadical/src/bump_var.cpp'  
  # restart
  # - '/home/ubuntu/Fun_SAT/implementation/cadical/src/restarting.cpp' 

  # SBVA
  # - '/home/ubuntu/Fun_SAT/implementation/SBVA/tiebreaking_heuristic.cpp'
  
  # z3
  # - '/home/ubuntu/z3/src/sat/inc_activity.cpp'
```
- patterns: 修改函数时识别的pattern
```yaml
  # kissat
  # bump
  - '(void kissat_bump_score_increment\(.*?\)\s*{)([\s\S]*?)(^\})'  
  # restart
  # - '(bool kissat_restarting\(.*?\)\s*{)([\s\S]*?)(^\})' 

  # cadical
  # bump
  # - '(void Internal::bump_variable_score\(.*?\)\s*{)([\s\S]*?)(^\})'  
  # restart
  # - '(bool Internal::restarting\(.*?\)\s*{)([\s\S]*?)(^\})'

  # SBVA
  # - '(int Formula::tiebreaking_heuristic\(.*?\)\s*{)([\s\S]*?)(^\})'

  # z3
  # - '(void solver::inc_activity\(.*?\)\s*{)([\s\S]*?)(^\})'
```
- language: 求解器的实现语言，'c' 或者 'cpp'
- function_pattern: 为获取函数名的pattern
```yaml
  # kissat
  # bump
  - '\bvoid\s+(\w+)\s*\(' 
  # restart
  # - '\bbool\s+(\w+)\s*\(' 

  # cadical
  # - '\b(Internal::\w+)\s*\('  

  # SBVA
  # - '\b(Formula::\w+)\s*\('

  # z3
  # - '\b(solver::\w+)\s*\('
```
- includes: 函数的preface，有这部分才能成功进行语法分析
```yaml
  # 需要一个列表，除了这一项以外都只需要列表中的一项
  # kissat
  # bump
  - "#include \"bump.h\""
  - "#include \"internal.h\""
  # restart
  # - "#include <stdbool.h>"
  # - "#include \"internal.h\""
  # - "#include \"restart.h\""
  
  # cadical
  # - "using namespace CaDiCaL;"
  # - "#include \"internal.hpp\""

  # SBVA
  # - "using namespace std;"
  # - "#include \"sbva.hpp\""

  # z3
  # - "using namespace sat;"
  # - "#include \"sat/sat_solver.h\""
```
- include_paths: 也是有这部分才能成功进行语法分析
```yaml
  # kissat
  - "/home/ubuntu/Fun_SAT/implementation/kissat/src" 

  # cadical
  # - "/home/ubuntu/Fun_SAT/implementation/cadical/src"  

  # SBVA
  # - "/home/ubuntu/Fun_SAT/implementation/SBVA"

  # z3
  # - "/home/ubuntu/Fun_SAT/implementation/z3/src"
```
- additional_prompt: 给llm的prompt，函数的简单介绍，根据实验情况有时需要添加一些限制
```yaml
- |
  In the context of SAT solvers that use the VSIDS heuristic, 
  ...
```
- specifications: 初始函数
```yaml
- |
  #include "internal.hpp"

  using namespace CaDiCaL;
  
  void Internal::bump_variable_score(int lit) {
    int idx = vidx (lit);
    double old_score = score (idx);
    double new_score = old_score + score_inc;
    if (evsids_limit_hit (new_score)) {
      rescale_variable_scores ();
      old_score = score (idx);
      new_score = old_score + score_inc;
    }
    score (idx) = new_score;
    if (scores.contains (idx))
      scores.update (idx);
  }
```



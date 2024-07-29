# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""A single-threaded implementation of the FunSearch pipeline."""
from __future__ import annotations

# from collections.abc import Sequence

# RZ: there are multiple errors in the original code
# we should use typing.xxx rather than collections.abc.xxx
from typing import Any, Tuple, Sequence

from implementation import code_manipulation
from implementation import config as config_lib
from implementation import evaluator
from implementation import programs_database
from implementation import sampler
from implementation import profile
        
# def _extract_function_names(specification: str) -> Tuple[str, str]:
#     """Returns the name of the function to evolve and of the function to run.

#     RZ: The so-called specification refers to the boilerplate code template for a task.
#     The template MUST have two important functions decorated with '@funsearch.run', '@funsearch.evolve' respectively.
#     The function labeled with '@funsearch.run' is going to evaluate the generated code (like fitness evaluation).
#     The function labeled with '@funsearch.evolve' is the function to be searched (like 'greedy' in cap-set).
#     This function (_extract_function_names) makes sure that these decorators appears in the specification.
#     """
#     run_functions = ['Internal::restarting'] #code_manipulation.yield_decorated(specification, '@funsearch.run')
#     if len(run_functions) != 1:
#         raise ValueError('Expected 1 function decorated with `@funsearch.run`.')
#     evolve_functions = ['Internal::restarting'] #code_manipulation.yield_decorated(specification, '@funsearch.evolve')
#     if len(evolve_functions) != 1:
#         raise ValueError('Expected 1 function decorated with `@funsearch.evolve`.')
#     return evolve_functions[0], run_functions[0]

def _extract_function_names(spec: str) -> Tuple[str, str]:
    import re

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


def main(
        # specification: str,
        specifications: list,
        inputs: Sequence[Any],
        config: config_lib.Config,
        max_sample_nums: int | None,
        class_config: config_lib.ClassConfig,
        **kwargs
):
    """Launches a FunSearch experiment.
    RZ:
    Args:
        specification: the boilerplate code for the problem.
        inputs       : the data instances for the problem (see 'bin_packing_utils.py').
        config       : config file.
        max_sample_nums: the maximum samples nums from LLM. 'None' refers to no stop.
    """
    # include_paths = ["/home/ubuntu/Fun_SAT/implementation/EasySAT-main"]

    # get log_dir and create profiler
    log_dir = kwargs.get('log_dir', None)
    if log_dir is None:
        profiler = None
    else:
        profiler = profile.Profiler(log_dir)

    # -------changed to multifunc-------
    # function_to_evolve, function_to_run = _extract_function_names(specification)
    # template = code_manipulation.text_to_program(specification)
    # database = programs_database.ProgramsDatabase(config.programs_database, template, function_to_evolve)
    # evaluators = []
    # for _ in range(config.num_evaluators):
    #     evaluators.append(evaluator.Evaluator(
    #         database,
    #         template,
    #         function_to_evolve,
    #         function_to_run,
    #         inputs,
    #         sandbox_class=class_config.sandbox_class
    #     ))

    function_to_evolve_list = []
    function_to_run_list = []
    templates = []
    databases = []
    evaluators_list = []
    current_index=0
    score_list = evaluator.ScoreList()
    for spec in specifications:
        function_to_evolve, function_to_run = _extract_function_names(spec)
        template = code_manipulation.text_to_program(spec)
        function_to_evolve_list.append(function_to_evolve)
        function_to_run_list.append(function_to_run)
        templates.append(template)
        
        database = programs_database.ProgramsDatabase(config.programs_database, template, function_to_evolve)
        databases.append(database)

        evaluators = []
        for _ in range(config.num_evaluators):
            evaluators.append(evaluator.Evaluator(
                database,
                template,
                function_to_evolve,
                function_to_run,
                inputs,
                sandbox_class=class_config.sandbox_class
            ))
        evaluators_list.append(evaluators)
        
    # We send the initial implementation to be analysed by one of the evaluators.
    # initial = template.get_function(function_to_evolve).body
    # score_list=evaluator.ScoreList()
    # count_list=evaluators[0].analyse(initial, island_id=None, version_generated=None, profiler=profiler,score_list_score=score_list.all_score,exec_size=score_list.dataset_size,score_list=score_list,init=True)
    # 对每一个 template 进行一次 analyse
        initial = template.get_function(function_to_evolve).body
        count_list = evaluators[0].analyse(
            initial, 
            island_id=None, 
            version_generated=None, 
            profiler=profiler,
            score_list_score=score_list.all_score,
            exec_size=score_list.dataset_size,
            score_list=score_list, 
            init=True,
            current_index=current_index
        )
        current_index+=1

    # Set global max sample nums.
    # samplers = [sampler.Sampler(database, evaluators, config.samples_per_prompt, max_sample_nums=max_sample_nums, llm_class=class_config.llm_class)
    #             for _ in range(config.num_samplers)]
    # Initialize samplers using the entire databases and evaluators_list
    samplers = [sampler.Sampler(
        databases, 
        evaluators_list, 
        config.samples_per_prompt, 
        max_sample_nums=max_sample_nums, 
        llm_class=class_config.llm_class,
        functions_num=len(specifications)
    ) for _ in range(config.num_samplers)]
    
    # -------changed to multifunc-------




    # This loop can be executed in parallel on remote sampler machines. As each
    # sampler enters an infinite loop, without parallelization only the first
    # sampler will do any work.
    for s in samplers:
        s.sample(count_list, profiler=profiler,score_list=score_list)

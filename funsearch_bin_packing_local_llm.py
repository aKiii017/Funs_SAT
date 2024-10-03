import json
import multiprocessing
from typing import Collection, Any

import requests
from implementation import funsearch
from implementation import config
from implementation import sampler
from implementation import evaluator_accelerate
from implementation import evaluator
from implementation import code_manipulation
import bin_packing_utils

import os

data_set='2024random_25_1'
data_set_eval='2024random_25_1'
dataset_size='25'
timeout_value='100'
case_num='100101'
parallel_size='25'
case_code=data_set+'_'+timeout_value+'_'+case_num
log_name='logs_z3'
time_list=[100,300,500,700,1000]
        

class LocalLLM(sampler.LLM):
    """Language model that predicts continuation of provided source code.
    """

    def __init__(self, samples_per_prompt: int, batch_inference: bool = True) -> None:
        """
        Args:
            batch_inference: Use batch inference when sample functions. The batch size equals to the samples_per_prompt.
        """
        super().__init__(samples_per_prompt)
        # url = 'http://0.0.0.0:8000/v1/completions'
        url = 'http://0.0.0.0:8000/v1/chat/completions'
        additional_prompt = [
            # (
            #  'In the context of SAT solvers that use the VSIDS heuristic. '
            #  'Given the existing restarting_v0 function, please generate an optimized version named restarting_v*. '
            #  'This new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
            #  'The function evaluates several conditions related to the solver\'s state, conflict count, and metrics of clause quality to decide whether a restart should occur. '
            #  'This helps the solver to avoid getting stuck in difficult regions of the search space and potentially improve its efficiency.'
            #  'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
            #  'Ensure the function is significantly different and more advanced than the prior versions. '
            #  'Only the C++ code for the function is required, without any additional descriptions or annotations.'
            #  'Existing restarting_v0 function for reference:'
            #  'If the option to restart (\'opts.restart\') is not enabled, the function immediately returns \'false\', indicating that no restart should occur.'
            #  'This condition checks if the current decision level (\'level\') is less than the number of assumptions plus two. If it is, the function returns \'false\', meaning the solver is too early in its decision process to consider a restart.'
            #  'If the \'stabilizing()\' function returns \'true\', the function returns the value of \'reluctant\', which indicates whether a reluctant restart should be considered based on the solver\'s stabilization state.'
            #  'If the current number of conflicts (\'stats.conflicts\') is less than or equal to the restart limit (\'lim.restart\'), the function returns \'false\', meaning there haven\'t been enough conflicts to warrant a restart.'
            #  'The function calculates the fast and slow exponential moving averages (EMAs) of the glue (a measure of clause quality). '
            #  'It computes the restart margin based on \'opts.restartmargin\' and multiplies the slow EMA by this margin to get the limit (\'l\'). '
            #  'The function returns \'true\' if the fast EMA (\'f\') is greater than or equal to the computed limit (\'l\'), indicating that the conditions for a restart have been met. Otherwise, it returns \'false\'.'
            #   'Your task is to create the optimized restarting_v* function based on the guidelines above. Remember, only the C++ function code is needed.'
            # ),

            # (
            #  'In the context of SAT solvers that use the VSIDS heuristic. '# the activity of a variable represents how often the variable has been involved in conflicts.'
            #  'Given the existing bump_variable_score_v0 function, please generate an optimized version named bump_variable_score_v*. '
            #  'ensure that no new member variables or functions are introduced beyond those already mentioned, and avoid any syntax errors or undefined behaviors.'
            #  'This function is part of a SAT solver\'s implementation designed to dynamically adjust the heuristic scores of variables '
            #  'based on their involvement in conflict resolution or other heuristic decisions. '
            #  'The new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
            #  'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
            #  'Ensure the function is significantly different and more advanced than the prior versions. '
            #  'Only the C++ code for the function is required, without any additional descriptions or annotations.'
            #  'Existing bump_variable_score_v0 function for reference:'
            #  'Args:'
            #      'lit: An integer representing the literal whose variable\'s score needs to be bumped.'
            #  'The function increments the score of the variable associated with lit by score_inc, a predefined increment value, enhancing the variable\'s priority for future decision-making.'
            #  'If updating the score results in exceeding a predefined limit (evsids_limit_hit), a rescaling function (rescale_variable_scores) is triggered to prevent numerical overflow:'
            #  'Scores are recalibrated, and then the score increment is reapplied to ensure the updated value is within the acceptable range.'
            #  'The function updates the score of the variable at index idx to new_score.'
            #  'It checks if the variable\'s index is currently in the scores data structure. '
            #  'If it is, its position in the structure is updated to reflect its new score. '
            #  'This data structure is crucial for efficiently selecting the next variable for decision-making based on their activity scores.'
            #  'Your task is to create the optimized bump_variable_score_v* function based on the guidelines above.'
            #  'Remember, only the C++ function code is needed, and it should adhere strictly to C++11 standards without referencing undefined functions, variables, or external libraries.'
            #  'Additionally, ensure that no new member variables or functions are introduced beyond those already mentioned.'
            # ),


            # (
            # 'The tiebreaking_heuristic function is designed to compare two literals, lit1 and lit2, in solving SAT problems. '
            # 'It calculates a heuristic value to help break ties between these literals based on their relationships with each other.'
            # 'The function first checks if there is a cached heuristic value for lit2. '
            # 'This is done using tmp_heuristic_cache_full, a cache that stores precomputed heuristic values. '
            # 'The function uses the index of lit2 (retrieved by sparsevec_lit_idx(lit2)) to look it up.'
            # 'If a cached value is found, it is returned immediately, which helps avoid redundant calculations.'
            # 'If the value is not cached, the function proceeds to update the adjacency matrix with lit1 and lit2 by calling update_adjacency_matrix for each literal.' 
            # 'The adjacency matrix represents relationships between literals.'
            # 'The function then retrieves sparse vectors vec1 and vec2 from the adjacency matrix.' 
            # 'These vectors correspond to the literals abs1 and abs2, where abs1 and abs2 are the absolute values of lit1 and lit2, respectively.'
            # 'It initializes a variable total_count to accumulate the heuristic value.'
            # 'The function iterates over the non-zero elements of vec2. For each non-zero element, it updates the adjacency matrix for a variable var and retrieves its sparse vector vec3.'
            # 'It then computes the dot product between vec1 and vec3, multiplied by the coefficient of vec2 at var, and adds this to total_count.'
            # 'The computed total_count is then stored in the cache (tmp_heuristic_cache_full) with the index of lit2 as the key for future use.'
            # 'Finally, the function returns the total_count, which is the heuristic value used to break ties between lit1 and lit2.'
            # 'Your task is to create the optimized tiebreaking_heuristic_v* function based on the guidelines above. Remember, only the C++ function code is needed.'
            # ),
            # (
            # 'The tiebreaking_heuristic function is designed to compare two literals, lit1 and lit2, in solving SAT problems. '
            # 'It calculates a heuristic value to help break ties between these literals based on their relationships with each other.'
            # 'The function first calculates the index idx2 for lit2, then searches for this index in the tmp_heuristic_cache_full hash table.'
            # 'If found, it directly returns the cached value to avoid redundant computations. '
            # 'The function updates the adjacency matrices for both literals lit1 and lit2 '
            # 'and retrieves the corresponding sparse vectors vec1 and vec2 from the updated adjacency matrices.'
            # 'The function then uses OpenMP to parallelize the computation of the heuristic value.' 
            # 'It iterates over all elements in vec2, and for each non-zero element, calculates the dot product with vec1, '
            # 'then multiplies the dot product by the coefficient in vec2 and adds it to total_count.' 
            # 'After the computation, the result is stored in the cache and returned.'
            # 'Your task is to create the optimized tiebreaking_heuristic_v* function based on the guidelines above. Remember, only the C++ function code is needed.'
            # ),
            # (
            #  'In the context of SAT solvers that use the VSIDS heuristic. '
            #  'Given the existing bump_var_v0 function, please generate an optimized version named bump_var_v*. '
            #  'This new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
            #  'The function is part of a SAT solver\'s implementation, which is designed to dynamically adjust the heuristic scores of variables '
            #  'based on their involvement in conflict resolution or other heuristic decisions. '
            #  'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
            #  'Ensure the function is significantly different and more advanced than the prior versions. '
            #  'Only the C++ code for the function is required, without any additional descriptions or annotations.'
            #  'Existing bump_var_v0 function for reference:'
            #  'Args:'
            #      'var: An integer representing the index of a variable.'
            #      'coeff: A double value used as a coefficient to scale the increment of the variable\'s activity score.'
            #  'This function increments the activity score of the variable var by var_inc (a base increment value) scaled by coeff. '
            #  'This is done to increase the priority of the variable for future decision-making.'
            #  'If this updated score exceeds 1e100, it triggers a normalization step to prevent floating-point overflow:'
            #  'All variable scores are scaled down by multiplying with 1e-100.'
            #  'The base increment value var_inc is also scaled down by the same factor to maintain consistent scaling.'
            #  'The function checks if the variable is currently in the VSIDS heap. If it is, its position in the heap is updated to reflect its new activity score. '
            #  'This heap is crucial for efficiently selecting the next variable for decision-making based on their activity scores.'
            #   'Your task is to create the optimized restarting_v* function based on the guidelines above. Remember, only the C++ function code is needed.'
            # ),
            # ('''
            #  In the context of SAT solvers that use the VSIDS heuristic, 
            #  you are tasked with developing an optimized version of the bump_variable_score function, 
            #  named bump_variable_score_v*. This function is integral to a SAT solver's implementation, 
            #  designed to dynamically adjust the heuristic scores of variables based on their involvement in conflict resolution or other heuristic decisions. 
            #  The new version should be more efficient and capable of helping the SAT solver escape from local optima.
            #  Requirements:
            #     Function Name: bump_variable_score_v*
            #     Language: C++11
            #     Dependencies: Avoid using undefined functions, variables, or external libraries.
            #     Member Variables and Functions: Use only those that have been explicitly mentioned or are evident from the provided context.
            #     Complexity: Incorporate multiple conditional logics and loops as necessary to enhance efficiency and decision-making capability.
            #     Behavioral Guarantees: Ensure no syntax errors or undefined behaviors are introduced. The function should significantly differ from and advance beyond the prior versions.
            #  Existing Function for Reference:
            #     Function: bump_variable_score_v0
            #     Arguments:
            #         lit: An integer representing the literal whose variable's score needs to be bumped.
            #     Behavior:
            #         Increments the score of the variable associated with lit by a predefined increment value (score_inc), enhancing the variable's priority.
            #         If updating the score results in exceeding a predefined limit (evsids_limit_hit), a rescaling function (rescale_variable_scores) is triggered to prevent numerical overflow:
            #             Scores are recalibrated, and the score increment is reapplied to ensure the updated value is within the acceptable range.
            #         Updates the score of the variable at index idx to new_score.
            #         Checks if the variable's index is currently in the scores data structure. If it is, its position in the structure is updated to reflect its new score. 
            #         This data structure is crucial for efficiently selecting the next variable for decision-making based on their activity scores.
            #  Task:
            #     Create the optimized bump_variable_score_v* function based on the guidelines above. 
            #     Ensure that no new member variables or functions are introduced beyond those already mentioned. 
            #     The code should adhere strictly to C++11 standards without referencing undefined functions, variables, or external libraries.
            #  Functions and Variables Available:
            #     vidx(int lit)
            #         Purpose: Converts a literal to its corresponding variable index.
            #         Parameter: lit - Literal whose index needs to be retrieved.
            #         Return Type: int - Index of the variable corresponding to the given literal.
            #     score(int idx)
            #         Purpose: Accesses or modifies the score of a variable located at the given index via reference.
            #         Parameter: idx - Index of the variable.
            #         Return Type: double& - A reference to the score of the variable, allowing both to retrieve and modify the value.
            #     score_inc
            #         Type: double
            #         Purpose: Defines the increment value by which the variable's score is increased during each call to bump_variable_score.
            #     evsids_limit_hit(double new_score)
            #         Purpose: Checks whether the new score hits or exceeds a predefined limit, which might necessitate score rescaling to prevent overflow.
            #         Parameter: new_score - The score to be checked against the limit.
            #         Return Type: bool - Returns true if the limit is hit or exceeded; otherwise, false.
            #     rescale_variable_scores()
            #         Purpose: Rescales all variable scores in the system to prevent numerical overflow and maintain granularity in score differences.
            #     scores.contains(int idx)
            #         Purpose: Checks if the index (variable) is currently tracked in the relevant data structure (like a priority queue or a heap).
            #         Parameter: idx - Index of the variable.
            #         Return Type: bool - Returns true if the index is present; otherwise, false.
            #     scores.update(int idx)
            #         Purpose: Updates the position of the variable in the data structure to reflect changes in its score.
            #         Parameter: idx - Index of the variable whose position needs updating.
            #     Aside from the functions and variables mentioned above, do not assume the existence of any other functions or variables.
            #  '''
            #  ),
            # ('''
            #  In the context of SAT solvers that use the VSIDS heuristic, 
            #  you are tasked with developing an optimized version of the kissat_bump_score_increment function, 
            #  named kissat_bump_score_increment_v*. This function is integral to a SAT solver's implementation, 
            #  designed to dynamically adjusts the rate at which variable scores increase within the solver, 
            #  ensuring that the scoring mechanism adapts to the solver's needs and maintains numerical stability.
            #  The new version should be more efficient and capable of helping the SAT solver escape from local optima.
            #  Requirements:
            #     Function Name: kissat_bump_score_increment_v*
            #     Language: C
            #     Dependencies: Avoid using undefined functions, variables, or external libraries.
            #     Member Variables and Functions: Use only those that have been explicitly mentioned or are evident from the provided context.
            #     Complexity: Incorporate multiple conditional logics and loops as necessary to enhance efficiency and decision-making capability.
            #     Behavioral Guarantees: Ensure no syntax errors or undefined behaviors are introduced. The function should significantly differ from and advance beyond the prior versions.
            #  Existing Function for Reference:
            #     Function: kissat_bump_score_increment
            #     Arguments:
            #         solver: A pointer to a kissat structure representing the SAT solver instance.
            #     Behavior:
            #         The function begins by accessing the decay configuration of the solver through the GET_OPTION(decay) macro, 
            #         which extracts the decay value from the solver's options structure, casting it to an integer.
            #         This decay value is then scaled down by multiplying with 1e-3 to compute the dec_factor. 
            #         This factor is crucial as it determines the rate of growth of the score increment, 
            #         allowing the function to adjust dynamically based on solver performance and configuration settings.
            #         The function calculates an adjustment factor using the formula 1.0 / (1.0 - dec_factor). 
            #         This computation is designed to inversely adjust the scoring increment, 
            #         ensuring it gradually increases to counteract the effects of decay, 
            #         fostering the solver's adaptability over its operational span.
            #         Using this adjustment, the function updates the current score increment (solver->scinc) by multiplying it with the decay adjustment to derive a new score increment (new_scinc). 
            #         It also ensures that if the current scinc is less than 1.0, it is set to 1.0 to maintain a minimum effective increment level.
            #         The newly calculated score increment (new_scinc) is then checked against a maximum allowable score (MAX_SCORE). 
            #         If new_scinc exceeds this threshold, the function sets the solver->scinc to MAX_SCORE / scinc before setting new_scinc to MAX_SCORE. 
            #         This step is critical to prevent the score from escalating beyond what the system can handle efficiently.
            #         Subsequently, the function invokes kissat_rescale_scores(solver) if the new score limit is exceeded. 
            #         This rescaling adjusts all variable scores within the solver to prevent numerical overflow and ensure that all scores, 
            #         including the score increment, remain within practical operational limits.
            #         Through these mechanisms, the function not only manages the dynamic increase of score increments to enhance variable selection priority but also ensures numerical stability and effective performance management of the solver. 
            #         By carefully controlling and adjusting the score increment and implementing conditional rescaling, the function maintains the solver's operational integrity and efficiency.             
            #  Task:
            #     Create the optimized kissat_bump_score_increment_v* function based on the guidelines above. 
            #     Ensure that no new member variables or functions are introduced beyond those already mentioned. 
            #     The code should adhere strictly to C standards without referencing undefined functions, variables, or external libraries.
            #  '''
            #  ),
            # ('''
            #  In the context of SAT solvers that use the VSIDS heuristic, 
            #  you are tasked with developing an optimized version of the kissat_restarting function, 
            #  named kissat_restarting_v*. This function is integral to a SAT solver's implementation, 
            #  designed to determine whether a restart of the SAT solver is necessary based on dynamic conditions and performance metrics.
            #  The new version should be more efficient and capable of helping the SAT solver escape from local optima.
            #  Requirements:
            #     Function Name: kissat_restarting_v*
            #     Language: C
            #     Dependencies: Avoid using undefined functions, variables, or external libraries.
            #     Member Variables and Functions: Use only those that have been explicitly mentioned or are evident from the provided context.
            #     Complexity: Incorporate multiple conditional logics and loops as necessary to enhance efficiency and decision-making capability.
            #     Behavioral Guarantees: Ensure no syntax errors or undefined behaviors are introduced. The function should significantly differ from and advance beyond the prior versions.
            #  Existing Function for Reference:
            #     Function: kissat_restarting
            #     Arguments:
            #         solver: A pointer to a kissat structure representing the SAT solver instance.
            #     Behavior:
            #         The function begins by checking if the restart option is disabled (!GET_OPTION(restart)), if the decision level is zero (!solver->level), or if the number of conflicts is less than a predetermined restart conflict limit (CONFLICTS < solver->limits.restart.conflicts). 
            #         If any of these conditions are true, it returns false, indicating no need for a restart.
            #         It then checks if the solver is in a stable phase (solver->stable). If true, the function determines whether to trigger a restart based on a reluctant trigger mechanism by calling kissat_reluctant_triggered(&solver->reluctant).
            #         For unstable modes, the function computes the average "fast" and "slow" glue values, which are measures of clause quality. Based on these values and a user-defined margin (restartmargin), it calculates a limit (limit) that helps in deciding whether to restart.
            #         If the "fast" glue value is not exceeding the "slow" glue value (fast <= slow), it continues without restarting. Otherwise, it calculates a displacement limit for variables based on the "fast" glue value and the margin.
            #         The function then examines the solver\'s trail from the most recent decision to the earliest. During this examination, it counts the number of displaced variables and the maximum decision level observed.
            #         The restart conditions are checked against:
            #             Exceeding the threshold of displaced variables.
            #             A significant portion of decisions being on the current maximum level (max_level_count > 0.5 * seen_lits).
            #             The computed limit being less than or equal to the "fast" glue value (limit <= fast).
            #         If any of the above conditions are met, the function returns true, indicating a restart should occur. Otherwise, if none of the criteria are satisfied, it concludes with false.             
            #  Task:
            #     Create the optimized kissat_restarting_v* function based on the guidelines above. 
            #     Ensure that no new member variables or functions are introduced beyond those already mentioned. 
            #     The code should adhere strictly to C standards without referencing undefined functions, variables, or external libraries.
            #  '''
            #  ),
            # ('''
            #  In the context of SAT solvers that use the VSIDS heuristic, 
            #  you are tasked with developing an optimized version of the bump_var function, 
            #  named bump_var_v*. This function is integral to a SAT solver's implementation, 
            #  designed to determine whether a restart of the SAT solver is necessary based on dynamic conditions and performance metrics.
            #  The new version should be more efficient and capable of helping the SAT solver escape from local optima.
            #  Requirements:
            #     Function Name: bump_var_v*
            #     Language: C++
            #     Dependencies: Avoid using undefined functions, variables, or external libraries.
            #     Member Variables and Functions: Use only those that have been explicitly mentioned or are evident from the provided context.
            #     Complexity: Incorporate multiple conditional logics and loops as necessary to enhance efficiency and decision-making capability.
            #     Behavioral Guarantees: Ensure no syntax errors or undefined behaviors are introduced. The function should significantly differ from and advance beyond the prior versions.
            #  Existing Function for Reference:
            #     Function: bump_var
            #     Arguments:
            #         var: An integer that specifies the variable index within the SAT solver.
            #         coeff: A double representing the coefficient used to update the variable's activity based on its involvement in recent conflicts or heuristics.
            #     Behavior:
            #         The function begins by adjusting the activity of the specified variable (var) by adding the product of a global increment value (var_inc) and the passed coefficient (coeff). This is done to dynamically reflect the variable's importance based on recent solver activities.
            #         It checks if the updated activity value exceeds a threshold of 1e100 to prevent floating-point overflow. If this threshold is crossed:
            #             The function iterates over all variables (from 1 to vars), scaling down their activity values by multiplying with 1e-100. This scaling down helps in maintaining numerical stability within the system.
            #             Similarly, it scales down the var_inc value by 1e-100, ensuring the increment remains proportional and prevents excessive growth in future updates.
            #         Following the activity update, the function verifies if var is currently managed within a heap structure (vsids), used for maintaining variable priorities based on activities.
            #             If the variable is in the heap, it updates its position to reflect its new activity, thereby ensuring that the heap properties (such as order and integrity) are maintained correctly.
            #         This approach enables the SAT solver to dynamically prioritize variables with higher relevance to recent conflicts or conditions, improving the efficiency of the solving process.
            #         By carefully managing the activity scaling and heap updates, the function prevents numerical instability and maintains the efficiency and effectiveness of the solver's operations.             
            #  Task:
            #     Create the optimized bump_var_v* function based on the guidelines above. 
            #     Ensure that no new member variables or functions are introduced beyond those already mentioned. 
            #     The code should adhere strictly to C standards without referencing undefined functions, variables, or external libraries.
            #  '''
            #  ),
            ('''
             In the context of SAT solvers that use the VSIDS heuristic, 
             you are tasked with developing an optimized version of the inc_activity function, 
             named inc_activity_v*. This function is integral to a SAT solver's implementation, 
             designed to determine whether a restart of the SAT solver is necessary based on dynamic conditions and performance metrics.
             The new version should be more efficient and capable of helping the SAT solver escape from local optima.
             Requirements:
                Function Name: inc_activity_v*
                Language: C++
                Dependencies: Avoid using undefined functions, variables, or external libraries.
                Member Variables and Functions: Use only those that have been explicitly mentioned or are evident from the provided context.
                Complexity: Incorporate multiple conditional logics and loops as necessary to enhance efficiency and decision-making capability.
                Behavioral Guarantees: Ensure no syntax errors or undefined behaviors are introduced. The function should significantly differ from and advance beyond the prior versions.
             Existing Function for Reference:
                Function: inc_activity
                Arguments:
                    v: A type bool_var that specifies the variable index within the SAT solver.
                Behavior:
                    The function begins by increasing the activity of the specified variable (v) by adding a fixed increment (m_activity_inc). This increment reflects the variable's significance based on recent solver activities.
                    It checks if the updated activity value exceeds a preset threshold (1 << 24) to prevent integer overflow. If this threshold is exceeded:
                        The function executes rescale_activity(), which iterates through all variables, scaling down their activity values to ensure numerical stability within the system. This activity scaling is crucial in maintaining proper operational balance and preventing runaway growth in activity values.
                        This rescaling makes certain that the increment value (m_activity_inc) remains proportionate, thereby curbing excessive accumulation in future updates.
                    After updating the activity, the function checks if the variable v is currently managed within a priority queue (m_case_split_queue), which is utilized for maintaining variable priorities based on activities.
                        If the variable is in the queue, it triggers an event handler (activity_increased_eh) to update its position, ensuring that the queue properties (such as order and integrity) are properly maintained.
                    The function's approach permits the SAT solver to dynamically prioritize variables that are increasingly relevant to recent conflicts or conditions, thereby improving the efficiency of the solving process.
                    By attentively managing the activity increments and queue updates, the function averts numerical instabilities and sustains both the efficiency and effectiveness of the solver's operations.             Task:
                Create the optimized inc_activity_v* function based on the guidelines above. 
                Ensure that no new member variables or functions are introduced beyond those already mentioned. 
                The code should adhere strictly to C standards without referencing undefined functions, variables, or external libraries.
             '''
             ),

            ]
        extra_info = r'''

                        '''
        self._batch_inference = batch_inference
        self._url = url
        self._additional_prompt = additional_prompt
        self._trim = True

    def draw_samples(self, prompt: str,count_list,current_index) -> Collection[str]:
        """Returns multiple predicted continuations of `prompt`."""
        all_samples = []
        if self._batch_inference:
            response = self._do_request(prompt,count_list,current_index)
            for res in response:
                all_samples.append(res)
        else:
            for _ in range(self._samples_per_prompt):
                response = self._do_request(prompt,count_list,current_index)
                all_samples.append(response)
        # print(all_samples)
        return all_samples

    def _do_request(self, content: str,count_list,current_index) -> str:
        import re
        # import pdb;pdb.set_trace()
        content = '\n'.join([self._additional_prompt[current_index],content])
        # content = '\n'.join([content, 'Your task is to create the optimized restarting_v* function based on the guidelines above. Remember, only the C++ function code is needed.'])
        content = '\n'.join([content, 'Do not include exceptional interruptions.'])
        content = '\n'.join([content, 'Please give the optimized code at the begining of your respond with no specification ahead.'])
        # content = '\n'.join([content, 'Score stands for the amount of instences that are successfully solved within '+timeout_value+'s, you need to try to maximum this value.'])
        # content = '\n'.join([content, 'This Dict is provided for reference: '+str(count_list)])
        # content = '\n'.join([content, 'In this Dict, the key represents time in seconds, and the value represents the number of instances successfully executed in the corresponding time.'])
        
        JSONfile='JSONfile/'+case_code+'.json'
        if not os.path.exists(JSONfile):
            with open(JSONfile, 'w') as outfile:
                data = []
        else:
            with open(JSONfile, 'r') as infile:
                try:
                # 尝试加载JSON数据
                    data = json.load(infile)
                except json.JSONDecodeError:
            # 如果文件为空或不是有效的JSON格式，初始化为空数组
                    data = []    # 文件存在，打开文件        
 
        new_record = {'id': len(data) + 1, 'prompt': content, 'response': None}


        # 随机生成session_id
        session_id = case_num+str(len(data) + 1)
        
        while True:
            try:
                # response = requests.post(self._url, data=json.dumps(data), headers=headers)
                
                # --------------api implement------------------------
                # from openai import OpenAI
                # openai_api_key = "EMPTY"
                # openai_api_base = "http://172.23.148.56:8000/v1"
                # client = OpenAI(
                #     api_key=openai_api_key,
                #     base_url=openai_api_base,
                # )
                
                # completion = client.completions.create(model="model",
                #                                     prompt=content,
                #                                     temperature=0.8,
                #                                         max_tokens=2048,)
                
                # print("Completion result:", json.loads(completion.json())['choices'][0]['text'])
                # response = json.loads(completion.json())['choices'][0]['text'] #给model发送prompt
                # --------------api implement------------------------

                # --------------api implement azure------------------------
                # from openai import OpenAI
                # from openai import AzureOpenAI
                

                # openai_api_key = "f825f61246354ec090c5703ca4f76418"
                # openai_api_base = "https://midivi-main-scu1.openai.azure.com/"
                # client = AzureOpenAI(
                #   api_key = openai_api_key,  
                #   api_version = "2024-02-01",
                #   azure_endpoint = openai_api_base
                # )
                # # 初始化对话历史
                # messages = [
                #     {"role": "system", "content": "You are a helpful assistant."},
                #     # {"role": "user", "content": "How do I use session management in APIs?"}
                # ]

                # def ask_question(question, messages):
                #     messages.append({"role": "user", "content": question})
                #     response = client.chat.completions.create(
                #         model="gpt-35-turbo",  # 使用适当的模型
                #         messages=messages
                #     )
                #     answer = response.choices[0].message.content
                #     messages.append({"role": "assistant", "content": answer})
                #     return answer

                # response=ask_question(content, messages)
                # print("Assistant:", response)

                # --------------api implement azure------------------------

                # --------------api implement openai------------------------
                from openai import OpenAI
                client = OpenAI(
                    # This is the default and can be omitted
                    base_url="https://api.f2gpt.com/v1",
                    api_key="sk-f27nghhUpWfx5ULqL5MNmPmZhZxkRGkkoPbHLis30bCJ0U4z",
                )
                completion = client.chat.completions.create(
                  model="gpt-4o",
                  messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": content}
                  ]
                )
                
                print("Completion result:", completion.choices[0].message.content)
                response = completion.choices[0].message.content #给model发送prompt
                # --------------api implement openai------------------------


                new_record['response'] = response

                data.append(new_record)

                with open(JSONfile, 'w') as outfile:
                    json.dump(data, outfile, indent=4)



                # import pdb;pdb.set_trace()
                print('------------old------------')
                print(content)#print(response.json()['choices'][0]['message']['content'])
                # import pdb;pdb.set_trace()
                print('------------new------------')
                print(response)
                # import pdb;pdb.set_trace()
                
                # response = response.json()['choices'][0]['text']
                # response = response.json()['choices'][0]['message']['content']
                # response = json.loads(response.json())['choices'][0]['message']['content']
                # response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                return response
                
            except Exception as e:
                continue


class Sandbox(evaluator.Sandbox):
    """Sandbox for executing generated code. Implemented by RZ.

    RZ: Sandbox returns the 'score' of the program and:
    1) avoids the generated code to be harmful (accessing the internet, take up too much RAM).
    2) stops the execution of the code in time (avoid endless loop).
    """

    def __init__(self, verbose=False, numba_accelerate=True):
        """
        Args:
            verbose         : Print evaluate information.
            numba_accelerate: Use numba to accelerate the evaluation. It should be noted that not all numpy functions
                              support numba acceleration, such as np.piecewise().
        """
        self._verbose = verbose
        self._numba_accelerate = numba_accelerate
    def _compile_and_run_function(self, program, function_to_run, function_to_evolve, numba_accelerate,score_list_score,exec_size,score_list:evaluator.ScoreList,init=False):
        try:
            
            import json
            import os
            
            import subprocess
            # conda_env = 'sf'
            # script_path = os.path.expanduser("~/funsearch_vm_schecduling/implementation/vm/VMAgent_plus/vmagent/test_baselines.py")
            # script_path = os.path.expanduser("~/Fun_SAT/implementation/cadical/temp/cadical.sh")
            # script_path = os.path.expanduser("~/Fun_SAT/implementation/SBVA/temp/sbva.sh")
            # script_path = os.path.expanduser("~/Fun_SAT/implementation/EasySAT-main/EasySAT.sh")
            # script_path = os.path.expanduser("~/Fun_SAT/implementation/kissat/temp/kissat.sh")
            script_path = os.path.expanduser("/home/ubuntu/z3/temp/z3.sh")
            data_path = os.path.expanduser("~/Fun_SAT/implementation/EasySAT-main/dataset/"+data_set)
            data_path_eval = os.path.expanduser("~/Fun_SAT/implementation/EasySAT-main/dataset/"+data_set_eval)

            command_run = []
            if(init):  
                command_run = [
                script_path,
                data_path_eval,
                timeout_value, 
                parallel_size,
                exec_size  
            ]
            else:
                command_run = [
                script_path,
                data_path,
                timeout_value, 
                parallel_size,
                exec_size  
            ]
            # # 构造命令
            # command_run = []
            # if init:  
            #     command_run = [
            #         f"conda activate base && {script_path} {data_path_eval} {timeout_value} {parallel_size} {exec_size}"
            #     ]
            # else:
            #     command_run = [
            #         f"conda activate base && {script_path} {data_path} {timeout_value} {parallel_size} {exec_size}"
            #     ]
            

            import re
            # 运行命令
            # subprocess.run(command_make, capture_output=True, text=True, check=True)
            out = subprocess.run(command_run, capture_output=True, text=True, check=True)
            flag = out.returncode
            # result = float(result.stdout)
            par2 = re.search(r"AVGtime: (-\d+(\.+\d+)?)", out.stdout)
            par2 = float(par2.group(1))
            print("par2:",par2)

            successcnt = re.search(r"SUCCESScount: (\d+(\.+\d+)?)", out.stdout)
            successcnt = int(successcnt.group(1))
            print("successcnt:",successcnt)

            count_list={}
            for i in time_list:#,400,500,700,1000]:
                value = re.search(str(i)+r"Scount: (\d+(\.+\d+)?)", out.stdout)
                value = int(value.group(1))
                count_list[i] = value

            print(count_list)

            # 前缀字符串
            prefix1 = '/home/ubuntu/Fun_SAT/implementation/EasySAT-main/dataset/'+data_set+'/'
            prefix2 = '/home/ubuntu/Fun_SAT/implementation/EasySAT-main/dataset/'+data_set_eval+'/'

            # 正则表达式模式，用于匹配 TASK、其后到 RUNtime 之前的内容和 RESULT
            pattern = r'\[TASK(\d+)\](.*?)\[RUNtime\].*?\[RESULT\](SATISFIABLE|UNSATISFIABLE|UNKNOWN)'

            # 查找所有匹配的内容
            matches = re.findall(pattern, out.stdout, re.DOTALL)
            score_list_score={}
            # 将匹配结果存储到字典中
            for match in matches:
                task_number = f'TASK{match[0]}'
                task_content = match[1].strip()
                task_result = 0 if match[2]=='UNKNOWN' else 1
                # 去掉前缀字符串
                if task_content.startswith(prefix1):
                    task_content = task_content[len(prefix1):]
                elif task_content.startswith(prefix2):
                    task_content = task_content[len(prefix2):]

                score_list_score[task_content] = task_result

            # 打印结果字典
            print('score_list_score: ')
            for scorel in score_list_score.items():
                print(scorel)

            # 初次运行更新分数list和successcnt
            if(init):    
                score_list.update_all_score(score_list_score)
                score_list.update_successcnt(successcnt)
            
            # 计算当前得分是否更高
            cal=score_list.cal_cur_score(score_list_score)
            print('cal: ',cal)
            if cal:
                # 是则运行整个set比较successcnt
                command_run_eval = [
                script_path,
                data_path_eval,
                timeout_value, 
                parallel_size,
                dataset_size
                ]
                import re
                out_eval = subprocess.run(command_run_eval, capture_output=True, text=True, check=True)
                successcnt_eval = re.search(r"SUCCESScount: (\d+(\.+\d+)?)", out_eval.stdout)
                successcnt_eval = int(successcnt_eval.group(1))
                print("successcnt_eval:",successcnt_eval)
                if successcnt_eval>score_list.successcnt:
                    matches_eval = re.findall(pattern, out_eval.stdout, re.DOTALL)
                    # 结果更好则更新列表和分数
                    score_list_score_eval={}
                    # 将匹配结果存储到字典中
                    for match in matches_eval:
                        task_number = f'TASK{match[0]}'
                        task_content = match[1].strip()
                        task_result = 0 if match[2]=='UNKNOWN' else 1
                        # 去掉前缀字符串
                        if task_content.startswith(prefix1):
                            task_content = task_content[len(prefix1):]
                        elif task_content.startswith(prefix2):
                            task_content = task_content[len(prefix2):]

                        score_list_score_eval[task_content] = task_result
                    
                    # 打印结果字典
                    print('score_list_score: ')
                    for scorel in score_list_score_eval.items():
                        print(scorel)

                    score_list.update_cur_score(score_list_score_eval)

            # 给出最后的分数        
            result=score_list.successcnt
            print('result: ',result)

            # result=successcnt


            if flag == 0:
                # 确保结果被正确解析并放入队列
                # result_queue.put((result, True))
                return result,True, count_list
            else:
                # result_queue.put((None, False))
                return None, False, count_list
        except Exception as e:
            # 如果出现异常，我们认为执行失败
            # result_queue.put((None, False))
            return None, False, {}
    def run(
            self,
            program: str,
            function_to_run: str,  # RZ: refers to the name of the function to run (e.g., 'evaluate')
            function_to_evolve: str,  # RZ: accelerate the code by decorating @numba.jit() on function_to_evolve.
            inputs: Any,  # refers to the dataset
            test_input: str,  # refers to the current instance
            timeout_seconds: int,
            score_list_score: dict,
            exec_size:int,
            score_list:evaluator.ScoreList,
            init=False,
            **kwargs  # RZ: add this
    ) -> tuple[Any, bool]:
        """Returns `function_to_run(test_input)` and whether execution succeeded.

        RZ: If the generated code (generated by LLM) is executed successfully,
        the output of this function is the score of a given program.
        RZ: PLEASE NOTE THAT this SandBox is only designed for bin-packing problem.
        """
        # dataset = inputs[test_input]
        # result_queue = multiprocessing.Queue()
        # process = multiprocessing.Process(
        #     target=self._compile_and_run_function,
        #     args=(program, function_to_run, function_to_evolve, dataset, self._numba_accelerate, result_queue)
        # )
        # process.start()
        # process.join(timeout=timeout_seconds)
        # if process.is_alive():
        #     # if the process is not finished in time, we consider the program illegal
        #     process.terminate()
        #     process.join()
        #     results = None, False
        # else:
        #     if not result_queue.empty():
        #         results = result_queue.get_nowait()
        #     else:
        #         results = None, False
        # result_queue = multiprocessing.Queue()

        # 这里我们假设`_compile_and_run_function`将负责使用`subprocess`来执行程序
        # 注意：由于我们不再直接使用multiprocessing.Process，下面的调用方式需要调整
        count_list={}
        isok, result, count_list = self._compile_and_run_function(program, function_to_run, function_to_evolve, self._numba_accelerate,score_list_score,exec_size,score_list,init)
        

        # 获取结果，这部分可能需要根据你的实际情况进行调整
        #TODO:1.需要处理不运行or效果不如最佳的结果（也可以不做统计，仅保留最后最优的结果？）2.修改evulate的process为5个(done) 3.需要对启发式的bin packing code重构以兼容双NUMA的request(done)
         
        results = isok,result, count_list
        
        if self._verbose:
            print(f'================= Evaluated Program =================')
            program_: code_manipulation.Program = code_manipulation.text_to_program(text=program)
            func_to_evolve_: str = kwargs.get('func_to_evolve', 'Internal::restarting')
            function_: code_manipulation.Function = program_.get_function(func_to_evolve_)
            function_: str = str(function_).strip('\n')
            print(f'{function_}')
            print(f'-----------------------------------------------------')
            print(f'Score: {str(results)}')
            print(f'=====================================================')
            print(f'\n\n')

        return results

    # def _compile_and_run_function(self, program, function_to_run, function_to_evolve, dataset, numba_accelerate,
    #                               result_queue):
    #     try:
    #         # optimize the code (decorate function_to_run with @numba.jit())
    #         if numba_accelerate:
    #             program = evaluator_accelerate.add_numba_decorator(
    #                 program=program,
    #                 function_to_evolve=function_to_evolve
    #             )
    #         # compile the program, and maps the global func/var/class name to its address
    #         all_globals_namespace = {}
    #         # execute the program, map func/var/class to global namespace
    #         exec(program, all_globals_namespace)
    #         # get the pointer of 'function_to_run'
    #         function_to_run = all_globals_namespace[function_to_run]
    #         # return the execution results
    #         results = function_to_run(dataset)
    #         # the results must be int or float
    #         if not isinstance(results, (int, float)):
    #             result_queue.put((None, False))
    #             return
    #         result_queue.put((results, True))
    #     except:
    #         # if raise any exception, we assume the execution failed
    #         result_queue.put((None, False))

    

specifications = [
# r'''
# #include "internal.hpp"

# using namespace CaDiCaL;

# bool Internal::restarting() {
#     if (!opts.restart || level <= assumptions.size() + 1 || (stats.conflicts <= lim.restart)) return false;

#     double limit = (1.0 + opts.restartmargin / 100.0) * averages.current.glue.slow;
#     bool fast_ema_limit = averages.current.glue.fast >= limit;

#     if (stabilizing()) return fast_ema_limit && reluctant;
#     else return fast_ema_limit;
# }
# ''',
# r'''
# #include "internal.hpp"

# using namespace CaDiCaL;

# void Internal::bump_variable_score(int lit) {
#   int idx = vidx (lit);
#   double old_score = score (idx);
#   double new_score = old_score + score_inc;
#   if (evsids_limit_hit (new_score)) {
#     rescale_variable_scores ();
#     old_score = score (idx);
#     new_score = old_score + score_inc;
#   }
#   score (idx) = new_score;
#   if (scores.contains (idx))
#     scores.update (idx);
# }
# ''',
# r'''
# #include "sbva.hpp"
# using namespace std;

# int Formula::tiebreaking_heuristic(int lit1, int lit2) {
#   // Check cached value for lit2
#   const int idx2 = sparsevec_lit_idx(lit2);
#   const auto it = tmp_heuristic_cache_full.find(idx2);
#   if (it != tmp_heuristic_cache_full.end()) {
#     return it->second;
#   }

#   // Update adjacency matrix for both literals and get corresponding sparse vectors
#   update_adjacency_matrix(lit1);
#   update_adjacency_matrix(lit2);
#   const Eigen::SparseVector<int> vec1 = adjacency_matrix[sparsevec_lit_idx(abs(lit1))];
#   const Eigen::SparseVector<int> vec2 = adjacency_matrix[idx2];

#   // Compute heuristic value
#   int total_count = 0;
#   #pragma omp parallel for reduction(+:total_count)
#   for (int j = 0; j < vec2.outerSize(); ++j) {
#     // Retrieve variable and coefficient for vec2
#     const int var = sparcevec_lit_for_idx(j);
#     const int coeff = vec2.coeff(j);

#     // Avoid unnecessary computations
#     if (var == abs(lit1) || coeff == 0) {
#       continue;
#     }

#     // Retrieve and compute dot product for vec3
#     const Eigen::SparseVector<int> vec3 = adjacency_matrix[j];
#     const int dot_prod = vec3.dot(vec1);

#     // Update total count
#     total_count += coeff * dot_prod;
#   }

#   // Cache the heuristic value for future use
#   tmp_heuristic_cache_full[idx2] = total_count;

#   return total_count;
# }
# ''',
# r'''
# #include "EasySAT.hpp"
# #include <fstream>

# void Solver::bump_var(int var, double coeff) {
#     if ((activity[var] += var_inc * coeff) > 1e100) {           // Update score and prevent float overflow
#         for (int i = 1; i <= vars; i++) activity[i] *= 1e-100;
#         var_inc *= 1e-100;}
#     if (vsids.inHeap(var)) vsids.update(var);                 // update heap
# }''',
# r'''
# #include "bump.h"
# #include "internal.h"

# void kissat_bump_score_increment(kissat *solver) {
#   const double old_scinc = solver->scinc;
#   const double decay = GET_OPTION (decay) * 1e-3;
#   const double factor = 1.0 / (1.0 - decay);
#   const double new_scinc = old_scinc * factor;
#   solver->scinc = new_scinc;
#   if (new_scinc > MAX_SCORE)
#     kissat_rescale_scores (solver);
# }

# ''',
# r'''
# #include "bump.h"
# #include "internal.h"

# void kissat_bump_score_increment(kissat *solver) {
#     const double dec_factor = GET_OPTION(decay) * 1e-3;
#     double scinc = solver->scinc;

#     if (scinc < 1.0)
#         scinc = 1.0;

#     const double decay_adjustment = 1.0 / (1.0 - dec_factor);
#     double new_scinc = scinc * decay_adjustment;

#     if (new_scinc > MAX_SCORE) {
#         solver->scinc = MAX_SCORE / scinc;
#         new_scinc = MAX_SCORE;
#         kissat_rescale_scores(solver);
#     } else {
#         solver->scinc = new_scinc;
#     }
# }
# ''',
# r'''
# #include <stdbool.h>
# #include "internal.h"
# #include "restart.h"

# bool kissat_restarting(kissat *solver) {
#     if (!GET_OPTION (restart) || !solver->level || CONFLICTS < solver->limits.restart.conflicts)
#         return false;

#     if (solver->stable)
#         return kissat_reluctant_triggered (&solver->reluctant);

#     const double fast = AVERAGE (fast_glue);
#     const double slow = AVERAGE (slow_glue);
#     const double margin = (100.0 + GET_OPTION (restartmargin)) / 100.0;
#     const double limit = margin * slow;

#     if (fast <= slow)
#         return false;

#     const int limit_displaced = fast * (GET_OPTION (restartmargin) / 100.0);
#     const int trail_size = SIZE_STACK (solver->trail);
#     const value * values = solver->values;
#     const int *trail = BEGIN_STACK (solver->trail);

#     int max_level = 0;
#     int max_level_count = 0;
#     int seen_lits = 0;
#     int displaced_variables = 0;

#     for (int i = trail_size - 1; i >= 0; i--)
#     {
#         const int lit = trail[i];
#         const int idx = IDX (lit);
#         const int level = LEVEL (idx);

#         if (level <= 0 || displaced_variables > limit_displaced)
#             break;

#         seen_lits += !values[idx];

#         if (level > max_level)
#         {
#             max_level = level;
#             max_level_count = 1;
#         }
#         else if (level == max_level)
#         {
#             max_level_count++;
#         }

#         if (!values[idx] && level == solver->level)
#         {
#             displaced_variables++;
#         }

#         if (displaced_variables > limit_displaced)
#         {
#             break;
#         }
#         else if (max_level_count > (0.5 * seen_lits))
#         {
#             return true;
#         }
#         else if (limit <= fast)
#         {
#             return true;
#         }
#     }

#     return false;
# }

# ''',
r'''
#include "sat/sat_solver.h"
using namespace sat;

void solver::inc_activity(bool_var v) {
    unsigned &act = m_activity[v];
    act += m_activity_inc;
    m_case_split_queue.activity_increased_eh(v);
    if (act > (1 << 24))
        rescale_activity();
}
''',


]

# It should be noted that the if __name__ == '__main__' is required.
# Because the inner code uses multiprocess evaluation.

if __name__ == '__main__':
    class_config = config.ClassConfig(llm_class=LocalLLM, sandbox_class=Sandbox)
    config = config.Config(samples_per_prompt=4)

    bin_packing_or3 = {'OR3': bin_packing_utils.datasets['OR3']}
    global_max_sample_num = 400  # if it is set to None, funsearch will execute an endless loop
    funsearch.main(
        specifications=specifications,
        inputs=bin_packing_or3,
        config=config,
        max_sample_nums=global_max_sample_num,
        class_config=class_config,
        log_dir= log_name+'/funsearch_local_llm_'+case_code,
    )

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

data_set='2023random_240_1'
data_set_eval='2023random_240_1'
dataset_size='240'
timeout_value='100'
case_num='081801'
parallel_size='25'
case_code=data_set+'_'+timeout_value+'_'+case_num
log_name='logs_sbva'
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
            (
             'In the context of SAT solvers that use the VSIDS heuristic. '
             'Given the existing restarting_v0 function, please generate an optimized version named restarting_v*. '
             'This new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
             'The function evaluates several conditions related to the solver\'s state, conflict count, and metrics of clause quality to decide whether a restart should occur. '
             'This helps the solver to avoid getting stuck in difficult regions of the search space and potentially improve its efficiency.'
             'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
             'Ensure the function is significantly different and more advanced than the prior versions. '
             'Only the C++ code for the function is required, without any additional descriptions or annotations.'
             'Existing restarting_v0 function for reference:'
             'This function returns a boolean indicating whether a restart is needed. The initial if statement checks several conditions to decide if a restart should not be performed:'
             'opts.restart: This is likely a boolean option that enables or disables restarting. If it\'s false, restarting is disabled.'
             'level <= assumptions.size() + 1: This checks if the current decision level is too close to the number of assumptions. '
             'Assumptions are literals assumed to be true to restrict the search space temporarily. '
             'If the solver is still exploring close to these assumptions, it might not restart.'
             'stats.conflicts <= lim.restart: This checks if the number of conflicts encountered so far is less than a restart limit. '
             'If not enough conflicts have occurred, the solver might benefit from continuing the current search path rather than restarting.'
             'The function then calculates a dynamic limit based on the average "glue" level of learned clauses. '
             'The "glue" level typically measures how many different decision levels are involved in a clause, with lower glue indicating a more useful clause. '
             'The opts.restartmargin is used to adjust this threshold dynamically, allowing some flexibility in when restarts are triggered.'
             'This checks if the fast EMA of the glue level is above the calculated limit. '
             'EMAs are used to smooth out fluctuations and focus on recent trends. '
             'A fast EMA reacting to the limit suggests that recent clauses are less useful, possibly indicating that a restart could be beneficial.'
             'This part of the function makes the final decision on whether to restart:'
             'stabilizing(): This likely checks if the solver is in a stabilizing state, where it might be focusing on consolidating its findings rather than exploring aggressively.'
             'reluctant: This variable, used only in the stabilizing state, might indicate additional conditions or thresholds that affect restarting during stabilization.'
             'If the solver is stabilizing, both fast_ema_limit and reluctant must be true to trigger a restart. Otherwise, only fast_ema_limit needs to be true.'
              'Your task is to create the optimized restarting_v* function based on the guidelines above. Remember, only the C++ function code is needed.'
            ),

            # (
            #  'In the context of SAT solvers that use the VSIDS heuristic. '# the activity of a variable represents how often the variable has been involved in conflicts.'
            #  'Given the existing bump_variable_score_v0 function, please generate an optimized version named bump_variable_score_v*. '
            #  'The primary purpose of this function is to increase the specified variable\'s score and rescale the scores if necessary to ensure numerical stability in the scoring system. '
            #  'This new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
            #  'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
            #  'Ensure the function is significantly different and more advanced than the prior versions. '
            #  'Only the C++ code for the function is required, without any additional descriptions or annotations.'
            #  'Existing bump_variable_score_v0 function for reference:'
            #  'Args:'
            #      'lit: The index of a literal, which is a Boolean variable or its negation.'
            #  'The \'vidx\' function is used to convert the literal to its corresponding variable index \'idx\'. This index is used to access and update the variable\'s score.'
            #  'The \'score\' function is called to retrieve the current score of the variable \'old_score\'. Scores are typically used in heuristic decision-making to determine which variables should be prioritized for assignment.'
            #  'The current score \'old_score\' is increased by an increment value \'score_inc\', resulting in a new score \'new_score\'. This increment is a predefined constant used to gradually increase the variable\'s score.'
            #  'If the new score exceeds a predefined limit, all variable scores will be rescaled. Typically, this means reducing all scores proportionally to avoid overflow or excessively large values.'
            #  'To accomplish this, first goal here is to find an appropriate \'divider\' to proportionally scale all variable scores. It starts with \'score_inc\' as the initial value and then iterates through all the variable scores \'stab[idx]\'. '
            #  'If any score is greater than the current \'divider\', it updates the \'divider\' to that score. Ultimately, the \'divider\' becomes the maximum value between \'score_inc\' and all variable scores.'
            #  'Then the scaling factor \'factor\' is calculated, which is \'1.0\' divided by \'divider\'.'
            #  'Variable\'s scores is then rescaled by iterates through all variables, multiplying each variable\'s score \'stab[idx]\' by the scaling factor \'factor\'. It also scales \'score_inc\' by the same factor.'
            #  'By now the rescaling is accomplished.'
            #  'Then the old score is retrieved again, and the new score is recalculated. '
            #  'The new score is then assigned to the variable idx.'
            #  'If the variable idx is already in the priority queue scores, its score is updated. This ensures that the scores in the priority queue are always up to date.'                             
            #  'Your task is to create the optimized bump_variable_score_v* function based on the guidelines above. Remember, only the C++ function code is needed.'
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

                # --------------api implement gpt------------------------
                from openai import OpenAI
                from openai import AzureOpenAI
                openai_api_key = "f825f61246354ec090c5703ca4f76418"
                openai_api_base = "https://midivi-main-scu1.openai.azure.com/"
                client = AzureOpenAI(
                  api_key = openai_api_key,  
                  api_version = "2024-02-01",
                  azure_endpoint = openai_api_base
                )
                response = client.chat.completions.create(
                    model="gpt-35-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": content},
                    ],
                    stream=False
                )
                print("Completion result:",response.choices[0].message.content)
                response = response.choices[0].message.content
                # --------------api implement gpt------------------------

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
            script_path = os.path.expanduser("~/Fun_SAT/implementation/SBVA/temp/sbva.sh")
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
r'''
#include "internal.hpp"

using namespace CaDiCaL;

bool Internal::restarting() {
    if (!opts.restart || level <= assumptions.size() + 1 || (stats.conflicts <= lim.restart)) return false;

    double limit = (1.0 + opts.restartmargin / 100.0) * averages.current.glue.slow;
    bool fast_ema_limit = averages.current.glue.fast >= limit;

    if (stabilizing()) return fast_ema_limit && reluctant;
    else return fast_ema_limit;
}
''',
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

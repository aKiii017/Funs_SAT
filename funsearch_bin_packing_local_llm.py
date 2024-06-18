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

data_set='test'
dataset_size='150'
timeout_value='700'
case_num='061602'
parallel_size='25'
case_code=data_set+'_'+timeout_value+'_'+case_num
log_name='logs_cadical'
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
        additional_prompt = (
                            'In the context of SAT solvers that use the VSIDS heuristic. '
                            'Given the existing restarting_v0 function, please generate an optimized version named restarting_v*. '
                            'This new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
                            'The function evaluates several conditions related to the solver\'s state, conflict count, and metrics of clause quality to decide whether a restart should occur. '
                            'This helps the solver to avoid getting stuck in difficult regions of the search space and potentially improve its efficiency.'
                            'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
                            'Ensure the function is significantly different and more advanced than the prior versions. '
                            'Only the C++ code for the function is required, without any additional descriptions or annotations.'
                            'Existing restarting_v0 function for reference:'
                            'If the option to restart (\'opts.restart\') is not enabled, the function immediately returns \'false\', indicating that no restart should occur.'
                            'This condition checks if the current decision level (\'level\') is less than the number of assumptions plus two. If it is, the function returns \'false\', meaning the solver is too early in its decision process to consider a restart.'
                            'If the \'stabilizing()\' function returns \'true\', the function returns the value of \'reluctant\', which indicates whether a reluctant restart should be considered based on the solver\'s stabilization state.'
                            'If the current number of conflicts (\'stats.conflicts\') is less than or equal to the restart limit (\'lim.restart\'), the function returns \'false\', meaning there haven\'t been enough conflicts to warrant a restart.'
                            'The function calculates the fast and slow exponential moving averages (EMAs) of the glue (a measure of clause quality). '
                            'It computes the restart margin based on \'opts.restartmargin\' and multiplies the slow EMA by this margin to get the limit (\'l\'). '
                            'The function returns \'true\' if the fast EMA (\'f\') is greater than or equal to the computed limit (\'l\'), indicating that the conditions for a restart have been met. Otherwise, it returns \'false\'.'
                             )
        extra_info = r'''

                        '''
        self._batch_inference = batch_inference
        self._url = url
        self._additional_prompt = additional_prompt
        self._trim = True

    def draw_samples(self, prompt: str,count_list) -> Collection[str]:
        """Returns multiple predicted continuations of `prompt`."""
        all_samples = []
        if self._batch_inference:
            response = self._do_request(prompt,count_list)
            for res in response:
                all_samples.append(res)
        else:
            for _ in range(self._samples_per_prompt):
                response = self._do_request(prompt,count_list)
                all_samples.append(response)
        # print(all_samples)
        return all_samples

    def _do_request(self, content: str,count_list) -> str:
        import re
        # import pdb;pdb.set_trace()
        content = '\n'.join([self._additional_prompt,content])
        content = '\n'.join([content, 'Your task is to create the optimized restarting_v* function based on the guidelines above. Remember, only the C++ function code is needed.'])
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
                from openai import OpenAI
                openai_api_key = "EMPTY"
                openai_api_base = "http://172.23.148.56:8000/v1"
                client = OpenAI(
                    api_key=openai_api_key,
                    base_url=openai_api_base,
                )
                
                completion = client.completions.create(model="model",
                                                    prompt=content,
                                                    temperature=0.8,
                                                        max_tokens=2048,)
                
                print("Completion result:", json.loads(completion.json())['choices'][0]['text'])
                response = json.loads(completion.json())['choices'][0]['text'] #给model发送prompt
                # --------------api implement------------------------

                # --------------api implement gpt------------------------
                # from openai import OpenAI
                # from openai import AzureOpenAI
                # openai_api_key = "f825f61246354ec090c5703ca4f76418"
                # openai_api_base = "https://midivi-main-scu1.openai.azure.com/"
                # client = AzureOpenAI(
                #   api_key = openai_api_key,  
                #   api_version = "2024-02-01",
                #   azure_endpoint = openai_api_base
                # )
                # response = client.chat.completions.create(
                #     model="gpt-35-turbo",
                #     messages=[
                #         {"role": "system", "content": "You are a helpful assistant"},
                #         {"role": "user", "content": content},
                #     ],
                #     stream=False
                # )
                # print("Completion result:",response.choices[0].message.content)
                # response = response.choices[0].message.content
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
            script_path = os.path.expanduser("~/Fun_SAT/implementation/cadical/temp/cadical.sh")
            data_path = os.path.expanduser("~/Fun_SAT/implementation/EasySAT-main/dataset/"+data_set)
           

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
            prefix = '/home/ubuntu/Fun_SAT/implementation/EasySAT-main/dataset/'+data_set+'/'

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
                if task_content.startswith(prefix):
                    task_content = task_content[len(prefix):]
                
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
                data_path,
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
                        if task_content.startswith(prefix):
                            task_content = task_content[len(prefix):]

                        score_list_score_eval[task_content] = task_result

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

    

specification = r'''
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


'''

# It should be noted that the if __name__ == '__main__' is required.
# Because the inner code uses multiprocess evaluation.

if __name__ == '__main__':
    class_config = config.ClassConfig(llm_class=LocalLLM, sandbox_class=Sandbox)
    config = config.Config(samples_per_prompt=4)

    bin_packing_or3 = {'OR3': bin_packing_utils.datasets['OR3']}
    global_max_sample_num = 400  # if it is set to None, funsearch will execute an endless loop
    funsearch.main(
        specification=specification,
        inputs=bin_packing_or3,
        config=config,
        max_sample_nums=global_max_sample_num,
        class_config=class_config,
        log_dir= log_name+'/funsearch_local_llm_'+case_code,
    )

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

data_set='2023list1c'
timeout_value='100'
case_num='060201'
parallel_size='20'
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
                            'In the context of SAT solvers that use the VSIDS heuristic. '# the activity of a variable represents how often the variable has been involved in conflicts.'
                            'Given the existing bump_var_v0 function, please generate an optimized version named bump_variable_score_v*. '
                            # 'The function is used to handle the judgement conditions of restart function.'
                            # 'The function is used in SAT solvers to increase the activity of a variable.'
                            'The primary purpose of this function is to increase the specified variable\'s score and rescale the scores if necessary to ensure numerical stability in the scoring system. '
                            'This new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
                            'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
                            'Ensure the function is significantly different and more advanced than the prior versions. '
                            'Only the C++ code for the function is required, without any additional descriptions or annotations.'
                            'Existing bump_variable_score_v0 function for reference:'
                            'Args:'
                                'lit: The index of a literal, which is a Boolean variable or its negation.'
                            'The vidx function is used to convert the literal to its corresponding variable index idx. This index is used to access and update the variable\'s score.'
                            'The score function is called to retrieve the current score of the variable old_score. Scores are typically used in heuristic decision-making to determine which variables should be prioritized for assignment.'
                            'The current score old_score is increased by an increment value score_inc, resulting in a new score new_score. This increment is a predefined constant used to gradually increase the variable\'s score.'
                            'The evsids_limit_hit function checks if the new score exceeds a predefined limit. If it does, the scores need to be rescaled.'
                            'If the new score exceeds the limit, the rescale_variable_scores function is called to rescale all variable scores. Typically, this means reducing all scores proportionally to avoid overflow or excessively large values.'
                            'The old score is retrieved again, and the new score is recalculated. The new score is then assigned to the variable idx.'
                            'If the variable idx is already in the priority queue scores, its score is updated. This ensures that the scores in the priority queue are always up to date.'
                                # 'activity: An array that represents the activity level of variables.'
                                # 'var_inc: var_inc: A base increment (default is 1) representing the basic amount by which a variable\'s activity is increased with each conflict.'
                                # 'vars: An integer representing the total number of variables.'
                                # 'vsids: A heap structure (usually a max heap) organized according to the activity levels of variables, used to quickly select the next variable for assignment.'
                                #     'If the variable var is currently in the heap, then the heap needs to be updated to reflect the change in activity.  '
                                # 'var: The variable number whose activity is to be increased.' 
                                # 'coeff: A coefficient for adjusting the amount by which the activity is increased, typically set according to different contexts.'
                                # 'rephases: The number of conflicts since the last rephases.'
                                # 'threshold: A threshold for updating the local_best phase.'
                                # 'rephase_limit: Parameters for when to conduct rephase.'
                            #     'lbd_queue_size: The number of LBDs in this queue'
                            #     'fast_lbd_sum: Sum of the Global LBDs.'
                            #     'slow_lbd_sum: Sum of the recent 50 LBDs'
                            #     'conflicts: the number of conflicts.'
                            # 'Return:'
                            #     'A boolean value stands for the judgement conditions of restart function.'
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
        print(all_samples)
        return all_samples

    def _do_request(self, content: str,count_list) -> str:
        import re
        # import pdb;pdb.set_trace()
        content = '\n'.join([self._additional_prompt,content])
        content = '\n'.join([content, 'Your task is to create the optimized bump_variable_score_v* function based on the guidelines above. Remember, only the C++ function code is needed.'])
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
                
                from openai import OpenAI
                openai_api_key = "EMPTY"
                openai_api_base = "http://172.23.148.56:8000/v1"
                
                # --------------Local implement------------------------
                # from transformers import AutoTokenizer, AutoModelForCausalLM
                # import torch
               
                # tokenizer = AutoTokenizer.from_pretrained("/home/mail-ecnu/Public/wjh/llms/dpseek/DeepSeek-Coder/model", trust_remote_code=True)
                # model = AutoModelForCausalLM.from_pretrained("/home/mail-ecnu/Public/wjh/llms/dpseek/DeepSeek-Coder/model", trust_remote_code=True, torch_dtype=torch.bfloat16).cuda()
                # messages=[
                #     { 'role': 'user', 'content': content}
                # ]
                # inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
                # # tokenizer.eos_token_id is the id of <|EOT|> token
                # outputs = model.generate(inputs, max_new_tokens=512, do_sample=True, top_k=50, temperature = 0.9,top_p=0.95, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
                # response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
                # --------------Local implement------------------------
                
                # --------------api implement------------------------
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

                new_record['response'] = response

                data.append(new_record)

                with open(JSONfile, 'w') as outfile:
                    json.dump(data, outfile, indent=4)



                # import pdb;pdb.set_trace()
                # --------------api implement------------------------
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
    def _compile_and_run_function(self, program, function_to_run, function_to_evolve, numba_accelerate):
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
                parallel_size  
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

            result = re.search(r"SUCCESScount: (\d+(\.+\d+)?)", out.stdout)
            result = int(result.group(1))

            count_list={}
            for i in time_list:#,400,500,700,1000]:
                value = re.search(str(i)+r"Scount: (\d+(\.+\d+)?)", out.stdout)
                value = int(value.group(1))
                count_list[i] = value

            print(count_list)
            # result = re.search(r"result:(\d+(\.\d+)?)", result.stdout)
            # result = re.search(r"result:(\d+(\.\d+)?)", result.stdout)

            # result = float(result.group(1))

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
        isok, result, count_list = self._compile_and_run_function(program, function_to_run, function_to_evolve, self._numba_accelerate)
        

        # 获取结果，这部分可能需要根据你的实际情况进行调整
        #TODO:1.需要处理不运行or效果不如最佳的结果（也可以不做统计，仅保留最后最优的结果？）2.修改evulate的process为5个(done) 3.需要对启发式的bin packing code重构以兼容双NUMA的request(done)
         
        results = isok,result, count_list
        
        if self._verbose:
            print(f'================= Evaluated Program =================')
            program_: code_manipulation.Program = code_manipulation.text_to_program(text=program)
            func_to_evolve_: str = kwargs.get('func_to_evolve', 'Internal::bump_variable_score')
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
'''

# It should be noted that the if __name__ == '__main__' is required.
# Because the inner code uses multiprocess evaluation.

if __name__ == '__main__':
    class_config = config.ClassConfig(llm_class=LocalLLM, sandbox_class=Sandbox)
    config = config.Config(samples_per_prompt=4)

    bin_packing_or3 = {'OR3': bin_packing_utils.datasets['OR3']}
    global_max_sample_num = 200  # if it is set to None, funsearch will execute an endless loop
    funsearch.main(
        specification=specification,
        inputs=bin_packing_or3,
        config=config,
        max_sample_nums=global_max_sample_num,
        class_config=class_config,
        log_dir= log_name+'/funsearch_local_llm_'+case_code,
    )

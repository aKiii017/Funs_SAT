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
                            # 'Generate a different and more complex Python \'priority\' function. '
                            #  'Be creative and you can insert multiple if-else and for-loop in the code logic.'
                            #  'Only output the Python code, no descriptions.'
                            #  'Only generate the improved version of priority function,dont generate extra functions and other code annotation.'
                            #  'Improved function should be different from previous functions,and must inclue return value.Do not generate same function and code annotation.'
                            'Given the existing priority_v0 function, please generate an optimized version named priority_v*. '
                            'This new version should be more efficient, incorporating multiple conditional logic and loops as necessary. '
                            'The function is used in SAT solvers to increase the activity of a variable.'
                            'In the context of SAT solvers that use the VSIDS heuristic, the activity of a variable represents how often the variable has been involved in conflicts.'
                            'The new versions should try to help SAT solver escape from local optimum, and perform more efficiently.'
                            'Ensure the function is significantly different and more advanced than the prior versions. '
                            'Only the C++ code for the function is required, without any additional descriptions or annotations.'
                            'Existing priority_v0 function for reference:'
                            'Args:'
                                'activity: An array that represents the activity level of variables.'
                                'var_inc: var_inc: A base increment (default is 1) representing the basic amount by which a variable\'s activity is increased with each conflict.'
                                'vars: An integer representing the total number of variables.'
                                'vsids: A heap structure (usually a max heap) organized according to the activity levels of variables, used to quickly select the next variable for assignment.'
                                    'If the variable var is currently in the heap, then the heap needs to be updated to reflect the change in activity.  '
                                'var: The variable number whose activity is to be increased.' 
                                'coeff: A coefficient for adjusting the amount by which the activity is increased, typically set according to different contexts.'
                             )
        # additional_prompt = ('Be creative and you can insert multiple if-else and for-loop in the code logic.Please provide the improved priority function which is used in bin packiong problem,and just output the "priority" function, no other explanations needed.Your generated function must be different from previous functions.Use the python code to response.\nFunctions shows below.')
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
        return all_samples

    def _do_request(self, content: str,count_list) -> str:
        import re
        # import pdb;pdb.set_trace()
        content = '\n'.join([self._additional_prompt,content])
        content = '\n'.join([content, 'Your task is to create the optimized priority_v* function based on the guidelines above. Remember, only the C++ function code is needed.'])
        content = '\n'.join([content, 'Dict: '+str(count_list)])
        content = '\n'.join([content, 'In this Dict, the key represents time in seconds, and the value represents the number of instances successfully executed in the corresponding time. You should try to maximize the values.'])

        # content = '\n'.join([content, 'Score stands for the amount of instences that are successfully solved within 500s, you need to try to maximum this value.'])
       
        # first_function_end = content.find('return priorities') + len('return priorities')
        # content = content[:first_function_end] + re.sub(r'\ndef priority_v\d.*?(?=\ndef|$)', '', content[first_function_end:], flags=re.DOTALL)
        # content = '\n'.join([self._additional_prompt, content])
        # import pdb;pdb.set_trace()
        # repeat the prompt for batch inference (inorder to decease the sample delay)
        # repeat_prompt: int = self._samples_per_prompt if self._batch_inference else 1
        # data = {
        #     # 'model': 'codeLlama',
        #     # 'model': 'model',
        #     'model': 'deepseek_7B',
        #     # 'prompt': content,
        #     "messages":[
        #         {"role": "user", "content": content},
        #     ],
        #     # 'repeat_prompt': repeat_prompt,
        #     # 'system_prompt': '',
        #     # 'stream': False,
        #     'temperature': 0.5,
        #     'max_tokens': 4096,
        #     # 'top_p':1, # 可选参数，控制多样性
        #     'frequency_penalty':1, # 可选参数，降低重复内容的概率
        #     # 'params': {
        #     #     'temperature': 0.5,
        #     #     'top_k': None,
        #     #     'top_p': None,
        #     #     'add_special_tokens': False,
        #     #     'skip_special_tokens': True,
        #     # }
        # }
        # headers = {'Content-Type': 'application/json'}
        while True:
            try:
                # response = requests.post(self._url, data=json.dumps(data), headers=headers)
                
                from openai import OpenAI
                openai_api_key = "EMPTY"
                openai_api_base = "http://localhost:8000/v1"
                
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
                openai_api_base = "http://localhost:8000/v1"
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
            script_path = os.path.expanduser("/mnt/data/linyanqiu/Fun_SAT/implementation/EasySAT-main/EasySAT.sh")

           
            # command_make = [
            #     "make","-C",
            #     "/mnt/data/linyanqiu/Fun_SAT/implementation/EasySAT-main",
            #     # script_path
            # ]
            import re

            command_run = [
                # "make","-C",
                # "/mnt/data/linyanqiu/Fun_SAT/implementation/EasySAT-main",
                script_path
            ]
            import re
            # 运行命令
            # subprocess.run(command_make, capture_output=True, text=True, check=True)
            out = subprocess.run(command_run, capture_output=True, text=True, check=True)

            flag = out.returncode
            # result = float(result.stdout)
            # result = re.search(r"AVGtime: (-\d+(\.+\d+)?)", result.stdout)
            result = re.search(r"SUCCESScount: (\d+(\.+\d+)?)", out.stdout)
            result = int(result.group(1))

            count_list={}
            for i in [100,200,300,400,500,1000]:
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
            func_to_evolve_: str = kwargs.get('func_to_evolve', 'priority')
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
#include "EasySAT.hpp"
#include <fstream>
using namespace std;

void priority(double*& activity, double& var_inc, int vars, Heap<GreaterActivity>& vsids, int var, double coeff) {
    const double MAX_ACTIVITY = 700, ACTIVITY_FACTOR = 0.9, DECAY_FACTOR = 0.95, DECAY_THRESHOLD = 0.001;
    double& var_activity = activity[var];

    // Increase the activity of the variable by the coeff
    var_activity += coeff;

    // Increase the base increment var_inc if the variable's activity is at the maximum threshold
    if (var_activity >= MAX_ACTIVITY) {
        var_activity = MAX_ACTIVITY;
        for (int i = 0; i < vars; ++i)
            activity[i] *= ACTIVITY_FACTOR;
        var_inc *= ACTIVITY_FACTOR;
    }
    // If the variable's activity is below the decay threshold, reset activity to 0
    else if (var_activity < DECAY_THRESHOLD) {
        activity[var] = 0.0;
        var_inc *= DECAY_FACTOR;
        for (int i = 0; i < vars; ++i)
            activity[i] *= DECAY_FACTOR;
    }

    // Update the variable in the heap
    vsids.update(var);
}

'''

# It should be noted that the if __name__ == '__main__' is required.
# Because the inner code uses multiprocess evaluation.

if __name__ == '__main__':
    class_config = config.ClassConfig(llm_class=LocalLLM, sandbox_class=Sandbox)
    config = config.Config(samples_per_prompt=4)

    bin_packing_or3 = {'OR3': bin_packing_utils.datasets['OR3']}
    global_max_sample_num = 2000  # if it is set to None, funsearch will execute an endless loop
    funsearch.main(
        specification=specification,
        inputs=bin_packing_or3,
        config=config,
        max_sample_nums=global_max_sample_num,
        class_config=class_config,
        log_dir='logs/funsearch_local_llm_2023list1000_1000_042001',
    )


# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch
# content = '''
# Given the existing priority_v0 function, please generate an optimized version named priority_v*. This new version should be more complex and efficient, incorporating multiple conditional logic and loops as necessary. The function should calculate priorities for items to be added to bins, considering the item size and bin capacities. Ensure the function is significantly different and more advanced than the prior versions. Only the Python code for the function is required, without any additional descriptions or annotations.

# Existing priority_v0 function for reference:

# import numpy as np

# def priority_v0(item: float, bins: np.ndarray) -> np.ndarray:
#     """Returns priority with which we want to add item to each bin.

#     Args:
#         item: Size of item to be added to the bin.
#         bins: Array of capacities for each bin.

#     Return:
#         Array of same size as bins with priority score of each bin.
#     """
#     ratios = item / bins
#     log_ratios = np.log(ratios)
#     priorities = -log_ratios
#     return priorities

# Your task is to create one optimized priority_v* function based on the guidelines above. Remember, only the Python function code is needed,do not response the prompt.
# '''
# # content = '#Complete a different and more complex \'priority\' function. Be creative and you can insert multiple if-else and for-loop in the code logic.Only output the Python code, no descriptions.Improved function should be different from previous functions,and must inclue return value.Do not generate same function and code annotation.\n\nimport numpy as np\n\n\ndef priority_v0(item: float, bins: np.ndarray) -> np.ndarray:\n    """Returns priority with which we want to add item to each bin.\n\n    Args:\n        item: Size of item to be added to the bin.\n        bins: Array of capacities for each bin.\n\n    Return:\n        Array of same size as bins with priority score of each bin.\n    """\n    ratios = item / bins\n    log_ratios = np.log(ratios)\n    priorities = -log_ratios\n    return priorities\n\n\n \n def priority_v1(item: float, bins: np.ndarray) -> np.ndarray:\n    """Improved version of `priority_v0`.Improved function should be different from previous functions.Do not generate same function and code annotation."""\n\n\n '
# content = '\nimport numpy as np\n\n\ndef priority_v0(item: float, bins: np.ndarray) -> np.ndarray:\n    """Returns priority with which we want to add item to each bin.\n\n    Args:\n        item: Size of item to be added to the bin.\n        bins: Array of capacities for each bin.\n\n    Return:\n        Array of same size as bins with priority score of each bin.\n    """\n    ratios = item / bins\n    log_ratios = np.log(ratios)\n    priorities = -log_ratios\n    return priorities\n\n\n *** def priority_v1(item: float, bins: np.ndarray) -> np.ndarray:\n    """Improved version of `priority_v0`.Improved function should be different from previous functions.Do not generate same function and code annotation."""\n\n\n '



# from transformers import AutoTokenizer, AutoModelForCausalLM
# tokenizer = AutoTokenizer.from_pretrained("/home/mail-ecnu/Public/wjh/llms/dpseek/DeepSeek-Coder/model", trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained("/home/mail-ecnu/Public/wjh/llms/dpseek/DeepSeek-Coder/model", trust_remote_code=True).cuda()
# messages=[
#     { 'role': 'user', 'content': content}
# ]
# inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)

# outputs = model.generate(inputs, max_new_tokens=512, do_sample=True, temperature=0.8,top_k=50, top_p=0.95, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
# print(tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True))
# import pdb;pdb.set_trace()

                                                                      
from openai import OpenAI
from transformers import AutoTokenizer
import json
# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://127.0.0.1:6066"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
# tokenizer = AutoTokenizer.from_pretrained("/home/mail-ecnu/Public/wjh/llms/deepseek_7B", trust_remote_code=True)
# content = '\nimport numpy as np\n\n\ndef priority_v0(item: float, bins: np.ndarray) -> np.ndarray:\n    """Returns priority with which we want to add item to each bin.\n\n    Args:\n        item: Size of item to be added to the bin.\n        bins: Array of capacities for each bin.\n\n    Return:\n        Array of same size as bins with priority score of each bin.\n    """\n    ratios = item / bins\n    log_ratios = np.log(ratios)\n    priorities = -log_ratios\n    return priorities\n\n\ndef priority_v1(item: float, bins: np.ndarray) -> np.ndarray:\n    """Improved version of `priority_v0`.Improved function should be different from previous functions.Do not generate same function and code annotation."""\n\n\n"""Complete a different and more complex Python function. Be creative and you can insert multiple if-else and for-loop in the code logic.Only output the Python code, no descriptions.Pls just complete the improved version of priority function,just one function will be generated,dont generate extra functions."""'
# content = '\nimport numpy as np\n\n\ndef priority_v0(item: float, bins: np.ndarray) -> np.ndarray:\n    """Returns priority with which we want to add item to each bin.\n\n    Args:\n        item: Size of item to be added to the bin.\n        bins: Array of capacities for each bin.\n\n    Return:\n        Array of same size as bins with priority score of each bin.\n    """\n    ratios = item / bins\n    log_ratios = np.log(ratios)\n    priorities = -log_ratios\n    return priorities\n\n\n *** def priority_v1(item: float, bins: np.ndarray) -> np.ndarray:\n    """Improved version of `priority_v0`.Improved function should be different from previous functions.Do not generate same function and code annotation."""\n\n\n '
# content = '\nimport numpy as np\n\n\ndef priority_v0(item: float, bins: np.ndarray) -> np.ndarray:\n    """Returns priority with which we want to add item to each bin.\n\n    Args:\n        item: Size of item to be added to the bin.\n        bins: Array of capacities for each bin.\n\n    Return:\n        Array of same size as bins with priority score of each bin.\n    """\n    ratios = item / bins\n    log_ratios = np.log(ratios)\n    priorities = -log_ratios\n    return priorities\n\n\n #Complete a different and more complex Python function. Be creative and you can insert multiple if-else and for-loop in the code logic.Only output the Python code, no descriptions.Pls just complete the improved version of priority function,just one function will be generated,dont generate extra functions.\n def priority_v1(item: float, bins: np.ndarray) -> np.ndarray:\n    """Improved version of `priority_v0`.Improved function should be different from previous functions.Do not generate same function and code annotation."""\n\n\n '
# content = '#Complete a different and more complex \'priority\' function. Be creative and you can insert multiple if-else and for-loop in the code logic.Only output the Python code, no descriptions.Improved function should be different from previous functions,and must inclue return value.Do not generate same function and code annotation.\n\nimport numpy as np\n\n\ndef priority_v0(item: float, bins: np.ndarray) -> np.ndarray:\n    """Returns priority with which we want to add item to each bin.\n\n    Args:\n        item: Size of item to be added to the bin.\n        bins: Array of capacities for each bin.\n\n    Return:\n        Array of same size as bins with priority score of each bin.\n    """\n    ratios = item / bins\n    log_ratios = np.log(ratios)\n    priorities = -log_ratios\n    return priorities\n\n\n \n def priority_v1(item: float, bins: np.ndarray) -> np.ndarray:\n    """Improved version of `priority_v0`.Improved function should be different from previous functions.Do not generate same function and code annotation."""\n\n\n '
content = '''
Given the existing priority_v0 function, please generate an optimized version named priority_v2. This new version should be more complex and efficient, incorporating multiple conditional logic and loops as necessary. The function should calculate priorities for items to be added to bins, considering the item size and bin capacities. Ensure the function is significantly different and more advanced than the prior versions. Only the Python code for the function is required, without any additional descriptions or annotations.

Existing priority_v0 function for reference:

import numpy as np

def priority_v0(item: float, bins: np.ndarray) -> np.ndarray:
    """Returns priority with which we want to add item to each bin.

    Args:
        item: Size of item to be added to the bin.
        bins: Array of capacities for each bin.

    Return:
        Array of same size as bins with priority score of each bin.
    """
    ratios = item / bins
    log_ratios = np.log(ratios)
    priorities = -log_ratios
    return priorities

Your task is to create the optimized priority_v2 function based on the guidelines above. Remember, only the Python function code is needed.
'''
# content = 'Please provide the improved priority function based on original function,and only output the code,do not add descriptions.This function is used in bin packiong problem.Functions shows below.\n\nimport numpy as np\n\n\ndef priority_v0(item: float, bins: np.ndarray) -> np.ndarray:\n    """Returns priority with which we want to add item to each bin.\n\n    Args:\n        item: Size of item to be added to the bin.\n        bins: Array of capacities for each bin.\n\n    Return:\n        Array of same size as bins with priority score of each bin.\n    """\n    ratios = item / bins\n    log_ratios = np.log(ratios)\n    priorities = -log_ratios\n    return priorities\n\n\n """\n\n\nThe example response should be like:\n def priority_v*(item: float, bins: np.ndarray) -> np.ndarray:\n    return -(bins - item) * (bins >= item)\n'

from openai import OpenAI

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
completion = client.completions.create(model="model",
                                      prompt=content,
                                      temperature=0.8,
                                        max_tokens=1024,)
print("Completion result:", json.loads(completion.json())['choices'][0]['text'])
import pdb;pdb.set_trace()
# content = tokenizer(content, return_tensors="pt")
completion = client.chat.completions.create(
                                    model='deepseek_7B',
                                    messages=[
                                        {"role": "user", "content": content},
                                    ],
                                    # prompt=content,
                                    max_tokens=512, # 设置生成文本的最大长度
                                    temperature=0.5, # 可选参数，控制创新性
                                    # # top_p=1, # 可选参数，控制多样性
                                    # frequency_penalty=1, # 可选参数，降低重复内容的概率
                                    )
# json.loads(completion.json())['choices'][0]['text']
# print("Completion result:", json.loads(completion.json())['choices'][0]['text'])
# output_ids = completion  # 假设这是从模型获取的输出
# decoded_output = tokenizer.decode(output_ids[0], skip_special_tokens=True)


print('------------')
print("Completion result:", json.loads(completion.json())['choices'][0]['text'])
# print("Completion result:", json.loads(completion.json())['choices'][0]['message']['content'])
import pdb;pdb.set_trace()
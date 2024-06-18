import re
import subprocess

# 用于存储结果的字典
results_dict = {}

# 前缀字符串
prefix = '/home/ubuntu/Fun_SAT/implementation/EasySAT-main/dataset/test/'

# 假设你的命令是 command_run
command_run = ['your_command_here']

# 运行命令并捕获输出
out = subprocess.run(command_run, capture_output=True, text=True, check=True)

# 获取命令输出
data = out.stdout

# 正则表达式模式，用于匹配 TASK、其后到 RUNtime 之前的内容和 RESULT
pattern = r'\[TASK(\d+)\](.*?)\[RUNtime\].*?\[RESULT\](SATISFIABLE|UNSATISFIABLE)'

# 查找所有匹配的内容
matches = re.findall(pattern, data, re.DOTALL)

# 将匹配结果存储到字典中
for match in matches:
    task_number = f'TASK{match[0]}'
    task_content = match[1].strip()
    result = match[2]
    
    # 去掉前缀字符串
    if task_content.startswith(prefix):
        task_content = task_content[len(prefix):]
    
    results_dict[task_number] = {'content': task_content, 'result': result}

# 打印结果字典
print(results_dict)

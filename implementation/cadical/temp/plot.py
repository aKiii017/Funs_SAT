import re
import matplotlib.pyplot as plt

# 文件路径列表
file_paths = [
    '/home/ubuntu/Fun_SAT/implementation/cadical/temp/2023_1500_cadical_20.txt',
    '/home/ubuntu/Fun_SAT/implementation/cadical/temp/2023_1500_kissat_20.txt',
    '/home/ubuntu/Fun_SAT/implementation/cadical/temp/2023_1500_SBVAcadical_20.txt',
    '/home/ubuntu/Fun_SAT/implementation/cadical/temp/2023_1500_061201_20.txt',
    '/home/ubuntu/Fun_SAT/implementation/cadical/temp/2023_1500_061401_20.txt'
# 添加更多文件路径
]

# 设置颜色和标签
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
labels = ['cadical', 'kissat', 'SBVA-cadical', 'cadical-restart-t100', 'cadical-restart-bump-t100', 'File 6', 'File 7']

# 绘制图形
plt.figure(figsize=(10, 10))

for idx, file_path in enumerate(file_paths):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # 提取任务信息的正则表达式
    task_pattern = re.compile(r'\[TASK\d+\].*?\[(RUNtime)\](\d+\.?\d*) s', re.DOTALL)
    
    # 提取所有任务的运行时间或超时时间，并转换为整数
    task_times = [int(round(float(match.group(2)))) for match in task_pattern.finditer(content)]

    task_times.sort()
    
    # 以10秒为间隔计算x秒内完成的任务总数
    interval = 10
    time_intervals = range(interval, task_times[-1] + interval, interval)  # 以10秒为间隔
    completed_tasks = [sum(1 for time in task_times if time <= t) for t in time_intervals]
    
    # 在同一图中绘制每个文件的数据
    plt.plot(time_intervals, completed_tasks, marker='x', linestyle='-', markersize=5,  markeredgewidth=0.5,
             linewidth=0.5, markerfacecolor='none', color=colors[idx % len(colors)], label=labels[idx])

plt.xlabel('Time (s)')
plt.ylabel('Number of solved instances')
# plt.title('Number of Tasks Completed within x Seconds')
plt.legend()
plt.grid(True)

# 显示图形
# plt.show()

# 或者保存图形为文件
plt.savefig('completed_tasks_plot_multiple_files.png')

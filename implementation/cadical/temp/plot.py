import re
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

# 设置全局字体大小
plt.rcParams.update({'font.size': 23})  # 设置默认字体大小为10pt

# 若要使其他元素如图例更清晰，也可以单独设置
plt.rcParams['legend.fontsize'] = 18  # 小号字体用于图例，因为通常需要更紧凑一些

# 文件路径列表和绘图设置
file_paths = [
    '/home/ubuntu/Fun_SAT/implementation/cadical/temp/2023_1500_cadical_20.txt',
    '/home/ubuntu/Fun_SAT/implementation/cadical/temp/2023_1500_051002_20.txt',
]
colors = ['r', 'b']
labels = [
    'cadical-original',
    'cadical-after optimization'
]

plt.figure(figsize=(10, 7))   # 适当调整尺寸，以便适合论文格式

for idx, file_path in enumerate(file_paths):
    with open(file_path, 'r') as file:
        content = file.read()
    
    task_pattern = re.compile(r'\[TASK\d+\].*?\[(RUNtime)\](\d+\.?\d*) s', re.DOTALL)
    task_times = [int(round(float(match.group(2)))) for match in task_pattern.finditer(content)]
    task_times.sort()
    
    interval = 10
    time_intervals = range(interval, task_times[-1] + interval, interval)
    completed_tasks = [sum(1 for time in task_times if time <= t) for t in time_intervals]
    
    plt.plot(time_intervals, completed_tasks, marker='x', linestyle='-', markersize=5, 
             markeredgewidth=0.5, linewidth=0.5, markerfacecolor='none', color=colors[idx % len(colors)], label=labels[idx])

plt.xlabel('Time (s)')
plt.ylabel('Number of solved instances')
plt.legend()
plt.grid(True)
# 调整上下边距
plt.subplots_adjust(bottom=0.12, top=0.95)  # 调整这些值以优化上下边距
# 保存图形（推荐PDF格式以保持清晰度）
plt.savefig('completed_tasks_plot_multiple_files.pdf', format='pdf')  # 保存为PDF以保持最佳质量
plt.savefig('completed_tasks_plot_multiple_files.png')  # 保存为PDF以保持最佳质量

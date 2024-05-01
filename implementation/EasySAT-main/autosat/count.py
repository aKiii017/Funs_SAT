def read_and_process_file(filepath):
    # 读取文件内容
    with open(filepath, 'r') as file:
        content = file.read()

    # 寻找所有的时间记录
    import re
    pattern = r"Function took (\d+) seconds to complete."
    results = re.findall(pattern, content)

    # 转换为整数
    times = list(map(int, results))

    # 计算不同区间的数量
    counts = {
        '<100': sum(1 for time in times if time < 100),
        '<200': sum(1 for time in times if time < 200),
        '<300': sum(1 for time in times if time < 300),
        '<400': sum(1 for time in times if time < 400),
        '<500': sum(1 for time in times if time < 500),
        '<700': sum(1 for time in times if time < 700),
        '<1000': sum(1 for time in times if time < 1000),
        '<1500': sum(1 for time in times if time < 1500),
        '>=1500': sum(1 for time in times if time >= 1500),

    }

    # 计算平均值
    # 如果值为1500，算作3000，否则算作其本身
    adjusted_times = [3000 if time == 1500 else time for time in times]
    average = sum(adjusted_times) / len(adjusted_times)

    return counts, average

# 文件路径
filepath = './2022.txt'

# 处理文件并获取结果
counts, average = read_and_process_file(filepath)

# 打印结果
print("Counts:", counts)
print("Average time:", average)

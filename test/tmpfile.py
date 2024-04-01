import subprocess
import tempfile

# 创建临时C++文件
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cpp') as tmp:
    # 写入priority函数定义
    tmp.write("""
#include <iostream>
void priority(int x) {
    std::cout << "Priority function from tempfile: " << x << std::endl;
}
""")
    tmp_path = tmp.name  # 保存临时文件的路径
print(tmp_path)

# 编译test.cpp，将临时文件名作为宏定义传递给编译器
compile_command = ['g++', '-o', 'test', 'test.cpp', f'-DPRIORITY_FILE=\"{tmp_path}\"']
print(compile_command)
compile_process = subprocess.run(compile_command, capture_output=True, text=True)

if compile_process.returncode == 0:
    print("编译成功，执行程序：")
    # 执行编译后的程序
    execution_process = subprocess.run(['./test'], capture_output=True, text=True)
    print(execution_process.stdout)
else:
    print("编译失败:")
    print(compile_process.stderr)
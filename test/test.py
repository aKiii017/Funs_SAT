import re

def extract_priority_function_body(code):
    # 查找函数开始的位置
    pattern_start = r"void Solver::priority\(.*?\)\s*{"
    start_match = re.search(pattern_start, code)
    if not start_match:
        return "Function start not found."

    # 从函数声明的开花括号开始，向后查找匹配的闭花括号
    open_braces_count = 1  # 开始时计数器为1，因为我们找到了开花括号
    start_index = start_match.end() - 1  # 减去1是因为我们要包括这个开花括号

    # 初始化函数体结束索引为-1，表示未找到
    end_index = -1

    # 从函数声明花括号后的第一个字符开始遍历
    for i in range(start_index + 1, len(code)):
        if code[i] == '{':
            open_braces_count += 1
        elif code[i] == '}':
            open_braces_count -= 1
            if open_braces_count == 0:
                # 找到了匹配的闭花括号
                end_index = i
                break

    if end_index == -1:
        return "Function end not found."

    # 提取函数体，包括所有内部的代码，但不包括首尾的花括号
    function_body = code[start_index + 1:end_index].strip()
    
    # 可选：处理缩进，这里简单地移除每行开头的空白字符
    function_body_lines = function_body.split('\n')
    function_body_dedented = "\n".join(line.lstrip() for line in function_body_lines)

    return function_body

# 示例用的C++代码字符串
cpp_code = """
// Example C++ code snippet
void Solver::priority(int var) {
    // This is the function body
    if (var > 0) {
        // Do something
    } else {
        // Do something else
    }
    if (true) {
        // Nested block
    }
}
"""

# 调用函数，提取Solver::priority函数体
extracted_body = extract_priority_function_body(cpp_code)
print(extracted_body)

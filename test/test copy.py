import re

def parse_cpp_function(code):
    # 删除代码中的字符串内容，避免干扰解析
    # code = re.sub(r'".*?"', '', code)
    
    # 处理单行和多行注释
    single_line_comments = re.findall(r'//.*', code)
    multi_line_comments = re.findall(r'/\*.*?\*/', code, re.DOTALL)
    comments = single_line_comments + multi_line_comments
    code_without_comments = re.sub(r'//.*|/\*.*?\*/', '', code)
    print(comments)
    # 用正则表达式匹配函数定义
    function_pattern = re.compile(r'(\w[\w\s\*]*\*?)\s+(\w+)\s*\((.*?)\)\s*{(.*)}', re.DOTALL)
    match = function_pattern.search(code_without_comments)
    if not match:
        return None
    
    return_type, function_name, params, body = match.groups()
    params = params.split(',') if params else []
    params = [param.strip() for param in params]
    
    return {
        'return_type': return_type.strip(),
        'function_name': function_name.strip(),
        'params': params,
        'body': body.strip(),
        'comments': comments
    }

# 示例代码
cpp_code = """
// 计算两个数的和
int add(int a, int b) {
    return a + b; // 返回和
}
"""

parsed_function = parse_cpp_function(cpp_code)
print(parsed_function)

import clang.cindex
import dataclasses
from typing import List, Optional
import tempfile
import os

cpp_code = """
#include "EasySAT.hpp"
void Solver::bump_var_v0(var, coeff) 
{
    /*
    The function is used in SAT solvers to increase the activity of a variable.
    Args:
        var: The variable whose activity is to be changed. 
        coeff: To adjust the coefficient of variable activity. 
    */
    if ((activity[var] += var_inc * coeff) > 1e100) {           // Update score and prevent float overflow
        for (int i = 1; i <= vars; i++) activity[i] *= 1e-100;
        var_inc *= 1e-100;}
    if (vsids.inHeap(var)) vsids.update(var);                 // update heap
}"""

@dataclasses.dataclass
class Function:
    name: str
    args: str
    body: str
    return_type: str
    docstring: Optional[str] = None

@dataclasses.dataclass
class Program:
    functions: List[Function]
    preface: str = ""

def get_function_body(func_node):
    extent = func_node.extent
    start_token = extent.start
    end_token = extent.end
    with open(start_token.file.name, 'r') as file:
        file_content = file.read()
        start_offset = file_content.find('{', start_token.offset)
        end_offset = file_content.rfind('}', start_offset, end_token.offset)
        if start_offset != -1 and end_offset != -1:
            return file_content[start_offset:end_offset+1]  # 包括大括号
        else:
            return ""

def print_function_info(func_node, source_file_path) -> Optional[Function]:
    # 确保函数是在我们感兴趣的源文件中定义的
    if func_node.location.file is None or os.path.abspath(func_node.location.file.name) != os.path.abspath(source_file_path):
        return None

    # 提取类名（如果存在）
    parent = func_node.semantic_parent
    class_name = ""
    if parent and parent.kind in [clang.cindex.CursorKind.CLASS_DECL, clang.cindex.CursorKind.STRUCT_DECL, clang.cindex.CursorKind.CLASS_TEMPLATE]:
        class_name = parent.spelling + "::"
    elif parent.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
        # 如果没有父节点且是直接在翻译单元下定义的成员函数
        class_name = func_node.semantic_parent.spelling + "::"

    # 提取函数签名
    function_name = class_name + func_node.spelling
    return_type = func_node.result_type.spelling
    params = ', '.join([param.spelling for param in func_node.get_arguments()])

    # 提取函数体和潜在的文档字符串
    body = get_function_body(func_node)
    docstring = None  # Docstrings are not standard in C++, but you could extract comments if desired

    return Function(name=function_name, args=params, body=body, return_type=return_type, docstring=docstring)

def text_to_program(code: str, include_paths: Optional[List[str]] = None) -> Program:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.cpp') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(code.encode('utf-8'))

    index = clang.cindex.Index.create()
    args = ['-std=c++11']
    if include_paths:
        for path in include_paths:
            args.append(f'-I{path}')
    
    tu = index.parse(temp_file_path, args=args)  # 解析C++代码，使用C++11标准
    functions = []
    preface_end_line = None
    for node in tu.cursor.walk_preorder():
        if node.kind in [clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD]:
            function = print_function_info(node, temp_file_path)
            if preface_end_line is None or node.extent.start.line - 1 < preface_end_line:
                preface_end_line = node.extent.start.line - 1
            if function is not None:
                functions.append(function)
    preface_text = ""
    if preface_end_line is not None:
        preface_lines = code.splitlines()[:preface_end_line]
        preface_text = "\n".join(preface_lines)
    
    os.remove(temp_file_path)
    return Program(functions=functions, preface=preface_text)

# 使用 Solver.hpp 的绝对路径
include_paths = ["/home/ubuntu/Fun_SAT/implementation/EasySAT-main"]
program = text_to_program(cpp_code, include_paths=include_paths)
print("Preface:", program.preface)
print("Functions:", len(program.functions))
for func in program.functions:
    print(f"Function name: {func.name}")
    print(f"Arguments: {func.args}")
    print(f"Return type: {func.return_type}")
    print(f"Body:\n{func.body}")

import clang.cindex
import tempfile
from typing import List, Optional
import dataclasses
import os
@dataclasses.dataclass
class Function:
    name: str
    args: str
    body: str
    return_type: str

    def __str__(self):
        return f'Function Name: {self.name}\n' \
               f'Arguments: {self.args}\n' \
               f'Return Type: {self.return_type}\n' \
               f'Function Body:\n{self.body}\n'

@dataclasses.dataclass
class Program:
    functions: List[Function]
    preface: Optional[str] = None

    def __str__(self) -> str:
        program = f"{self.preface}\n" if self.preface else ""
        program += '\n'.join(str(f) for f in self.functions)
        return program

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

    return Function(name=function_name, args=params, body=body, return_type=return_type)

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

def text_to_program(code: str) -> Program:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.cpp') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(code.encode('utf-8'))

    # include_paths = ["/home/ubuntu/Fun_SAT/implementation/cadical/src"]
    # include_paths = ["/home/ubuntu/Fun_SAT/implementation/SBVA"]
    # include_paths = ["/home/ubuntu/Fun_SAT/implementation/EasySAT-main"]
    # include_paths = ["/home/ubuntu/Fun_SAT/implementation/kissat/src"]
    include_paths = ["/home/ubuntu/z3/src"]

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

# 示例C代码字符串，包含<stdbool.h>以确保bool被正确处理
c_code = """
#include "sat/sat_solver.h"
using namespace sat;

void solver::inc_activity(bool_var v)
{
    unsigned &act = m_activity[v];
    act += m_activity_inc+1;
    m_case_split_queue.activity_increased_eh(v);
    if (act > (1 << 24))
        rescale_activity();
}
"""

# 解析C代码字符串
file_path='/home/ubuntu/z3/src/sat/inc_activity.cpp'
program = text_to_program(c_code)
print(program)

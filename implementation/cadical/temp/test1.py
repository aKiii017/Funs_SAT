import clang.cindex
import tempfile
from typing import List, Optional
import dataclasses

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

def parse_c_code_from_string(source_code: str) -> Program:
    with tempfile.NamedTemporaryFile(suffix=".c", delete=True) as temp_file:
        temp_file.write(source_code.encode())
        temp_file.flush()

        index = clang.cindex.Index.create()
        args = ['-x', 'c', '--include-directory=/usr/lib/llvm-10/lib/clang/10.0.0/include']
        tu = index.parse(temp_file.name, args=args)

        functions = []
        first_function_position = len(source_code)
        preface = None
        for node in tu.cursor.walk_preorder():
            if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
                function_position = node.extent.start.offset
                if function_position < first_function_position:
                    first_function_position = function_position
                function_name = node.spelling
                return_type = node.result_type.spelling
                if return_type == '_Bool':
                    return_type='bool'
                params = ', '.join([param.spelling for param in node.get_arguments()])
                extent = node.extent
                start = extent.start.offset
                end = extent.end.offset
                body = source_code[start:end]
                brace_open = body.find('{')
                brace_close = body.rfind('}')
                if brace_open != -1 and brace_close != -1 and brace_close > brace_open:
                    body = body[brace_open:brace_close+1]
                functions.append(Function(name=function_name, args=params, body=body, return_type=return_type))

        if first_function_position != len(source_code):
            preface = source_code[:first_function_position]

        return Program(functions=functions, preface=preface)

# 示例C代码字符串，包含<stdbool.h>以确保bool被正确处理
c_code = """
#include <stdbool.h>
#include "internal.h"
#include "restart.h"

bool kissat_restarting(kissat *solver) {
  // function implementation
}
"""

# 解析C代码字符串
program = parse_c_code_from_string(c_code)
print(program)

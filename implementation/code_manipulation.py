# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Tools for manipulating Python code.

It implements 2 classes representing unities of code:
- Function, containing all the information we need about functions: name, args,
  body and optionally a return type and a docstring.
- Program, which contains a code preface (which could be imports, global
  variables and classes, ...) and a list of Functions.

RZ: The frequently used word 'call' in this file refers to the name of the function. For example the following:
def add_five(param) -> int:
    return param + 5
The 'call' of the function is 'add_file'.
"""
from __future__ import annotations

import ast
from collections.abc import Iterator, MutableSet, Sequence
import dataclasses
import io
import tokenize
import clang.cindex
import os
import tempfile
from typing import List, Optional
from absl import logging

@dataclasses.dataclass
class Function:
    """A parsed C++ function."""
    name: str
    args: str
    body: str
    return_type: str
    docstring: Optional[str] = None
    score: int | None = None  # RZ: add this to record the score of the function.
    global_sample_nums: int | None = None  # RZ: record the order of the current program in the sequence of samples taken.
    sample_time: float | None = None  # RZ: add this
    evaluate_time: float | None = None  # RZ: add this

    def __str__(self) -> str:
        docstring = f'/* {self.docstring} */\n' if self.docstring else ''
        return f'{self.return_type} {self.name}({self.args}) \n{docstring}{self.body}\n\n'

    def __setattr__(self, name: str, value: str) -> None:
        # Ensure there aren't leading & trailing new lines in `body`.
        if name == 'body':
            value = value.strip('\n')
        # Ensure there aren't leading & trailing quotes in `docstring``.
        if name == 'docstring' and value is not None:
            if '"""' in value:
                value = value.strip()
                value = value.replace('"""', '')
        super().__setattr__(name, value)


@dataclasses.dataclass
class Program:
    """A parsed C++ program."""
    functions: List[Function]
    # `preface` is everything from the beginning of the code till the first
    # function is found.
    preface: str | None = None

    def __str__(self) -> str:
        program = f'{self.preface}\n' if self.preface else ''
        program += '\n'.join(str(f) for f in self.functions)
        return program

    def find_function_index(self, function_name: str) -> int:
        """Returns the index of input function name."""
        function_names = [f.name for f in self.functions]
        count = function_names.count(function_name)
        if count == 0:
            raise ValueError(
                f'function {function_name} does not exist in program:\n{str(self)}'
            )
        if count > 1:
            raise ValueError(
                f'function {function_name} exists more than once in program:\n'
                f'{str(self)}'
            )
        index = function_names.index(function_name)
        return index

    def get_function(self, function_name: str) -> Function:
        index = self.find_function_index(function_name)
        return self.functions[index]


class ProgramVisitor(ast.NodeVisitor):
    """Parses code to collect all required information to produce a `Program`.

    Note that we do not store function decorators.
    """

    def __init__(self, sourcecode: str):
        self._codelines: list[str] = sourcecode.splitlines()
        self._preface: str = ''
        self._functions: list[Function] = []
        self._current_function: str | None = None

    def visit_FunctionDef(self,  # pylint: disable=invalid-name
                          node: ast.FunctionDef) -> None:
        """Collects all information about the function being parsed."""
        if node.col_offset == 0:  # We only care about first level functions.
            self._current_function = node.name
            if not self._functions:
                self._preface = '\n'.join(self._codelines[:node.lineno - 1])
            function_end_line = node.end_lineno
            body_start_line = node.body[0].lineno - 1
            # Extract the docstring.
            docstring = None
            if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                docstring = f'  """{ast.literal_eval(ast.unparse(node.body[0]))}"""'
                if len(node.body) > 1:
                    body_start_line = node.body[1].lineno - 1
                else:
                    body_start_line = function_end_line

            self._functions.append(Function(
                name=node.name,
                args=ast.unparse(node.args),  # RZ: ast.unparse() failed in Python3.8. Let us try Python3.9
                return_type=ast.unparse(node.returns) if node.returns else None,
                docstring=docstring,
                body='\n'.join(self._codelines[body_start_line:function_end_line]),
            ))
        self.generic_visit(node)

    def return_program(self) -> Program:
        return Program(preface=self._preface, functions=self._functions)

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

    include_paths = ["/home/ubuntu/Fun_SAT/implementation/cadical/src"]
    # include_paths = ["/home/ubuntu/Fun_SAT/implementation/SBVA"]

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

# def text_to_program(text: str) -> Program:
#     """Returns Program object by parsing input text using Python AST.
#     """
#     try:
#         # We assume that the program is composed of some preface (e.g. imports,
#         # classes, assignments, ...) followed by a sequence of functions.
#         tree = ast.parse(text)
#         visitor = ProgramVisitor(text)
#         visitor.visit(tree)
#         return visitor.return_program()
#     except Exception as e:
#         logging.warning('Failed parsing %s', text)
#         raise e
    

def text_to_function(text: str) -> Function:
    """Returns Function object by parsing input text using Python AST."""

    text="using namespace CaDiCaL;\n"+text
    text="#include \"internal.hpp\"\n"+text
    # text="using namespace std;\n"+text
    # text="#include \"sbva.hpp\"\n"+text

    # include_paths = ["/home/ubuntu/Fun_SAT/implementation/EasySAT-main"]
    program = text_to_program(text)
    # print('program:',program)
    # print("Preface:", program.preface)
    # print("Functions:", len(program.functions))
    # for func in program.functions:
    #     print(f"Function name: {func.name}")
    #     print(f"Arguments: {func.args}")
    #     print(f"Return type: {func.return_type}")
    #     print(f"Body:\n{func.body}")

    if len(program.functions) != 1:
        raise ValueError(f'Only one function expected, got {len(program.functions)}'
                         f':\n{program.functions}')
    return program.functions[0]


def _tokenize(code: str) -> Iterator[tokenize.TokenInfo]:
    """Transforms `code` into Python tokens."""
    code_bytes = code.encode()
    code_io = io.BytesIO(code_bytes)
    return tokenize.tokenize(code_io.readline)


def _untokenize(tokens: Sequence[tokenize.TokenInfo]) -> str:
    """Transforms a list of Python tokens into code."""
    code_bytes = tokenize.untokenize(tokens)
    return code_bytes.decode()


def _yield_token_and_is_call(code: str) -> Iterator[tuple[tokenize.TokenInfo, bool]]:
    """Yields each token with a bool indicating whether it is a function call.
    """
    try:
        tokens = _tokenize(code)
        prev_token = None
        is_attribute_access = False
        for token in tokens:
            if (prev_token and  # If the previous token exists and
                    prev_token.type == tokenize.NAME and  # it is a Python identifier
                    token.type == tokenize.OP and  # and the current token is a delimiter
                    token.string == '('):  # and in particular it is '('.
                yield prev_token, not is_attribute_access
                is_attribute_access = False
            else:
                if prev_token:
                    is_attribute_access = (
                            prev_token.type == tokenize.OP and prev_token.string == '.'
                    )
                    yield prev_token, False
            prev_token = token
        if prev_token:
            yield prev_token, False
    except Exception as e:
        logging.warning('Failed parsing %s', code)
        raise e


def rename_function_calls(code: str, source_name: str, target_name: str) -> str:
    """Renames function calls from `source_name` to `target_name`.
    """
    if source_name not in code:
        return code
    modified_tokens = []
    for token, is_call in _yield_token_and_is_call(code):
        if is_call and token.string == source_name:
            # Replace the function name token
            modified_token = tokenize.TokenInfo(
                type=token.type,
                string=target_name,
                start=token.start,
                end=token.end,
                line=token.line
            )
            modified_tokens.append(modified_token)
        else:
            modified_tokens.append(token)
    return _untokenize(modified_tokens)


def get_functions_called(code: str) -> MutableSet[str]:
    """Returns the set of all functions called in `code`.
    """
    return set(token.string for token, is_call in
               _yield_token_and_is_call(code) if is_call)


def yield_decorated(code: str, decorator: str) -> list:
    decorated_functions = []
    function_pattern = decorator + r"\s*void (\w+)\(([^)]*)\)\s*{"

    import re
    matches = re.finditer(function_pattern, code, re.DOTALL)
    for match in matches:
        decorated_functions.append(match.group(2))

    return decorated_functions


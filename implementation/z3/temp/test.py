import sys
sys.path.append('/home/ubuntu/z3/build/python')
from z3 import *

def parse_cnf(filename):
    with open(filename, 'r') as file:
        clauses = []
        n_vars = 0
        for line in file:
            if line.startswith('c'):
                continue
            elif line.startswith('p'):
                parts = line.split()
                n_vars = int(parts[2])
            else:
                # 解析子句
                parts = line.split()
                clause = []
                for part in parts:
                    if part == '0':
                        break
                    num = int(part)
                    if num < 0:
                        clause.append(Not(Bool(f'x{-num}')))
                    else:
                        clause.append(Bool(f'x{num}'))
                clauses.append(Or(clause))
        return clauses, n_vars

def solve_cnf(filename):
    clauses, n_vars = parse_cnf(filename)
    s = Solver()
    s.add(clauses)
    if s.check() == sat:
        m = s.model()
        print("s SATISFIABLE")
        # for i in range(1, n_vars + 1):
        #     print(f"x{i} = {m.evaluate(Bool(f'x{i}'))}")
    else:
        print("s UNSATISFIABLE")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <cnf_filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    solve_cnf(filename)
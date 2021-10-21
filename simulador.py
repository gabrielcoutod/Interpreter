from enum import Enum
import argparse

class Function:
    def __init__(self, name, beg_address, end_address, parent):
        self.name = name 
        self.beg_address = beg_address # index of def ...
        self.end_address = end_address # index of end ...
        self.parent = parent # parent Function()

    def __str__(self):
        return f"Foo: {self.name} {self.beg_address} {self.end_address} {self.parent.name if self.parent else None}"

class Var:
    def __init__(self, name, value, parent):
        self.name = name
        self.value = value
        self.parent = parent

    def __str__(self):
        return f"Var: {self.name} {self.value} {self.parent.name if self.parent else None}"

class ScopeMode(Enum):
    STATIC = 0
    DYNAMIC = 1
    def __str__(self):
        return self.name

def parse_args():
    '''Retorna uma estrutura com os argumentos passados para o programa.'''
    parser = argparse.ArgumentParser(description="Arquivo")
    parser.add_argument("file", metavar="FILE", type=str, help="Arquivo com Codigo")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dynamic', "-d", action='store_true')
    group.add_argument('--static', "-s", action='store_true')
    return parser.parse_args()

stack_functions  = []
stack_vars  = []
scope_mode = -1


def read_lines(filename):
    with open(filename) as f:
        return f.readlines()
    

def interpret(function):
    function_counter = 0 # para funções de mesmo nome aninhadas
    counter = function.beg_address + 1
    initial_len_stack_vars = len(stack_vars)
    initial_len_stack_functions = len(stack_functions)
    
    for line in lines[function.beg_address + 1:function.end_address]:
        function_counter = parseLine(line, function_counter, function, counter)

        input(f"{counter}")
        for stack_function in stack_functions:
            print(stack_function, end=';')
        print()
        for stack_var in stack_vars:
            print(stack_var, end=';')
        print()

        counter += 1
        

    # Remover valores das pilhas
    for i in range(len(stack_vars) - initial_len_stack_vars):
        stack_vars.pop()
    for i in range(len(stack_functions) - initial_len_stack_functions):
        stack_functions.pop()
    


def parseLine(line, function_counter, parent_function, counter):
    line = line.strip()
    # Caso em que uma função começa
    if line.startswith('def '):
        function_counter += 1
        if function_counter == 1:
            stack_functions.append(Function(line[line.find('def') + len('def '):], counter, -1, parent_function))
    
    # Caso que uma função termina
    elif line.startswith('end '):
        function_counter -= 1
        if function_counter == 0:
            stack_functions[-1].end_address = counter

    # Casos de operações na função atual        
    elif function_counter == 0:
        if line.startswith('var '):
            temp_line = line[line.find('var') + len('var '):] # toda linha depois de var
            equal_index = temp_line.find('=')
            stack_vars.append(Var( temp_line[: equal_index].strip(), int(temp_line[equal_index + 1:]), parent_function))   
        elif line.endswith(')'): #quando for chamada de funcao foo()
            function_name = line[:line.find('(')].strip()
            function_element = get_elem(function_name, stack_functions, parent_function)
            interpret(function_element)
        elif line.find('=') != -1: # casos de atribuição, ex x = 5, depende se é dinamico ou estatico
            equal_index = line.find('=')
            name = line[: equal_index].strip()
            value = int(line[equal_index + 1:])
            elem = get_elem(name, stack_vars, parent_function)
            elem.value = value

    return function_counter

def get_elem(name, list_of_elements, parent):
    if scope_mode == ScopeMode.DYNAMIC:
        return get_elem_dynamic(name, list_of_elements)
    elif scope_mode == ScopeMode.STATIC:
        return get_elem_static(name, list_of_elements, parent)

def get_elem_dynamic(name, list_of_elements):
    for i in range(len(list_of_elements) - 1, -1, -1):
        if list_of_elements[i].name == name:
            return list_of_elements[i]
    return None

def get_elem_static(name, list_of_elements, parent):
    while parent is not None:
        # pesquisa
        for element in list_of_elements:
            if element.name == name and element.parent == parent:
                return element
        # atualizo parent_function
        parent = parent.parent
    return None


args = parse_args()
scope_mode = ScopeMode.DYNAMIC if args.dynamic else ScopeMode.STATIC
filename = args.file
lines = read_lines(filename)
global_function = Function('global',0, len(lines), None)
stack_functions.append(global_function)

interpret(global_function)
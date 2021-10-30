from enum import Enum
import argparse
from blessings import Terminal




class Node:
    """ Nodo da arvore de uma expressao matematica. """

    def __init__(self, operands, operator):
        """
        Operands é uma lista de expressões ou lista de variaveis mesmo que a expressão só tenha uma variavel (ex: x).
        As folhas da arvore serão variaveis ou constantes.
        """
        self.operands = operands
        self.operator = operator

    def get_value(self):
        # Arithmetic operators
        if self.operator == "-":
            return self.operands[0].get_value() - self.operands[1].get_value()
        elif self.operator == "*":
            return self.operands[0].get_value() * self.operands[1].get_value()
        elif self.operator == "+":
            return self.operands[0].get_value() + self.operands[1].get_value()
        if self.operator == "-u":
            return -self.operands[0].get_value()
        elif self.operator == "+u":
            return self.operands[0].get_value()
        # Boolean operators
        elif self.operator == "!":
            return not self.operands[0].get_value()
        elif self.operator == "&&":
            return self.operands[0].get_value() and self.operands[1].get_value()
        elif self.operator == "||":
            return self.operands[0].get_value() or self.operands[1].get_value()
        # Relational operators
        elif self.operator == "==":
            return self.operands[0].get_value() == self.operands[1].get_value()
        elif self.operator == "~=":
            return self.operands[0].get_value() != self.operands[1].get_value()
        elif self.operator == "<":
            return self.operands[0].get_value() < self.operands[1].get_value()
        elif self.operator == "<=":
            return self.operands[0].get_value() <= self.operands[1].get_value()
        elif self.operator == ">":
            return self.operands[0].get_value() > self.operands[1].get_value()
        elif self.operator == ">=":
            return self.operands[0].get_value() >= self.operands[1].get_value()

class Function:
    def __init__(self, name, beg_address, end_address, parent):
        self.name = name 
        self.beg_address = beg_address # index of def ...
        self.end_address = end_address # index of end ...
        self.parent = parent # parent Function()
        self.called = None

    def __str__(self):
        return f"Foo: {self.name} {self.beg_address} {self.end_address} {self.parent.name if self.parent else None} {self.called.name if self.called else None}"

class Var:
    def __init__(self, name, value, parent):
        self.name = name
        self.value = value
        self.parent = parent

    def get_value(self):
        return self.value

    def __str__(self):
        return f"Var: {self.name} {self.value} {self.parent.name if self.parent else None}"

class Const:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value



class Expression:
    """
    Cria uma arvore para representar uma expressão matematica e avalia-la
    """

    
    OPERATOR_PRECEDENCE = {
        "(":  0,
        ")":  0,
        "!":  1,
        "-u": 1,
        "+u": 1,
        "*":  2,
        "+":  3,
        "-":  3,
        "<":  4,
        "<=": 4,
        ">":  4,
        ">=": 4,
        "==": 5,
        "~=": 5,
        "&&": 6,
        "||": 6
    }

    def __init__(self, string, parent, list_of_elements):
        # string da expressão
        string = string.strip()
        self.string = string
        self.string_len = len(self.string)
        self.string_index = 0
        
        # nodo raiz
        self.node = None
        
        # variaveis da formula
        self.variables = []
        
        # pai da expressão
        self.parent = parent

        # variaveis definidas até agora
        self.list_of_elements = list_of_elements
       
        # cria e seta as variaveis da expressão
        self.create_tree()

    def create_tree(self):
        rpn = self.get_rpn()[::-1]  #inverte a lista para leitura com pop
        stack = []
        while rpn:
            value = rpn.pop()
            if Expression.is_operator(value):
                if Expression.is_unary_operator(value):
                    operands = [stack.pop()]
                else:
                    operand_2 = stack.pop()
                    operand_1 = stack.pop()
                    operands = [operand_1, operand_2]
                value = Node(operands, value)
            stack.append(value)
        self.node = stack.pop()

    def get_rpn(self):
        """Transforma a string de input em uma string RPN usando ao algoritmo Shunting Yard"""
        oper_stack = []
        out_queue = []
        token = self.read_token()
        last_token_was_operator = True
        while token:
            if token in "+-*&&||!==~=<=<>=>":
                # unary + and -
                if last_token_was_operator and token in '+-':
                    token += 'u'
                while oper_stack and Expression.greater_op(oper_stack[-1], token) and oper_stack[-1] != "(":
                    out_queue.append(oper_stack.pop())
                oper_stack.append(token)
                last_token_was_operator = True
            elif "(" == token:
                oper_stack.append("(")
                last_token_was_operator = True
            elif ")" == token:
                while oper_stack and oper_stack[-1] != "(":
                    out_queue.append(oper_stack.pop())
                if oper_stack[-1] == "(":
                    oper_stack.pop()
                last_token_was_operator = False
            elif token.isalpha():
                out_queue.append(get_elem(token, self.list_of_elements, self.parent))
                last_token_was_operator = False
            elif token.isnumeric():
                out_queue.append(Const(int(token)))
                last_token_was_operator = False
            token = self.read_token()
        out_queue.extend(oper_stack[::-1])
        return out_queue

    def read_token(self):
        token = ""
        while self.string_index < self.string_len and not Expression.is_operator_char(self.string[self.string_index]):
            token += self.string[self.string_index]
            self.string_index += 1
        token = token.strip()
        # se não consegue ler nenhum char que não é operador, tenta ler chars de operadores
        return token if token else self.read_operator()

    def read_operator(self):
        operator = ""
        # Verifica not Expression.is_operator(operator) para não ler dois operadores diferentes junto ex: -(
        while self.string_index < self.string_len and not Expression.is_operator(operator)  \
                and Expression.is_operator_char(self.string[self.string_index]):
            operator += self.string[self.string_index]
            self.string_index += 1
        return operator
    
    def get_value(self):
        return self.node.get_value()

    @staticmethod
    def is_operator_char(char):
        return char in "-+*()!&|=<>~"

    @staticmethod
    def is_unary_operator(operator):
        return operator in ["!", "+u", "-u"]

    @staticmethod
    def is_operator(string):
        return string in ["+", "-", "*", "(", ")", "&&", "||", "!", "==", "~=", "<=", ">=", "<", ">", "+u", "-u"]

    @staticmethod
    def greater_op(operator_1, operator_2):
        """Retorna True se o operador 1 te precedencia maior que o operador 2"""
        return Expression.OPERATOR_PRECEDENCE[operator_1] < Expression.OPERATOR_PRECEDENCE[operator_2] 
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
    true_ifs = 0
    false_ifs = 0
    
    for line in lines[function.beg_address + 1:function.end_address]:
        function_counter, true_ifs, false_ifs, exec_line = parseLine(line, function_counter, function, counter, true_ifs, false_ifs)

        if exec_line:
            print_info(stack_functions, stack_vars, counter, function)

        counter += 1
        

    # Remover valores das pilhas
    for i in range(len(stack_vars) - initial_len_stack_vars):
        stack_vars.pop()
    for i in range(len(stack_functions) - initial_len_stack_functions):
        stack_functions.pop()
    

def print_info(stack_functions, stack_vars, counter, function):
    global terminal_start
    while (True):
        terminal_len = term.height
        print(term.clear())
        with term.location(0, 0):
            stack = get_function_stack(stack_functions, function)
            for foo in stack[::-1]:
                vars_foo = get_function_vars(stack_vars, foo)
                print(f"STACK: {counter + 1}: {foo.name} (", end='')
                len_vars_foo = len(vars_foo)
                for var_index in range(len_vars_foo):
                    print(f"{vars_foo[var_index].name}={vars_foo[var_index].value}", end='')
                    if var_index < len_vars_foo - 1:
                        print("", end=', ')
                print(f")",end=";")
        temp_lines = [l.strip(' \n') for l in lines]
        j = 0
        for i in range(terminal_start, terminal_start + min(terminal_len - 1,len(lines))):
            with term.location(0, j + 1):
                if i == counter:
                    print(term.bold_red_on_bright_green(temp_lines[i]),end='')
                else:
                    print(temp_lines[i],end='')
            j += 1
        user_input = input()
        if user_input == 'w':
            terminal_start = 0 if terminal_start <= 1 else terminal_start - 1
        if user_input == 's':
            terminal_start =  terminal_start if terminal_start + terminal_len >= len(lines) else terminal_start + 1
        if user_input == 'p':
            break
        if user_input == 'q':
            exit()



def parseLine(line, function_counter, parent_function, counter, true_ifs, false_ifs):
    line = line.strip()
    exec_line = True
    # Caso em que uma função começa
    if line.startswith('def '):
        function_counter += 1
        if function_counter == 1:
            stack_functions.append(Function(line[line.find('def') + len('def '):], counter, -1, parent_function))
        else:
            exec_line = False
    
    # Caso que uma função termina
    elif line.startswith('end '):
        function_counter -= 1
        if function_counter == 0:
            stack_functions[-1].end_address = counter
        else:
            exec_line = False

    # Casos de operações na função atual        
    elif function_counter == 0:
        if line.startswith('if '):
            if false_ifs > 0:
                false_ifs += 1
                exec_line = False
            else:
                cond = line[line.find('if') + len('if '):] # toda linha depois de if
                if evaluate(cond, parent_function, stack_vars):
                    true_ifs += 1
                else:
                    false_ifs += 1
        elif line.startswith('endif'):
            if false_ifs > 0:
                false_ifs -= 1
                exec_line = False
            else:
                true_ifs -= 1
        elif false_ifs == 0:
            if line.startswith('var '):
                temp_line = line[line.find('var') + len('var '):] # toda linha depois de var
                equal_index = temp_line.find('=')
                stack_vars.append(Var( temp_line[: equal_index].strip(), evaluate(temp_line[equal_index + 1:], parent_function, stack_vars), parent_function))   
            elif line.find('=') != -1: # casos de atribuição, ex x = 5, depende se é dinamico ou estatico
                equal_index = line.find('=')
                name = line[: equal_index].strip()
                elem = get_elem(name, stack_vars, parent_function)
                elem.value = evaluate(line[equal_index + 1:], parent_function, stack_vars)
            elif line.endswith(')'): #quando for chamada de funcao foo()
                function_name = line[:line.find('(')].strip()
                function_element = get_elem(function_name, stack_functions, parent_function)
                function_element.called = parent_function
                interpret(function_element)
                function_element.called = None
            else:
                exec_line = False
    else:
        exec_line = False
    return function_counter, true_ifs, false_ifs, exec_line

def evaluate(line, parent, list_of_elements):
    exp = Expression(line, parent, list_of_elements)
    return exp.get_value()

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

def get_function_stack(list_of_elements, parent):
    stack = []
    while parent is not None:
        for element in list_of_elements:
            if element == parent:
                stack.append(element)
                parent = element.called
                break
    return stack

def get_function_vars(stack_vars, foo):
    vars = []
    for var in stack_vars:
        if var.parent == foo:
            vars.append(var)
    return vars


args = parse_args()
scope_mode = ScopeMode.DYNAMIC if args.dynamic else ScopeMode.STATIC
filename = args.file
lines = read_lines(filename)
global_function = Function('global',-1, len(lines), None)
stack_functions.append(global_function)
term = Terminal()
terminal_start = 0
terminal_len = term.height
with term.fullscreen():
    print_info(stack_functions, stack_vars, -1, global_function)
    interpret(global_function)
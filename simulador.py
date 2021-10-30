from enum import Enum
import argparse

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

    def __str__(self):
        return f"Foo: {self.name} {self.beg_address} {self.end_address} {self.parent.name if self.parent else None}"

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
        "*":  1,
        "+":  2,
        "-":  2,
        "<":  3,
        "<=": 3,
        ">":  3,
        ">=": 3,
        "&&": 4,
        "||": 4
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
                if value == "!":
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
        while token:
            if token in "+-*&&||!==<=<>=>":
                while oper_stack and Expression.greater_op(oper_stack[-1], token) and oper_stack[-1] != "(":
                    out_queue.append(oper_stack.pop())
                oper_stack.append(token)
            elif "(" == token:
                oper_stack.append("(")
            elif ")" == token:
                while oper_stack and oper_stack[-1] != "(":
                    out_queue.append(oper_stack.pop())
                if oper_stack[-1] == "(":
                    oper_stack.pop()
            elif token.isalpha():
                out_queue.append(get_elem(token, self.list_of_elements, self.parent))
            elif token.isnumeric():
                out_queue.append(Const(int(token)))
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
        return char in "-+*()!&|=<>"

    @staticmethod
    def is_operator(string):
        return string in ["+", "-", "*", "(", ")", "&&", "||", "!", "==", "<=", ">=", "<", ">"]

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
            stack_vars.append(Var( temp_line[: equal_index].strip(), evaluate(temp_line[equal_index + 1:], parent_function, stack_vars), parent_function))   
        elif line.find('=') != -1: # casos de atribuição, ex x = 5, depende se é dinamico ou estatico
            equal_index = line.find('=')
            name = line[: equal_index].strip()
            elem = get_elem(name, stack_vars, parent_function)
            elem.value = evaluate(line[equal_index + 1:], parent_function, stack_vars)
        elif line.endswith(')'): #quando for chamada de funcao foo()
            function_name = line[:line.find('(')].strip()
            function_element = get_elem(function_name, stack_functions, parent_function)
            interpret(function_element)

    return function_counter

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


args = parse_args()
scope_mode = ScopeMode.DYNAMIC if args.dynamic else ScopeMode.STATIC
filename = args.file
lines = read_lines(filename)
global_function = Function('global',-1, len(lines), None)
stack_functions.append(global_function)

interpret(global_function)
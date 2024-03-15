regnum = 0  # Initialize a global register number

def next_register():
    global regnum
    regnum += 1
    return regnum

def read_input(file_path):
    with open(file_path, 'r') as file:
        # Read the file, remove whitespace, and return it
        return ''.join(file.read().split())

def tokenizer(input_program):
    # This tokenizer splits tokens based on specific characters and treats each digit separately
    tokens = []
    i = 0
    while i < len(input_program):
        if input_program[i] in ['+', '-', '*', '&', '|', '=', '?', '%', ';', '!']:
            tokens.append(input_program[i])
            i += 1
        elif input_program[i].isalpha() or input_program[i].isdigit():
            tokens.append(input_program[i])
            i += 1
        else:
            # Skip any unrecognized characters (like whitespace)
            i += 1
    return tokens


def program(tokens):
    instructions = []
    while tokens:
        if tokens[-1] == '!':
            tokens.pop()  # Remove the '!' token
            instructions += stmt_list(tokens)
        else:
            raise ValueError("Program does not end with '!'")
    return instructions

def stmt_list(tokens):
    instructions = ""
    while tokens and tokens[0] != '!':
        if tokens[0].isalpha() and len(tokens) > 1 and tokens[1] == '=':
            variable_name = tokens.pop(0)
            tokens.pop(0)  # Remove '='
            assignment_code = parse_assignment(variable_name, tokens)
            instructions += assignment_code
        
        elif tokens[0] == '%':
            tokens.pop(0)  # Remove '%'
            variable = tokens.pop(0)
            print_code = f'WRITE {variable}\n'
            instructions += print_code
        
        elif tokens[0] == '?':
            tokens.pop(0)  # Remove '%'
            variable = tokens.pop(0)
            print_code = f'READ {variable}\n'
            instructions += print_code

        if tokens and tokens[0] == ';':
            tokens.pop(0)
    return instructions


def load_number(token):
    reg = next_register()
    return reg, code_gen('LOADI', f'r{reg}', f'#{token}', '')

def parse_expression(tokens):
    if not tokens:
        return "", None

    token = tokens.pop(0)
    code = ""
    operand_stack = []
    if token.isdigit():
        reg, instr = load_number(token)
        operand_stack.append(reg)
        code += instr
    elif token.isalpha():
        reg = next_register()
        operand_stack.append(reg)
        code += code_gen('LOAD', f'r{reg}', token, '')
    # Handle binary operations
    elif token in ['+', '-', '*', '&', '|']:
        code_left, reg_left = parse_expression(tokens)  # Recursively parse the left expr
        code_right, reg_right = parse_expression(tokens)  # Recursively parse the right expr
        
        if token == '|' and reg_left is not None and reg_right is not None:
            result_reg = next_register()
            code += code_left + code_right
            code += code_gen('OR', f'r{result_reg}', f'r{reg_left}', f'r{reg_right}')
            operand_stack.append(result_reg)
        
        elif token == '&' and reg_left is not None and reg_right is not None:
            result_reg = next_register()
            code += code_left + code_right
            code += code_gen('AND', f'r{result_reg}', f'r{reg_left}', f'r{reg_right}')
            operand_stack.append(result_reg)
        
        elif token == '*' and reg_left is not None and reg_right is not None:
            result_reg = next_register()
            code += code_left + code_right
            code += code_gen('MUL', f'r{result_reg}', f'r{reg_left}', f'r{reg_right}')
            operand_stack.append(result_reg)
        
        elif token == '-' and reg_left is not None and reg_right is not None:
            result_reg = next_register()
            code += code_left + code_right
            code += code_gen('SUB', f'r{result_reg}', f'r{reg_left}', f'r{reg_right}')
            operand_stack.append(result_reg)
        
        elif token == '+' and reg_left is not None and reg_right is not None:
            result_reg = next_register()
            code += code_left + code_right
            code += code_gen('ADD', f'r{result_reg}', f'r{reg_left}', f'r{reg_right}')
            operand_stack.append(result_reg)

    if operand_stack:
        return code, f'{operand_stack[-1]}'
    return code, None

def parse_assignment(variable, tokens):
    # Generate code for the expression, including loading values and operations
    expr_code, last_reg = parse_expression(tokens)
    
    # Append STORE instruction to store the result of the expression into the variable
    if last_reg:
        store_instr = code_gen('STORE', variable, f'r{last_reg}', '')
        expr_code += store_instr
    
    return expr_code


def code_gen(opcode, field1, field2, field3):
    return f"{opcode} {field1} {field2} {field3}\n"

# Assuming this is called when you run your Python compiler
if __name__ == '__main__':
    num = input("Enter comp number: ")
    
    input_program = read_input(f'tests/comp0{num}.tinyL') if int(num) <= 9 else read_input(f'tests/comp{num}.tinyL')
    print(input_program)
    tokens = tokenizer(input_program)
    print(f"tokens: {tokens}")
    
    instructions = program(tokens)
    
    # Write the instructions to the output file
    with open('my.out', 'w') as outfile:
        for instr in instructions:
            outfile.write(instr)

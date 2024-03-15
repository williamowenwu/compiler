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
    if token.isdigit():
        # If it's a digit, load it directly into a register and return the code
        reg, instr = load_number(token)
        return instr, str(reg)
    elif token.isalpha():
        reg = next_register()
        return code_gen('LOAD', f'r{reg}', token, ''), str(reg)
    elif token in ['+', '-', '*', '&', '|']:
        code_left, result_left = parse_expression(tokens)
        code_right, result_right = parse_expression(tokens)

        # Check if both operands are digits for constant propagation
        if result_left.isdigit() and result_right.isdigit():
            computed_result = evaluate_operation(token, int(result_left), int(result_right))
            result_reg = next_register()
            # Generate the operation code but use the computed result
            op_code = get_opcode_for_token(token)
            # Consider adding a comment or a simplified instruction that indicates the optimization
            optimized_instr = code_gen(op_code, f'r{result_reg}', result_left, result_right) + f" r{result_reg} #{computed_result}\n"
            return optimized_instr, str(computed_result)
        else:
            result_reg = next_register()
            op_code = get_opcode_for_token(token)
            # Normal code generation for operations involving at least one non-constant operand
            code += code_left + code_right + code_gen(op_code, f'r{result_reg}', f'r{result_left}', f'r{result_right}')
            return code, str(result_reg)

    return code, None

def evaluate_operation(op, left, right):
    if op == '+':
        return left + right
    elif op == '-':
        return left - right
    elif op == '*':
        return left * right
    elif op == '&':
        return left & right
    elif op == '|':
        return left | right
    else:
        raise ValueError(f"Unsupported operation: {op}")

def get_opcode_for_token(token):
    return {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '&': 'AND',
        '|': 'OR'
    }.get(token, None)

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

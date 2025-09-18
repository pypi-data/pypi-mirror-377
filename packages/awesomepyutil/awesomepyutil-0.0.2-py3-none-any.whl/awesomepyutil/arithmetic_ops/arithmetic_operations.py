def func_divide(num1, num2):
    output = num1 / num2
    return output

def func_divide_remainder(dividend, divisor):
    quotient = dividend / divisor
    remainder = dividend % divisor
    return quotient, remainder

def func_multiply(num1, num2):
    output = num1 * num2
    return output

def func_subtract(num1, num2):
    output = num1 - num2
    return output

def func_add(num1, num2):
    output = num1 + num2
    return output


if __name__ == "__main__":
    out = func_divide(5,2)
    print(f"output: {out}")
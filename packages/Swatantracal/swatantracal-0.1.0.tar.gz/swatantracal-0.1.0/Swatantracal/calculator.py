def add(a,b):
    """this will return the sum of two numbers"""
    return a+b

def subtract(a,b):
    """this will return the difference of two numbers"""
    return a-b

def multiply(a,b):
    """this will return the product of two numbers"""
    return a*b     
 
def divide(a,b):
    """this will return the quotient of two numbers"""
    if b==0:
        raise ValueError("Cannot divide by zero")
    return a/b

def power(a,b):
    """this will return the a raised to the power of b"""
    return a**b
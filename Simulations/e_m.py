import sympy as sp

# Define your symbols
x, y = sp.symbols('x y')

# Create a symbolic expression
expr = x**2 + y**2

# Get user input for the values of x and y
x_value = float(input("Enter a value for x: "))
y_value = float(input("Enter a value for y: "))

# Substitute the values into the expression
result = expr.subs({x: x_value, y: y_value})

# Print the result
print(f"The result of the expression {expr} with x={x_value} and y={y_value} is: {result}")

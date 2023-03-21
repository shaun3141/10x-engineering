operation = input('Enter the operation you would like to perform (sum, product, or custom): ')
if operation == 'custom':
    expression = input('Enter a mathematical expression using x to represent each number in the list: ')
    numbers = input('Enter a comma-separated list of numbers: ').split(',')
    numbers = [float(num.strip()) for num in numbers]
    result = calculate(numbers, expression)
else:
    numbers = input('Enter a comma-separated list of numbers: ').split(',')
    numbers = [float(num.strip()) for num in numbers]
    result = calculate(numbers, operation)
print(result)

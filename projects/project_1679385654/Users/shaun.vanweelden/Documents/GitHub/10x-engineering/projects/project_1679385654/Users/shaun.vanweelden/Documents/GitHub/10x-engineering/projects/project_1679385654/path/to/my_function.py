def my_function(numbers, reverse=False):
    if reverse:
        numbers.reverse()
    return numbers[::-1] if not reverse else numbers
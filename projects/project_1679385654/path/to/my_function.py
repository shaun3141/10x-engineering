#sorting function for list of numbers
def sort_numbers(numbers, order='ascending'):
    sorted_numbers = sorted(numbers)
    if order == 'descending':
        sorted_numbers.reverse()
    return sorted_numbers


def my_function(numbers, reverse=False):
    sorted_numbers = sort_numbers(numbers, order='descending') if reverse else sort_numbers(numbers)
    return {
        'sorted_numbers': sorted_numbers,
        'sum': sum(sorted_numbers),
        'min': min(sorted_numbers),
        'max': max(sorted_numbers),
        'average': sum(sorted_numbers) / len(sorted_numbers)
    }

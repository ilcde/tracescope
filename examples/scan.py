numbers = [4, 8, 2, 6, 1]
total = 0

def accumulate(items):
    running = 0
    for index, value in enumerate(items):
        running += value
    return running

total = accumulate(numbers)
print("Total:", total)

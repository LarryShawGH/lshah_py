
''' for i in range(3):
    for j in range (3):
        print("#", end = '')

    print()

print ('%' * 4) '''

scores = []

for i in range (3):
    value = input('Value:')
    scores.append(int (value))

print(scores)
average = sum(scores) / len(scores)

print(f'Average: {average}')


people= {
    'Lalit': '222000',
    'BJ' : '333111',
    'PLS' : '444333'
}

name = input('Name: ')

if name in people:
    print(f'Number: {people[name]}')
else:
    print('not found')

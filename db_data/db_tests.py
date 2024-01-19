with open('test_excursions.txt', encoding='utf8') as file:
    excursions, windows = file.read().split('-#-')
    excursions = [list(filter(lambda x: len(x), exc.split('\n'))) for exc in excursions.split('@')]
    excursions = [list(map(lambda x: x.split(': ')[1], exc)) for exc in excursions]
    print(excursions)
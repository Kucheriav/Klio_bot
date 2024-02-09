# from db_models_new import excursions, schedule
# from sqlalchemy import insert, select
# from datetime import datetime
# from db_models_new import database_init, recreate_db
#
# #########TEST FUNCTIONS##############
# def add_test_data(connection):
#     with open('test_data.txt', encoding='utf8') as file:
#         new_excursions, open_visits = file.read().split('-#-')
#         new_excursions = [list(filter(lambda x: len(x), exc.split('\n'))) for exc in new_excursions.split('@')]
#         new_excursions = [list(map(lambda x: x.split(': ')[1], exc)) for exc in new_excursions]
#         open_visits = list(map(lambda x: x.split(), open_visits.split('-')))
#
#     for excursion in new_excursions:
#         query = insert(excursions).values(title=excursion[0],
#                                            description=excursion[2],
#                                            duration=excursion[1].split()[0]
#                                            ).prefix_with('IGNORE')
#         connection.execute(query)
#     for visit in open_visits:
#
#         query = insert(schedule).values(excursion_id=int(visit[0]),
#                                          date_time=datetime.strptime(visit[1], '%d.%m.%Y')).prefix_with('IGNORE')
#         connection.execute(query)

#
# engine, connection = recreate_db()
# add_test_data(connection)
# res = connection.execute(select(excursions))
# for el in res:
#     print(el)
# print()
# res = connection.execute(select(schedule))
# for el in res:
#     print(el)


from db_functions import database_init, get_all_windows, recreate_db, add_test_data_classes


session, engine = database_init()
# add_test_data_classes(session)
res = get_all_windows(session)
for el in res:
    print(el)
print()
import datetime

# with open('test_visits.txt', encoding='utf8') as file:
#     visits = list(map(lambda x: x.split(), file.read().split('-')))
#     for visit in visits:
#         d = datetime.datetime.strptime(visit[1], '%d.%m.%y')
#         print(d)


d = datetime.datetime.strptime(visit[1], '%d.%m.%y')
print(d)
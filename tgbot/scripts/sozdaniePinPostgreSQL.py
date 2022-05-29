import psycopg2
from psycopg2 import Error
import random


def sample_floats(low, high, k=1):
    """ Return a k-length list of unique random floats
        in the range of low <= x <= high
    """
    result = []
    seen = set()
    for i in range(k):
        x = random.uniform(low, high)
        while x in seen:
            x = random.uniform(low, high)
        seen.add(x)
        result.append(int(x))
    return result

    # Подключение к существующей базе данных


connection = psycopg2.connect(user="rxwovlanfxcamy",
                              # пароль, который указали при установке PostgreSQL
                              password="4efbade4f7c963d4f80b5be890df517cc49a96c21d6bcedd55edf7696fbc8249",
                              host="ec2-99-80-170-190.eu-west-1.compute.amazonaws.com",
                              port="5432",
                              database="dd16b87iprrbga")

list_username = ['Калин Данил', 'Верясов Данил', 'Сираев Вадим','Филиипов Саня','Манзуров Илья','Шереметьев Макар','Казеев Иван','Кулагин Григорий']
list_groupp = ['АДБ-19-06', 'АДБ-19-06', 'АДБ-19-07','АДБ-19-07', 'АДБ-19-06', 'АДБ-19-06', 'АДБ-19-06', 'АДБ-19-06']
list_pin = sample_floats(10000, 99999,len(list_username))
# Курсор для выполнения операций с базой данных
cursor = connection.cursor()
# Выполнение SQL-запроса для вставки данных в таблицу
for i, j, k in zip(list_username,list_groupp,list_pin):
    insert_query = f""" INSERT INTO users (username, groupp, pin) VALUES ('{str(i)}','{str(j)}','{str(k)}')"""
    cursor.execute(insert_query)
    connection.commit()
cursor.close()
connection.close()
print("Соединение с PostgreSQL закрыто")

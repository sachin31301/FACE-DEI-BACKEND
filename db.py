import psycopg2
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'sachindb'
DATABASE_HOST = "127.0.0.1"
DATABASE_PORT = '5432'
DATABASE_NAME = 'postgres'

def DATABASE_CONNECTION():
    return psycopg2.connect(user=DATABASE_USER,
                              password=DATABASE_PASSWORD,
                              host=DATABASE_HOST,
                              port=DATABASE_PORT,
                              database=DATABASE_NAME)

try:
    connection = DATABASE_CONNECTION()
    cursor = connection.cursor()
    print('succesful')
except:
    print('mar gya')
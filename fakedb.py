import psycopg2
from datetime import datetime
from random import randrange
from datetime import timedelta
import random

DATABASE_USER = 'xgkeclnubywrls'
DATABASE_PASSWORD = '619e2f4c00ce4762653d849126a789a1ee3377c18002c5dd6ec7d5ef2ade8ade'
DATABASE_HOST = "ec2-107-20-24-247.compute-1.amazonaws.com"
DATABASE_PORT = '5432'
DATABASE_NAME = 'dbrbsi2m64e7nu'

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def DATABASE_CONNECTION():
    return psycopg2.connect(user=DATABASE_USER,
                              password=DATABASE_PASSWORD,
                              host=DATABASE_HOST,
                              port=DATABASE_PORT,
                              database=DATABASE_NAME)


d1 = datetime.strptime('9/5/2021 8:30 AM', '%m/%d/%Y %I:%M %p')
d2 = datetime.strptime('9/15/2021 9:50 PM', '%m/%d/%Y %I:%M %p')
list=['sachin','deepshika','ojasvi','kuldeep','lokesh', 'mehar','neelu','gunjan']
#list=['gunjan']
try:
    connection = DATABASE_CONNECTION()
    cursor = connection.cursor()
    thisdict = {
        8: "programming",
        9: "algorithms",
        10: "mechanics",
        11:"electronics",
        12:"mathematics",
        13:"electromagnetics",
        14:"architecture",
        15:"systems",
        17:"production",
        18:"Chemistry",
        16:"thermodynamics",
        20:"compiler",
        21:"english",
        22:"Devops"
        }
    for x in range(200):
        predname = random.choice(list)
        datec=str(random_date(d1, d2).date())
        time=random_date(d1, d2).time()
        timec=str(time)
        #print(predname)
        #print(datec)
        #print(timec)
        subject=thisdict.get(int(time.hour), "Lunch break")
        user_information_sql_query = f"INSERT INTO schema (name, date, arrival_time,subject) VALUES ('"+predname+"', '"+datec+"', '"+timec+"','"+subject+"')"
        cursor.execute(user_information_sql_query)
    connection.commit()
    cursor.close()
    print('succesful')
except (Exception, psycopg2.DatabaseError) as error:
    print('mar gya',error)
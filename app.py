# * ---------- IMPORTS --------- *
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
from flask_cors.core import try_match
import psycopg2
import cv2
import numpy as np
import re
from PIL import Image
import time
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import os, time, uuid

projectid = "75f5bd51-949f-4616-8376-4a82a51b162a"
publish_iteration_name = "Iteration3"
ENDPOINT = "https://deiface.cognitiveservices.azure.com/"
prediction_key = "7bb53499bc494fa09b32fb0c79188d49"


# Get the relativ path to this file (we will use it later)
FILE_PATH = os.path.dirname(os.path.realpath(__file__))

# * ---------- Create App --------- *
app = Flask(__name__)
CORS(app, support_credentials=True)



# * ---------- DATABASE CONFIG --------- *
DATABASE_USER = 'xgkeclnubywrls'
DATABASE_PASSWORD = '619e2f4c00ce4762653d849126a789a1ee3377c18002c5dd6ec7d5ef2ade8ade'
DATABASE_HOST = "ec2-107-20-24-247.compute-1.amazonaws.com"
DATABASE_PORT = '5432'
DATABASE_NAME = 'dbrbsi2m64e7nu'


def DATABASE_CONNECTION():
    return psycopg2.connect(user=DATABASE_USER,
                              password=DATABASE_PASSWORD,
                              host=DATABASE_HOST,
                              port=DATABASE_PORT,
                              database=DATABASE_NAME)



# * --------------------  ROUTES ------------------- *
# * ---------- Get data from the face recognition ---------- *
@app.route('/receive_data', methods=['POST'])
def get_receive_data():
    if request.method == 'POST':
        json_data = request.get_json()

        # Check if the user is already in the DB
        try:
            # Connect to the DB
            connection = DATABASE_CONNECTION()
            cursor = connection.cursor()

            # Query to check if the user as been saw by the camera today
            user_saw_today_sql_query =\
                f"SELECT * FROM users WHERE date = '{json_data['date']}' AND name = '{json_data['name']}'"

            cursor.execute(user_saw_today_sql_query)
            result = cursor.fetchall()
            connection.commit()

            # If use is already in the DB for today:
            if result:
               print('user IN')
               image_path = f"{FILE_PATH}/assets/img/{json_data['date']}/{json_data['name']}/departure.jpg"

                # Save image
               os.makedirs(f"{FILE_PATH}/assets/img/{json_data['date']}/{json_data['name']}", exist_ok=True)
               cv2.imwrite(image_path, np.array(json_data['picture_array']))
               json_data['picture_path'] = image_path

                # Update user in the DB
               update_user_querry = f"UPDATE users SET departure_time = '{json_data['hour']}', departure_picture = '{json_data['picture_path']}' WHERE name = '{json_data['name']}' AND date = '{json_data['date']}'"
               cursor.execute(update_user_querry)

            else:
                print("user OUT")
                # Save image
                image_path = f"{FILE_PATH}/assets/img/history/{json_data['date']}/{json_data['name']}/arrival.jpg"
                os.makedirs(f"{FILE_PATH}/assets/img/history/{json_data['date']}/{json_data['name']}", exist_ok=True)
                cv2.imwrite(image_path, np.array(json_data['picture_array']))
                json_data['picture_path'] = np.array(json_data['picture_array'])

                # Create a new row for the user today:
                insert_user_querry = f"INSERT INTO schema (name, date, arrival_time, arrival_picture) VALUES ('{json_data['name']}', '{json_data['date']}', '{json_data['hour']}', '{json_data['picture_path']}')"
                cursor.execute(insert_user_querry)

        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR DB: ", error)
        finally:
            connection.commit()

            # closing database connection.
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

        # Return user's data to the front
        return jsonify(json_data)


# * ---------- Get all the data of an employee ---------- *
@app.route('/get_employee', methods=['GET'])
def get_employee():
    name = request.args.get('name')
    date = request.args.get('date')
    answer_to_send = {}
    # Check if the user is already in the DB
    try:
        # Connect to DB
        connection = DATABASE_CONNECTION()
        cursor = connection.cursor()
        # Query the DB to get all the data of a user:
        datec=f'{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}'
        user_information_sql_query = f"SELECT DISTINCT ON (subject) subject,arrival_time FROM schema WHERE name = '{name}' AND date='{date}'   "

        cursor.execute(user_information_sql_query)
        result = cursor.fetchall()
        connection.commit()

        # if the user exist in the db:
        if result:
            print('RESULT: ',result)
            # Structure the data and put the dates in string for the front
            for k,v in enumerate(result):
                answer_to_send[k] = {}
                for ko,vo in enumerate(result[k]):
                    answer_to_send[k][ko] = str(vo)
            print('answer_to_send: ', answer_to_send)
        else:
            answer_to_send = {'error': 'User not found...'}

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        # closing database connection:
        if (connection):
            cursor.close()
            connection.close()

    # Return the user's data to the front
    return jsonify(answer_to_send)

@app.route('/get_subject', methods=['GET'])
def get_subject():
    subj = request.args.get('subj')
    date = request.args.get('date')
    subanswer_to_send = {}
    # Check if the user is already in the DB
    try:
        # Connect to DB
        connection = DATABASE_CONNECTION()
        cursor = connection.cursor()
        # Query the DB to get all the data of a user:
        datec=f'{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}'
        user_information_sql_query = f"SELECT DISTINCT ON (name) name,arrival_time FROM schema WHERE subject = '{subj}'  AND date='{date}'    "

        cursor.execute(user_information_sql_query)
        subresult = cursor.fetchall()
        connection.commit()

        # if the user exist in the db:
        if subresult:
            print('RESULT: ',subresult)
            # Structure the data and put the dates in string for the front
            for k,v in enumerate(subresult):
                subanswer_to_send[k] = {}
                for ko,vo in enumerate(subresult[k]):
                    subanswer_to_send[k][ko] = str(vo)
            print('answer_to_send: ', subanswer_to_send)
        else:
            subanswer_to_send = {'error': 'User not found...'}

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        # closing database connection:
        if (connection):
            cursor.close()
            connection.close()

    # Return the user's data to the front
    return jsonify(subanswer_to_send)

# * --------- Get the 5 last users seen by the camera --------- *
@app.route('/get_5_last_entries', methods=['GET'])
def get_5_last_entries():
    answer_to_send = {}
    # Check if the user is already in the DB
    try:
        # Connect to DB
        connection = DATABASE_CONNECTION()

        cursor = connection.cursor()
        # Query the DB to get all the data of a user:
        lasts_entries_sql_query = f"SELECT * FROM schema ORDER BY id DESC LIMIT 2  ;"

        cursor.execute(lasts_entries_sql_query)
        result = cursor.fetchall()
        connection.commit()

        # if DB is not empty:
        if result:
            # Structure the data and put the dates in string for the front
            for k, v in enumerate(result):
                answer_to_send[k] = {}
                for ko, vo in enumerate(result[k]):
                    answer_to_send[k][ko] = str(vo)
        else:
            answer_to_send = {'error': 'error detect'}

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        # closing database connection:
        if (connection):
            cursor.close()
            connection.close()

    # Return the user's data to the front
    return jsonify(answer_to_send)


# * ---------- Add new employee ---------- *
@app.route('/add_employee', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_employee():
    try:
        # Get the picture from the request
        print('stated')
        image_file = request.files['image']
        #cv2.imshow(image_file)
        print(request.form['nameOfEmployee'])
        myname=request.form['nameOfEmployee']

        # Store it in the folder of the know faces:
        file_path = os.path.join(f'assets/img/users/{myname}.jpg')
        image_file.save(file_path)
        print('end')
        answer = 'new employee succesfully added'
    except:
        answer = 'Error while adding new employee. Please try later...'
    return jsonify(answer)


# * ---------- Get employee list ---------- *
@app.route('/get_employee_list', methods=['GET'])
def get_employee_list():
    employee_list = {}

    # Walk in the user folder to get the user list
    walk_count = 0
    for file_name in os.listdir(f"{FILE_PATH}/assets/img/users/"):
        # Capture the employee's name with the file's name
        name = re.findall("(.*)\.jpg", file_name)
        if name:
            employee_list[walk_count] = name[0]
        walk_count += 1

    return jsonify(employee_list)


# * ---------- Delete employee ---------- *
@app.route('/delete_employee/<string:name>', methods=['GET'])
def delete_employee(name):
    try:
        # Remove the picture of the employee from the user's folder:
        print('name: ', name)
        file_path = os.path.join(f'assets/img/users/{name}.jpg')
        os.remove(file_path)
        answer = 'Employee succesfully removed'
    except:
        answer = 'Error while deleting new employee. Please try later'

    return jsonify(answer)

@app.route('/imageshow', methods=['POST'])
def imageshow():
    try:
        file = request.files['picture']
        #print(file)
        print('start')
        #npimg = np.frombuffer(file, np.uint8)
       # img = cv2.imdecode(npimg,cv2.IMREAD_COLOR)
        #img = Image.fromarray(img.astype("uint8"))
        #cv2.imshow(img)
        connection = DATABASE_CONNECTION()
        cursor = connection.cursor()
        #cursor.execute(f"ALTER TABLE schema ADD COLUMN id SERIAL PRIMARY KEY")
        file_path = os.path.join(f"assets/img/users/res.jpg")
        file.save(file_path)
        print('hogya')
        answer="jihana"
        connection = DATABASE_CONNECTION()
        cursor = connection.cursor()
        print('condb')
        os.environ['TZ'] = 'Asia/Kolkata'
        time.tzset()
        mytime=time.localtime().tm_hour
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
        subject=thisdict.get(mytime, "Lunch break")
        print(subject)
        datec=f'{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}'
        timec=f'{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}'
        prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
        predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)
        with open(os.path.join(f"assets/img/users/res.jpg"), "rb") as image_contents:
            results = predictor.classify_image(
            projectid, publish_iteration_name, image_contents.read())
            predname=results.predictions[0].tag_name

        insert_user_querry = f"INSERT INTO schema (name, date, arrival_time,subject) VALUES ('"+predname+"', '"+datec+"', '"+timec+"','"+subject+"')"
        cursor.execute(insert_user_querry)
    except (Exception, psycopg2.DatabaseError) as error:
        answer="rihana"
        print("ERROR DB: ", error)
    finally:
            connection.commit()

            # closing database connection.
            if connection:
                cursor.close()
                #connection.close()
                print("PostgreSQL connection is closed")

    return jsonify(answer)

@app.route("/")
def hello_world():
    try:
        connection = DATABASE_CONNECTION()
        cursor = connection.cursor()
        #cursor.execute(f"ALTER TABLE schema ADD COLUMN id SERIAL PRIMARY KEY")
        print('succesful')
        #cursor.execute(f"ALTER TABLE users ADD COLUMN subject TEXT  ")
        create_table_query = '''CREATE TABLE schema
          (name           TEXT     NOT NULL,
          date         date NOT NULL,
          arrival_time TIME NOT NULL,
          subject TEXT NOT NULL ); '''
    # Execute a command: this creates a new table
        cursor.execute(create_table_query)
        cursor.execute(f"ALTER TABLE schema ADD COLUMN id SERIAL PRIMARY KEY")
        #cursor.execute(f"ALTER TABLE users ADD COLUMN subject TEXT ")
        print("hogya")
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
            connection.commit()

            # closing database connection.
            if connection:
                cursor.close()
                #connection.close()
                print("PostgreSQL connection is closed first")
    
    return "Hello world!"

                                 
# * -------------------- RUN SERVER -------------------- *
if __name__ == '__main__':
    # * --- DEBUG MODE: --- *
    app.run(host='127.0.0.1', port=5000, debug=True)
    #  * --- DOCKER PRODUCTION MODE: --- *
    # app.run(host='0.0.0.0', port=os.environ['PORT']) -> DOCKER

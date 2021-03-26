from flask import Flask, jsonify, request, make_response
import psycopg2
from psycopg2 import OperationalError, errorcodes, errors
from psycopg2.extensions import AsIs
import json
import sys
import datetime
import collections
from hashIt import hashIt
from sessionId import createRandomId
search_path = "SET SEARCH_PATH TO travelly;"
app = Flask(__name__)

def error_handler(err):
    errors = {
        'error': ''
    }
    # if (err.pgcode == '23505'):
    #     duplicate = 'User ID' if 'userid' in err.pgerror else 'Email' if 'email' in err.pgerror else 'Username' if 'username' in err.pgerror else 'Salt' if 'salt' in err.pgerror else ''
    #     errors['error'] = duplicate + ' already exists'

    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print ("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    print ("\nextensions.Diagnostics:", err.diag)

    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")
    
    # return errors

def getcon():
    connStr = "host='localhost' user='postgres' dbname='Travelly' password=password"
    conn=psycopg2.connect(connStr) 
    return conn

def check_if_record_exists(table, column, string):
    try:
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute("""SELECT %s FROM %s WHERE %s = %s;""", [AsIs(column), AsIs(table), AsIs(column), string])
        return cur.fetchone() is not None
    except Exception as e:
        print(e)

def insert_sessionID(sessionID, column, username):
    expire = datetime.datetime.now() + datetime.timedelta(hours=2)
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("""INSERT INTO %s VALUES(%s,%s,%s);""", [AsIs(column), sessionID,  username, str(expire)])
    conn.close()

def get_salt_from_db(username):
    try:
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute("SELECT salt FROM tr_users WHERE username = %s;", [username])
        return cur.fetchone()[0]
    except Exception as e:
        error_handler(e)

    

def get_password_from_db(username):
    try:
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute("SELECT password FROM tr_users WHERE username = %s", [username])
        password = cur.fetchone()
        return password
    except Exception as e:
        print(e)


@app.route('/api/signup', methods=['POST'])
def signup():
    
    data = {
        "username": request.json['username'],
        "firstname": request.json['firstname'],
        "lastname": request.json['lastname'],
        "email": request.json['email'],
        "dob": request.json['dob'],
        "password": request.json['password'],
    }
    expire = datetime.datetime.now() + datetime.timedelta(hours=2)
    salt = createRandomId()
    sessionID = createRandomId()
    secure_password = hashIt(data['password'] + salt)
    try:
        if(check_if_record_exists('tr_users', 'username', data['username']) == False):
            conn = getcon()
            cur = conn.cursor()
            cur.execute(search_path)
            cur.execute("""INSERT INTO tr_users VALUES (%s,%s,%s,%s,%s,%s,%s);""", [data['username'], data['firstname'], data['lastname'], data['email'], data['dob'], secure_password, salt]) 
            cur.execute("""INSERT INTO %s VALUES(%s,%s,%s);""", [AsIs('tr_session'), sessionID, data['username'], str(expire)])
            conn.commit()
            resp = jsonify(status='successful')
            resp.set_cookie('sessionID', sessionID)
            return resp, 200
        else:
            return jsonify(status='user already exists')
    except psycopg2.IntegrityError as e:
        err_resp = error_handler(e)
        return jsonify(status = 'unsuccessful', error=err_resp), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = {
        "username": request.json['username'],
        "password": request.json['password']
    }
    expire = datetime.datetime.now() + datetime.timedelta(hours=2)
    try:
        if(check_if_record_exists('tr_users', 'username', data['username'])):
            user_input_password = hashIt(data['password'] + get_salt_from_db(data['username']))
            user_stored_password = get_password_from_db(data['username'])[0]
            if (str(user_input_password) == str(user_stored_password)):
                sessionID = createRandomId()
                conn = getcon()
                cur = conn.cursor()
                cur.execute(search_path)
                cur.execute("""DELETE FROM %s WHERE username = %s""",[AsIs('tr_session'), data['username']])
                cur.execute("""INSERT INTO %s VALUES(%s,%s,%s);""", [AsIs('tr_session'), sessionID, data['username'], str(expire)])
                resp = jsonify(status='success')
                resp.set_cookie('sessionID', sessionID)
                return resp, 200
            else:
                return jsonify(status='Incorrect password')
        else:
            return jsonify(status='Record does not exist')
        
        return jsonify(status='unsuccessful')
    except Exception as e:
        print(e)
        return jsonify(status='fail')


if __name__ == '__main__':
    app.run(host='localhost', port = 7000, debug = True)
from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import OperationalError, errorcodes, errors
import json
import collections
from sessionId import createRandomId
app = Flask(__name__)

def getcon():
    connStr = "host='localhost' user='postgres' dbname='Travelly' password=password"
    conn=psycopg2.connect(connStr) 
    return conn

def error_handler(err):
    errors = {
        'error': ''
    }
    if (err.pgcode == '23505'):
        duplicate = 'User ID' if 'userid' in err.pgerror else 'Email' if 'email' in err.pgerror else 'Username' if 'username' in err.pgerror else 'Salt' if 'salt' in err.pgerror else ''
        errors['error'] = duplicate + ' already exists'
    
    return errors


@app.route('/api/signup', methods=['POST'])
def signup():
    print(createRandomId())
    data = {
        "username": request.json['username'],
        "firstname": request.json['firstname'],
        "lastname": request.json['lastname'],
        "email": request.json['email'],
        "dob": request.json['dob'],
        "password": request.json['password'],
    }
    try:
        conn = getcon()
        cur = conn.cursor()
        cur.execute("SET SEARCH_PATH TO travelly;")
        cur.execute("""INSERT INTO tr_users VALUES (%s,%s,%s,%s,%s,%s);""", [data['username'], data['firstname'], data['lastname'], data['email'], data['dob'], data['password']]) 
        conn.commit()
        return jsonify(status='successful')
    except psycopg2.IntegrityError as e:
        err_resp = error_handler(e)
        return jsonify(status = 'unsuccessful', error=err_resp)


if __name__ == '__main__':
    app.run(host='localhost', port = 7000, debug = True)
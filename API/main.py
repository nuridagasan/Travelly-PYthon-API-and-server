from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import OperationalError, errorcodes, errors
import json
import collections
app = Flask(__name__)

def getcon():
    connStr = "host='localhost' user='postgres' dbname='Travelly' password=password"
    conn=psycopg2.connect(connStr) 
    return conn

def get_column_names_from_table(table):
    conn = getcon()
    cur = conn.cursor()
    cur.execute("SET SEARCH_PATH to Travelly")
    cur.execute(f"select * from {table}")
    colnames = [desc[0] for desc in cur.description]
    return colnames

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
    conn = getcon()
    cur = conn.cursor()
    data = request.json
    col_names = get_column_names_from_table('tr_users')
    data_keys = list(data.keys())
    data_values = list(data.values())
    if (collections.Counter(col_names) == collections.Counter(data_keys)):
        try:
            conn = getcon()
            cur = conn.cursor()
            cur.execute("SET SEARCH_PATH TO travelly;")
            cur.execute('''INSERT INTO tr_users VALUES (''' + ','.join(['%s' for val in data_values]) + ''');''', data_values)
            conn.commit()
            return jsonify(status='successful')
        except psycopg2.IntegrityError as e:
            err_resp = error_handler(e)
            return jsonify(status = 'unsuccessful', error=err_resp)
    else:
        missing_values = (set(col_names).difference(data_keys))
        return jsonify(status='unsuccessful', missingFormValues=list(missing_values))

    
if __name__ == '__main__':
    app.run(host='localhost', port = 7000, debug = True)
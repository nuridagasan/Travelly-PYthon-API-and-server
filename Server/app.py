from flask import Flask, jsonify, request, url_for, redirect, session, render_template, make_response, redirect, render_template
import re
import random
from psycopg2.extensions import AsIs
import psycopg2
import sys
import json
import datetime
import collections

app = Flask(__name__)
app.config['DEBUG'] = True
search_path = "SET SEARCH_PATH TO travelly;"
app.config['SECRET_KEY'] = 'Thisisasecret!'


def getcon():
    connStr = "host='localhost' user='postgres' dbname='Travelly' password=password"
    conn=psycopg2.connect(connStr) 
    return conn

def error_handler(err):
    errors = {
        'error': ''
    }
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

#def check_if_record_exists(table, column, string):
    #try:
     #   conn = getcon()
     #   cur = conn.cursor()
      #  cur.execute(search_path)
       # cur.execute("""SELECT %s FROM %s WHERE %s = %s;""", [AsIs(column), AsIs(table), AsIs(column), string])
        #return cur.fetchone() is not None
    #except Exception as e:
     #   print(e)

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
        cur.execute("SELECT coalesce(min(salt),'1') FROM tr_users WHERE username = %s;", [username]) #using min here means 1 row will be sent back even if there is no salt (then it will send back a row saying null)
        return cur.fetchone()[0]                                                                     # this keeps the time exactly the same whether there is salt or not. Coalesce stops it from returning NULL for line 94.  
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

@app.route('/')
def home():
    return 'hello'

@app.route('/login')
def get_login():   
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def post_login():
    data = {
            'username' : request.form['username'].lower(),
            'password' : request.form['password']
    }
    expire = datetime.datetime.now() + datetime.timedelta(hours=2)
    try:
       sql= "SELECT count(*) from tr_users WHERE username =%s and password= %s"  #The count sends back 0 or 1 as a result, depending on whether the pw and username are correct 
        user_input_password = pw_hash_salt(data['password'], int(get_salt_from_db(data['username'])))
        query_data = (data['username'], str(user_input_password))
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute(sql, query_data)
        check_account = cur.fetchone()[0]
        # if there is a result, the pw and username were correct 
        if check_account != 0:
            sessionID = createRandomId()
            conn = getcon()
            cur = conn.cursor()
            cur.execute(search_path)
            cur.execute("""DELETE FROM %s WHERE username = %s""",[AsIs('tr_session'), data['username']])
            cur.execute("""INSERT INTO %s VALUES(%s,%s,%s);""", [AsIs('tr_session'), sessionID, data['username'], str(expire)])
            resp = make_response(redirect('/'))
            resp.set_cookie('sessionID', sessionID)
            return resp
        else:
            return render_template('login.html', check_input = 'Incorrect username or password')
    except Exception as e:
        print(e)
        return render_template('login.html', check_input = 'Something happened BAD!')

@app.route('/signup', methods = ['GET','POST'])
def signup_form():    
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        user_sign_up = {
            'firstname' :  request.form['name'].lower(),
            'lastname' : request.form['surname'].lower(),
            'username' : request.form['username'].lower(),
            'email' : request.form['email'].lower(),
            'dob' : request.form['birthdate'],
            'password' : request.form['password'],
            'salt' : pw_salt()
        }
    #first check user inputs are valid firstname, lastname, username, email and password
    check_input = input_validation(user_sign_up)
    if check_input == True:
        #hash and salt password before sending it to database
        user_sign_up['password'] = pw_hash_salt(user_sign_up['password'],user_sign_up['salt'])
        #insert user details to database. It returns a message whether the user is successfully
        #inserted or not
        return render_template('signup.html', check_input = insert_user(user_sign_up))
    else:
        #Give error message to user
        return render_template('signup.html', check_input = check_input)

def insert_user(data):
    try:
        conn = getcon()
        cur = conn.cursor()
        sql = """SET SEARCH_PATH TO travelly;
                    INSERT INTO tr_users (username, firstname,lastname, email, dob, password, salt) VALUES (%s,%s,%s,%s,%s,%s,%s);"""
        data = (data['username'], data['firstname'], data['lastname'], data['email'], data['dob'], data['password'], data['salt'])
        cur.execute(sql,data)
        conn.commit()
        return 'Your account is successfully created!'
    except psycopg2.IntegrityError as e:
        #err_resp = error_handler(e)
        return 'Username or email already exists! Please, try again.'

def input_validation(user_sign_up):
    if not bool(re.fullmatch('[A-Za-z]{2,25}( [A-Za-z]{2,25})?', user_sign_up['firstname'])):
        return "Your name is invalid. Please, type it again."
    elif not bool(re.fullmatch('[A-Za-z]{2,25}( [A-Za-z]{2,25})?', user_sign_up['lastname'])):
        return "Your surname is invalid. Please, type it again."
    elif not bool(re.fullmatch('^[A-Za-z0-9_-]*$', user_sign_up['username'])):    
        return "Username must include letters and numbers" 
    elif not bool(re.fullmatch('^(?=.{10,20})(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+*!=]).*$', user_sign_up['password'])): 
        return "Check your password again."
    else:
        return True

def pw_salt():
    random_digits = '''abcdeg_+]|,./;:>'''
    pw_salt=''
    i = 0 
   while i <= len(random_digits):
        random_digit = random.choice(random_digits)
        pw_salt += str(ord(random_digit))
        i +=1 
    return int(pw_salt) # The salt is a VARCHAR in the db at the moment so we can change the schema 

def pw_hash_salt(unhashed_pw,pw_salt=0):
    num = 31
    hashed_pw = 0
    for i in range(0,len(unhashed_pw)):
        hashed_pw += ((num * hashed_pw) + ord(unhashed_pw[i]))
    hashed_salted_pw = hashed_pw + pw_salt
    return hashed_salted_pw

def createRandomId():
    random_digits = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789'
    sess_id=''
    i = 0 
    while i<= len(random_digits):
        random_digit = random.choice(random_digits)
        sess_id += random_digit
        i +=1 
    return sess_id


if __name__ == '__main__':
    app.run(debug=True)



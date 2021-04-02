from flask import Flask, jsonify, request, url_for, jsonify, redirect, session, render_template, make_response, redirect, render_template
import re
import random
from psycopg2.extensions import AsIs
import psycopg2
import sys
import json
import datetime
import collections

# so that we can implement csrf tokens, we need to create a session as soon as someone visits the login or create a post page (if they don't have one already). 
# with GET request for each page, we can:

    # Check for an existing session: yes/no
    #if no:
        #create a new session and a new csrf token and store together in db (username blank). Then render relavent page with session cookie holding sid and csrf token being sent into html form. 
    #if yes:
        #check if there is a username with the session ID in db. 
        #If there is, for login:
            #render index.html
        #for post:
            # get csrf token from db where username= username and render page along with csrf token which is added to the form (need to insert hidden field into each form) 
        #if not, get csrf token where sessiondid= sessionid and return it with login.html\create_post.html 
        
#for the POST request for each page, we then just need to get the CSRF token from the sumitted data and check it in the db against the sessionID 



app = Flask(__name__)
app.config['DEBUG'] = True
search_path = "SET SEARCH_PATH TO travelly;"
app.config['SECRET_KEY'] = 'Thisisasecret!'


def createRandomId():
    random_digits = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789'
    sess_id=''
    for i in range(len(random_digits)):
        random_digit = random.choice(random_digits)
        sess_id += random_digit
    return sess_id

def escape(s):
    s = s.replace("&", "&amp;")
    s= s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s= s.replace("\"", "&quot;")
    s= s.replace("'", "&#x27;")
    s= s.replace("@", "&commat;")
    s= s.replace("=","&equals;")
    s= s.replace("`","&grave;")
    return s 

#def createRandomId():
    #random_digits = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789'
   # sess_id=''
   # i = 0 
   # while i < len(random_digits):
       # random_digit = random.choice(random_digits)
       # sess_id += random_digit
       # i += 1 
   # return sess_id


def getcon():
    connStr = "host='localhost' user='postgres' dbname='travelly' password=12345"
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
        return cur.fetchone()[0]                                                                     # this keeps the time exactly the same whether there is salt or not and stops errors later one. Coalesce stops it from returning NULL for line 94.  
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

def remove_session(username):
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute("""DELETE FROM %s WHERE username = %s""",[AsIs('tr_session'), username])
        conn.commit()
        conn.close()
        return

def insert_session(sid, username, time):
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("""INSERT INTO %s VALUES(%s,%s,%s);""", [AsIs('tr_session'), sid, username, time])
    conn.commit()
    print('inserted')
    return 

def session_auth(cookies):
    session = cookies.get('sessionID')
    if (session):
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute("SELECT sid FROM tr_session WHERE sid = %s", [session])
        resp = cur.fetchone()
        conn.commit()
        if (resp):
            return True
        else:
            return False
    else:
        return False

def get_username_from_session(sessionID):
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT username FROM tr_session WHERE sid = %s", [sessionID])
    user = cur.fetchone()
    conn.commit()
    if (user):
        return user[0]
    else:
        return 'No user'

def get_unused_pid():
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT MAX(pid) FROM tr_post;")
    conn.commit()
    return cur.fetchone()

def insert_post(post_info):
    title, country, author, content, date = post_info['title'],post_info['country'],post_info['author'],post_info['content'],post_info['date'],
    #post ID? 
    title= escape(title)
    content= escape(content) 
    country= escape(country)
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("INSERT INTO tr_post (title, country, author, content, date) VALUES (%s,%s,%s,%s,%s)", [title, country, author, content, date])
    conn.commit()

def fetch_most_recent_posts():
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT * FROM tr_post ORDER BY date DESC")
    posts = cur.fetchall()[:10]
    posts_array = []
    for post in posts:
        posts_array.append({
            "pid": post[0],
            "title": post[1],
            "country":post[2],
            "author":post[3],
            "content": post[4],
            "date": post[5]
        })
    return posts_array

def fetch_most_recent_user_posts(username):
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT * FROM tr_post WHERE author=%s ORDER BY date DESC", [username])
    posts = cur.fetchall()[:10]
    posts_array = []
    for post in posts:
        posts_array.append({
            "pid": post[0],
            "title": post[1],
            "country":post[2],
            "author":post[3],
            "content": post[4],
            "date": post[5]
        })
    return posts_array

def fetch_individual_post(id):
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT * FROM tr_post WHERE pid=%s", [id])
    post = cur.fetchone()
    return {
            "pid": post[0],
            "title": post[1],
            "country":post[2],
            "author":post[3],
            "content": post[4],
            "date": post[5]
        }

def get_user_information(sessionID):
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT username FROM tr_session WHERE sid = %s", [sessionID])
    username = cur.fetchone()
    cur.execute("SELECT * FROM tr_users WHERE username=%s", [username])
    user_details = cur.fetchone()
    return {
        "username":user_details[0],
        "firstname":user_details[1],
        "secondname":user_details[2],
        "email":user_details[3],
    }

@app.route('/')
def home():
    posts = fetch_most_recent_posts()
    print(posts[0]["title"])
    return render_template('home.html', len = len(posts), posts = posts)


#### IF a user has logged in, they can view the most recent posts from any user in the application.
@app.route('/user/<username>')
def user_page(username):
    session = session_auth(request.cookies)
    if (session):
        welcome_message = "Hello " + username 
        user_posts = fetch_most_recent_user_posts(username)
        return render_template('userpage.html', message=welcome_message, user_posts=user_posts)
    else:
        return render_template('login.html')

# @app.route('/post/<id>')
# def individual_post(id):
#     individual_post = fetch_individual_post(id)
#     return render_template('postpage.html', post=individual_post)

@app.route('/profile')
def profile_page():
    session = session_auth(request.cookies)
    if (session):
        sessionID = request.cookies.get('sessionID')
        private_user_information = get_user_information(sessionID)
        return render_template('profilepage.html', user_information=private_user_information)
    else:
        return render_template('login.html')

@app.route('/login')
def get_login():
    session = session_auth(request.cookies)
    if (session):
        return render_template("index.html")
    else:
        return render_template('login.html'
                              )

@app.route('/login', methods = ['POST'])
def post_login():   
    # get csrf token from form and check it against the one in the db for this session ID 
    # if match proceed, if not block. 
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

@app.route('/createpost')
def create_post():
    if(session_auth(request.cookies)):
        return render_template('post.html')
    else:
        return render_template('login.html')

# Make a post - POST /createpost
@app.route('/api/createpost', methods=['POST'])
def createpost():
    # Check that session exists and is valid. However, this could be removed as this check should be run
    # Before actually accessing the createpost page. To do this, run session auth on the /createpost
    # GET request and either redirect or allow post creation
    if (request.cookies.get('sessionID') and session_auth(request.cookies)):
        user_session = request.cookies.get('sessionID')
        # Useful data that can be accessed from the request object. Data sent as JSON for testing purposes
        input_data = {
        'title':request.json['title'],
        'country':request.json['country'],
        'content': request.json['content'],
        'date': datetime.datetime.now()
        }

        # In order to completed the input_data object with the missing data needed to
        # insert the post, we can use the session to access the author of the post.
        input_data['author'] = get_username_from_session(user_session)
        #input_data['pid'] = get_unused_pid()[0] + 1
        
        # Insert the data to tr_post table
        insert_post(input_data)

        return jsonify(status='post inserted')
    else:
        return jsonify(status='bad or no session')


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
    app.run(port=80, debug=True)



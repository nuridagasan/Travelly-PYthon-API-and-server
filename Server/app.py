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

# Look at checking to make sure session is still valid before carrying out actions- at the moment session is only removed at logout? 

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

app = Flask(__name__)
app.config['DEBUG'] = True
search_path = "SET SEARCH_PATH TO travelly;"
app.config['SECRET_KEY'] = 'Thisisasecret!'

<<<<<<< HEAD
def createRandomId():
    random_digits = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789'
    sess_id=''
    for i in range(len(random_digits)):
        random_digit = random.choice(random_digits) 
        sess_id += random_digit
    return sess_id
=======

# there's another copy of this function further down 
#def createRandomId():
 #   random_digits = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789'
  #  sess_id=''
   # for i in range(len(random_digits)):
    #    random_digit = random.choice(random_digits)
     #   sess_id += random_digit
    #return sess_id
>>>>>>> c9d645cf9e58fdbc7a730f5431d43b9db0daaca6

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

def fetch_five_most_pop():
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT country FROM %s GROUP BY country ORDER BY COUNT(*) DESC LIMIT 5", [AsIs('tr_post')])
    conn.commit()
    resp = cur.fetchall()
    five_most_pop_string =  " ".join([i[0] for i in resp])
    countries = five_most_pop_string.split()
    return countries

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
        "name":user_details[1],
        "surname":user_details[2],
        "email":user_details[3],
    }

def get_csrf_token(sessionID):
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT csrf FROM tr_session WHERE sid = %s", [sessionID])
    csrf_token = cur.fetchone()[0]
    return csrf_token


@app.route('/home', methods = ['GET'])
def home():
    home_buttons = False
    posts = fetch_most_recent_posts()
    session = session_auth(request.cookies)
    countries = fetch_five_most_pop()
    if (session):
        sessionID = request.cookies.get('sessionID')
        #private_user_information = get_user_information(sessionID)
        return render_template('home.html', len = len(posts), posts = posts, create_form = True, home_buttons = True, fav_countries = countries, len_countries = len(countries) )
    else:
        return render_template('home.html', len = len(posts), posts = posts, fav_countries = countries, len_countries = len(countries))

# Make a post - POST /createpost
@app.route('/home', methods=['POST'])
def createpost():
    # Check that session exists and is valid. However, this could be removed as this check should be run
    # Before actually accessing the createpost page. To do this, run session auth on the /createpost
    # GET request and either redirect or allow post creation
    posts = fetch_most_recent_posts()
    if (request.cookies.get('sessionID') and session_auth(request.cookies)):
        user_session = request.cookies.get('sessionID')
        # Useful data that can be accessed from the request object. Data sent as JSON for testing purposes
        input_data = {
        'title': str(request.form['post-title'].lower()),
        'country': str(request.form.get('country').lower()),
        'content': str(request.form['post-content'].lower()),
        'date': datetime.datetime.now()
        }

        # In order to completed the input_data object with the missing data needed to
        # insert the post, we can use the session to access the author of the post.
        input_data['author'] = get_username_from_session(user_session)
        #input_data['pid'] = get_unused_pid()[0] + 1
        # Insert the data to tr_post table
        insert_post(input_data)
        return redirect(url_for('home'))
    else:
        return jsonify(status='bad or no session')

@app.route('/logout', methods=['GET'])
def logout():
    session = request.cookies['sessionID']
    if (session and request.method == 'GET'):
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute("DELETE FROM %s WHERE sid=%s", [AsIs('tr_session'), session])
        conn.commit() 
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))   

@app.route('/home/<country>')
def return_counry_posts(country):
    session = session_auth(request.cookies)
    countries = fetch_five_most_pop()
    conn = getcon()
    cur = conn.cursor()
    cur.execute(search_path)
    cur.execute("SELECT * FROM %s WHERE country=%s", [AsIs('tr_post'), country])
    conn.commit()
    res = cur.fetchall()
    posts = []
    for p in res:
        post = {
            "pid": p[0],
            "title": p[1],
            "country": p[2],
            "author": p[3],
            "content": p[4],
            "date": p[5]
        }
        posts.append(post)
    if (session):
        sessionID = request.cookies.get('sessionID')
        return render_template('home.html', len = len(posts), posts = posts, create_form = True, home_buttons = True, fav_countries = countries, len_countries = len(countries) )
    else:
        return render_template('home.html', len = len(posts), posts = posts, fav_countries = countries, len_countries = len(countries))

  
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

@app.route('/post/<id>')
def individual_post(id):
    individual_post = fetch_individual_post(id)
    return render_template('postpage.html', post=individual_post)

@app.route('/profile')
def profile_page():
    session = session_auth(request.cookies)
    if (session):
        sessionID = request.cookies.get('sessionID')     
        private_user_information = get_user_information(sessionID)
        user_posts = fetch_most_recent_user_posts(private_user_information["username"])
        return render_template('profile.html', user_info=private_user_information, posts = user_posts, len = len(user_posts))
    else:
        return render_template('login.html')

@app.route('/login')
def get_login(): 
    session_exists = session_auth(request.cookies)
    if session_exists:
        if 'username' in session:
            return redirect(url_for('home'))
        else:
            sessionID= request.cookies.get('sessionID')
            csrf_token = get_csrf_token(sessionID)
            resp = make_response(render_template('login.html', csrf_token= csrf_token))
            return resp 
    else:
        sessionID= createRandomId()
        csrf_token= createRandomId()
        expire = datetime.datetime.now() + datetime.timedelta(hours=2)
        sql= "INSERT into tr_session VALUES (%s, %s, %s, %s)"
        data = (sessionID,'NULL',  expire,csrf_token,)
        conn = getcon()
        cur = conn.cursor()
        cur.execute(search_path)
        cur.execute(sql, data)
        conn.commit()
        resp = make_response(render_template('login.html', csrf_token= csrf_token))
        resp.set_cookie('sessionID', sessionID)
        return resp


@app.route('/login', methods = ['POST'])
def post_login():   
    # get csrf token from form and check it against the one in the db for this session ID 
    # if match proceed, if not block. 
<<<<<<< HEAD
    session = session_auth(request.cookies)

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
=======

    user_csrf_token = request.form['csrf_token'].strip("/")
    sessionID= request.cookies.get('sessionID')
    csrf_token= get_csrf_token(sessionID)
    if csrf_token == user_csrf_token:
        data = {
                'username' : request.form['username'].lower(),
                'password' : request.form['password']
        }
        expire = datetime.datetime.now() + datetime.timedelta(hours=2)
        try:
            sql= "SELECT count(*) from tr_users WHERE username =%s and password= %s"  #The count sends back 0 or 1 as a result, depending on whether the pw and username are correct 
            user_input_password = pw_hash_salt(data['password'], (get_salt_from_db(data['username'])))
            query_data = (data['username'], (user_input_password))
>>>>>>> c9d645cf9e58fdbc7a730f5431d43b9db0daaca6
            conn = getcon()
            cur = conn.cursor()
            cur.execute(search_path)
            cur.execute(sql, query_data)
            check_account = cur.fetchone()[0]
            # if there is a result, the pw and username were correct 
            if check_account != 0:
                conn = getcon()
                cur = conn.cursor()
                cur.execute(search_path)
                cur.execute("DELETE FROM %s WHERE sid=%s", [AsIs('tr_session'), sessionID])
                conn.commit() 
                sessionID = createRandomId()
                conn = getcon()
                cur = conn.cursor()
                cur.execute(search_path)
                cur.execute("""DELETE FROM %s WHERE username = %s""",[AsIs('tr_session'), data['username']])
                # may need to add csrf token here if we do it for create_post form 
                cur.execute("""INSERT INTO %s VALUES(%s,%s,%s);""", [AsIs('tr_session'), sessionID, data['username'], str(expire)])
                conn.commit()
                resp = make_response(redirect('/home'))
                resp.set_cookie('sessionID', sessionID)
                session['username'] = data['username'] 
                session['sessionid'] = sessionID
                return resp
            else:
                return render_template('login.html', check_input = 'Incorrect username or password', csrf_token= csrf_token)
        except Exception as e:
            print(e)
            return render_template('login.html', check_input = 'Something happened BAD!')
    else: 
        return render_template('login.html', check_input = 'CSRF tokens do not match.')


@app.route('/signup', methods = ['GET','POST'])
def signup_form():    
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        print(request.form['password'])
        user_sign_up = {
            'firstname' :  request.form['name'].lower(),
            'lastname' : request.form['surname'].lower(),
            'username' : request.form['username'].lower(),
            'email' : request.form['email'].lower(),
            'dob' : request.form['birthdate'],
            'password' : request.form['password'],
            'salt' : pw_salt()
        }
        #print(user_sign_up)
        #first check user inputs are valid firstname, lastname, username, email and password
        check_input = input_validation(user_sign_up)
        #print(check_input)
        if check_input == True:
            #hash and salt password before sending it to database
            user_sign_up['password'] = pw_hash_salt(user_sign_up['password'],user_sign_up['salt'])
            #insert user details to database. It returns a message whether the user is successfully
            #inserted or not
            return render_template('signup.html', check_input = insert_user(user_sign_up))
        else:
            #Give error message to user
            print('bad entry')
            return render_template('signup.html', check_input = check_input)

@app.route('/createpost')
def create_post():
    if(session_auth(request.cookies)):
        return render_template('post.html')
    else:
        return render_template('login.html')


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
        i = i+1
    return int(pw_salt)

def pw_hash_salt(unhashed_pw,pw_salt=0):
    num = 31
    hashed_pw = 0
    for i in range(0,len(unhashed_pw)):
        hashed_pw += ((num * hashed_pw) + ord(unhashed_pw[i]))
    hashed_salted_pw = hashed_pw + pw_salt 
    return hashed_salted_pw

# def createRandomId():
#     random_digits = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789'
#     sess_id=''
#     i = 0 

#     while i <= len(random_digits):
#         random_digit = random.choice(random_digits)
#         sess_id += random_digit
#         i += 1 
    
#     return sess_id


if __name__ == '__main__':
    app.run(port=80, debug=True)



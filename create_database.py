import psycopg2
import datetime
import random
from psycopg2.extensions import AsIs
def getConn():
    #pwFile = open("pw.txt", "r")
    #pw = pwFile.read()
    #pwFile.close()
    connStr = "host=localhost \
               dbname=Travelly user=postgres password = " + "password"
    conn=psycopg2.connect(connStr)      
    return  conn
    
USERS=["Aleida King","Billye Quayle","Mildred Beaty","Adeline Beyers","Tricia Wendel","Kizzy Bedoya","Marx Warn","Hulda Culberson","Devona Morvant","Winston Tomasello","Dede Frame","Lissa Follansbee","Timmy Dapolito","Gracie Lonon","Nana Officer","Yuri Kruchten","Chante Brasch","Edmond Toombs","Scott Schwan","Lean Beauregard","Norberto Petersen","Carole Costigan","Chantel Drumheller","Riva Redfield","Jennie Sandifer","Vivian Cimini","Goldie Hayworth","Tomeka Kimler","Micaela Juan","Jerrold Tjaden","Collene Olson","Edna Serna","Cleveland Miley","Ena Haecker","Huey Voelker","Annamae Basco","Florentina Quinlan","Eryn Chae","Mozella Mcknight"]

COUNTRIES=[ 
'France', 
'Spain', 
'United States', 
'China', 
'Italy', 
'Mexico', 
'United Kingdom', 
'Turkey', 
'Germany', 
'Thailand', 
'Austria', 
'Japan', 
'China', 
'Greece', 
'Malaysia', 
'Russia', 
'Canada', 
'Poland', 
'Netherlands',  
'Saudi Arabia',
'Croatia',
'India', 
'Portugal', 
'Ukraine', 
'Indonesia', 
'Singapore', 
'Korea', 
'Vietnam', 
'Denmark', 
'Bahrain', 
'Morocco', 
'Belarus', 
'Romania', 
'Ireland', 
'South Africa', 
'Czech Republic', 
'Switzerland', 
'Bulgaria', 
'Australia', 
'Belgium', 
'Egypt', 
'Kazakhstan', 
'United Arab Emirates', 
'Sweden', 
'Tunisia', 
'Argentina', 
'Philippines', 
'Brazil', 
'Georgia', 
'Chile', 
'Norway', 
'Dominican Republic', 
'Hungary', 
'Cambodia', 
'Syrian Arab Republic', 
'Iran', 
'Albania', 
'Cuba', 
'Kyrgyz Republic', 
'Colombia', 
'Peru', 
'Jordan', 
'Puerto Rico', 
'Uruguay', 
'Cyprus', 
'Israel', 
'Slovenia', 
'New Zealand', 
'Myanmar', 
'Lao PDR', 
'Estonia', 
'Finland', 
'Costa Rica', 
'Andorra', 
'Uzbekistan', 
'Lithuania', 
'Azerbaijan', 
'Algeria', 
'Zimbabwe', 
'Oman', 
'Jamaica', 
'Malta', 
'Qatar', 
'Iceland', 
'Slovak Republic', 
'Sri Lanka', 
'Guatemala', 
'Latvia', 
'Nigeria', 
'Montenegro', 
'Lebanon', 
'Panama', 
'Côte d\'Ivoire', 
'Nicaragua', 
'Ecuador', 
'Paraguay', 
'Botswana', 
'El Salvador', 
'Namibia'] 

def create_schema(cur):
    cur.execute(open("schema.sql", "r").read())

def create_user(name):
    password='password'
    username = name.split()[0] + '999'
    email = '%s.%s@email.com'%(name.split()[0][1].lower(), name.split()[1].lower())
    firstname= name.split()[0]
    lastname= name.split()[1]
    dob = datetime.date(1990,1,1)
    salt = 12345
    return [username, firstname, lastname, email, dob, password, salt]

 
def create_post(author, country, unique_id):
    pid=unique_id
    content = 'Content for this post'
    title = 'post about %s'%(country)
    date = datetime.date.today().replace(day=1, month=1) + datetime.timedelta(days=random.randint(0, 365))
    return [pid, title, country, author, content, date]
    
 
# def create_comment(cur, cid,pid, author):
#     for i in range(random.randrange(2,5)):
#         content = 'Comment %d'%(i)
#         date = date + datetime.timedelta( random.randrange(1,3), minutes=random.randrange(1,120), hours=random.randrange(0,6) )
#         cur.execute('INSERT INTO tr_comment (cid, author, content,date) VALUES (?,?,?,?,?,?)',(id, country, author, content,date))
        
try: 
    conn=None   
    conn=getConn()
    cur = conn.cursor()
    
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE", [AsIs('travelly')])

    file_p = open('schema.sql', 'r')
    cur.execute(file_p.read())
    
    for user in USERS:
        cur.execute("INSERT INTO tr_users VALUES (%s,%s,%s,%s,%s,%s,%s)", create_user(user))

    cur.execute("SELECT username FROM tr_users")
    users = cur.fetchall()
    
    for i, country in enumerate(COUNTRIES):
        user = random.choice(users)
        cur.execute("INSERT INTO tr_post VALUES (%s,%s,%s,%s,%s,%s)", create_post(user, country, i))

    conn.commit()
    conn.close()


except Exception as e:
    print (e)
import psycopg2
import datetime
import random

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



def create_user(cur, dob,name,salt):
    password='password'
    username = '%s%s'%(name.split()[0][1].lower(), name.split()[1].lower())
    email = '%s.%s@email.com'%(name.split()[0][1].lower(), name.split()[1].lower())
    fname= name.split()[0]
    lastname= name.split()[1]
    sql='SET search_path to travelly; INSERT INTO tr_user (username, firstname,lastname, email, dob, password, salt) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
    data= (username, fname,lastname, email, dob, password, salt)
    cur.execute(sql,data)
 
 
def create_post(cur, country, author,date):
    content = 'Content for this post'
    title = 'post about %s'%(country)
    date = date + datetime.timedelta( random.randrange(1,3), minutes=random.randrange(1,120), hours=random.randrange(0,6) )
    sql='SET search_path to travelly; INSERT INTO tr_post ( title, country, author, content,date) VALUES (%s,%s,%s,%s,%s)'
    data= (title, country, author, content,date)
    cur.execute(sql,data)
 
# def create_comment(cur, cid,pid, author):
#     for i in range(random.randrange(2,5)):
#         content = 'Comment %d'%(i)
#         date = date + datetime.timedelta( random.randrange(1,3), minutes=random.randrange(1,120), hours=random.randrange(0,6) )
#         cur.execute('INSERT INTO tr_comment (cid, author, content,date) VALUES (?,?,?,?,?,?)',(id, country, author, content,date))
        
try: 
        conn=None   
        conn=getConn()
        cur = conn.cursor()
        cid= 10
        salt= 12345
        dob = datetime.date(1990,1,1)
        date = datetime.datetime.now() - datetime.timedelta(28)
        for user in USERS:
            create_user(cur, dob,user,salt)
            id+=1
            salt +=1
            dob = dob + datetime.timedelta(days=1) 
            conn.commit()
        for country in COUNTRIES:
            create_post(cur,country, 1001,date)
            conn.commit()
        print("insert sucessful")
        conn.close()


except Exception as e:
    print (e)           
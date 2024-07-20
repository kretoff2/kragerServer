import json
import random
import socket
import smtplib
import pymysql as sql
from email.mime.text import MIMEText
from twilio.rest import Client
import fastapi

config = None
with open('core_config.json', 'r') as f:
    config = json.load(f)
print('server started')

def sql_conn():
    try:
        conn = sql.connect(
            host=config['SQL_IP'],
            port=config['SQL_PORT'],
            user=config['SQL_USER'],
            password=config['SQL_PASSWORD'],
            database=config['DB_NAME']
        )
        return conn
    except Exception as ex:
        print("No conaction SQL...")
        print(ex)
        return -1

app = FastAPI

conn = sql_conn()
cur= conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, id int, login varchar(50), tag varchar(50), password varchar(50), email varchar(50), subtitle varchar(50), num varchar(15))')
conn.commit()
cur.close()

temp = {
    "users_reg_codes":{

    }
}
def send_email(message, messageTo):
    sender = "kretoffauth@gmail.com"
    password = "mfhp qkkh axbh jgcs"

    smtpServer = smtplib.SMTP("smtp.gmail.com", 587)
    smtpServer.starttls()
    try:
        smtpServer.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = "Верификация"
        smtpServer.sendmail(sender,messageTo, msg.as_string())
        #print("message sanded")
    except Exception as _ex:
        print(f'Error: {_ex}')

def reg(cod, tag, password, email):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE tag = '{tag}'")
    thisLoginUser = cur.fetchone()
    cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
    thisEmailUser = cur.fetchone()
    if thisLoginUser != None:
        conn.commit()
        cur.close()
        return {"data": "invalidLogin"}
    elif thisEmailUser != None:
        conn.commit()
        cur.close()
        return {"data": "invalidEmail"}
    if cod == authCode:
        cur.execute('INSERT INTO users (tag, password, email) VALUES ("%s", "%s", "%s")' % (tag, password, email))
        conn.commit()
        cur.close()
        conn.close()
        return {"data": "goodRegistration"}
    else:
        user.send('wrongCode'.encode('utf-8'))
        return {"data": "wrongCode"}

def log(tag, password):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE tag = ? AND password = ?", (tag, password))
    thisUser = cur.fetchone()
    conn.commit()
    cur.close()
    if thisUser == None:
        return {"data": "invalidLoginOrPassword"}
    else:
        return {"data": "goodLogin"}

@app.get("/")
def main(data = Body()):
    pass
@app.get("/sandReg")
def main(data = Body()):
    try:
        authCode = str(random.randint(100000, 999999))
        user_id = len(temp["users_reg_codes"])
        temp["users_reg_codes"][user_id] = authCode
        _email = data["email"]
        send_email(f"Ваш код авторизации: {authCode}. Здравствуйте, на этот адрес электронной почты пытаются зарегестрировать аккаунт в krager. Если это не вы, просто проигнорируйте это сообщение",_email)
        return {"data": "message_sanded", "your_id": user_id}
    except Exception as _ex:
        return {"data": f"error {_ex}"}
@app.get("/reg")
def main(data = Body()):
    return reg(data["cod"], data["tag"], data["password"], data["email"])
@app.get("/login")
def main(data = Body()):
    return log(data["tag"], data["password"])


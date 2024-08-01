import json
import random
import socket
import smtplib
import pymysql as sql
from email.mime.text import MIMEText
from twilio.rest import Client
import fastapi
from  fastapi import FastAPI, Body
from decoder import generate_random_string
import time

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

app = FastAPI()

conn = sql_conn()
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, userID varchar(8), login varchar(50), tag varchar(50), password varchar(50), email varchar(50), subtitle varchar(50), num varchar(15), dayOfBirthdae varchar(50))')
cur.execute('CREATE TABLE IF NOT EXISTS chatsList (id int auto_increment primary key, chatID varchar(64), user1ID varchar(8), user2ID varchar(8))')
cur.execute('CREATE TABLE IF NOT EXISTS staticKeys (id int auto_increment primary key, userID varchar(8), deviceID int, staticKey varchar(128), timeReg int)')
cur.execute('CREATE TABLE IF NOT EXISTS conf (id int auto_increment primary key,userID varchar(8), viewNumber bit, viewTime bit, viewEmail bit, viewIcon bit, resandMessage bit, collin bit, gs bit, sendMessage bit, viewDateOfBirthday bit, viewSubtitle bit)')
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

def reg(cod, tag, password, email, id):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE tag = %s", (tag,))
    thisLoginUser = cur.fetchone()
    cur.execute(f"SELECT * FROM users WHERE email = %s", (email,))
    thisEmailUser = cur.fetchone()
    if thisLoginUser != None:
        conn.commit()
        cur.close()
        return {"data": "invalidLogin"}
    elif thisEmailUser != None:
        conn.commit()
        cur.close()
        return {"data": "invalidEmail"}
    if cod == temp["users_reg_codes"][id]:
        staticKey = generate_random_string(128)
        id = generateUserID()
        cur.execute('INSERT INTO users (tag, password, email, userID) VALUES ("%s", "%s", "%s", "%s")' % (tag, password, email, id))
        cur.execute('INSERT INTO staticKeys (userID, deviceID, staticKey, timeReg) VALUES ("%s","%s","%s", "%s")' % (id, 0, staticKey, int(time.time())))
        conn.commit()
        cur.close()
        conn.close()
        return {"data": "goodRegistration", "tag":tag, "email":email, "id":id, "key":staticKey}
    else:
        user.send('wrongCode'.encode('utf-8'))
        return {"data": "wrongCode"}
def generateUserID():
    id = generate_random_string(8)
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM users WHERE userID = %s', (id,))
    r = cur.fetchall()
    if r == None or len(r) <= 0:
        return id
    else: return generateUserID()
def log(tag, password):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE tag = %s AND password = %s", (tag, password))
    thisUser = cur.fetchone()
    if thisUser == None:
        conn.commit()
        cur.close()
        return {"data": "invalidLoginOrPassword"}
    else:
        staticKey = generate_random_string(128)
        cur.execute('SELECT * FROM statickeys WHERE userID = %s', (thisUser[1],))
        d = cur.fetchall()
        cur.execute('INSERT INTO statickeys (userID, deviceID, staticKey, timeReg) VALUES ("%s","%s","%s", "%s")' % (thisUser[1], len(d), staticKey, int(time.time())))
        conn.commit()
        cur.close()
        return {"data": "goodLogin", "userInfo":{"userID":thisUser[1], "login":thisUser[2], "tag":thisUser[3], "email":thisUser[5],"subTitle":thisUser[6], "num":thisUser[7]}, "key":staticKey, "deviceID":len(d)}

def see_chat_list(userID):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM chatsList WHERE user1ID = %s OR user2ID = %s", (userID,userID))
    chats = cur.fetchall()
    data = {"chatsCol":f"{len(chats)}","chatList":{}}
    for el in chats:
        data["chatList"][el[1]] = {}
        data["chatList"][el[1]]["user1ID"] = el[2]
        data["chatList"][el[1]]["user2ID"] = el[3]
    return data
@app.get("/test")
def main():
    return f"Have conect!!!"
@app.post("/")
def main(data = Body()):
    if data["data"] == "get_my_chats":
        return {"chats": see_chat_list(data["my_id"])}
@app.post("/sandReg")
def main(data = Body()):
    #try:
        authCode = str(random.randint(100000, 999999))
        user_id = len(temp["users_reg_codes"])
        temp["users_reg_codes"][str(user_id)] = authCode
        print(temp)
        _email = data["email"]
        send_email(f"Ваш код авторизации: {authCode}. Здравствуйте, на этот адрес электронной почты пытаются зарегестрировать аккаунт в krager. Если это не вы, просто проигнорируйте это сообщение",_email)
        return {"data": "message_sanded", "your_id": user_id}
    #except Exception as _ex:
        #return {"data": f"error {_ex}"}
@app.post("/reg")
def main(data = Body()):
    return reg(data["cod"], data["tag"], data["password"], data["email"], data["id"])
@app.post("/login")
def main(data = Body()):
    return log(data["tag"], data["password"])


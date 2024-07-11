import json
import random
import socket
import smtplib
import pymysql as sql
import json
from email.mime.text import MIMEText

config = None
with open('core_config.json', 'r') as f:
    config = json.load(f)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1',config['PORT']))
server.listen(40)
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
conn = sql_conn()
cur= conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, login varchar(50), tag varchar(50), password varchar(50), email varchar(50), subtitle varchar(50), num varchar(15))')
conn.commit()
cur.close()
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
        print("message sanded")
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
        user.send('invalidLogin'.encode('utf-8'))
        conn.commit()
        cur.close()
        return
    elif thisEmailUser != None:
        user.send('invalidEmail'.encode('utf-8'))
        conn.commit()
        cur.close()
        return
    if cod == authCode:
        cur.execute('INSERT INTO users (tag, password, email) VALUES ("%s", "%s", "%s")' % (tag, password, email))
        user.send('goodRegistration'.encode('utf-8'))
    else:
        user.send('wrongCode'.encode('utf-8'))
    conn.commit()
    cur.close()
    conn.close()

def log(tag, password):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE tag = ? AND password = ?", (tag, password))
    thisUser = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if thisUser == None:
        user.send('invalidLoginOrPassword'.encode('utf-8'))
    else:
        user.send('goodLogin'.encode('utf-8'))

authCode = "0"
while True:
    user, address = server.accept()
    print(f'connected:\t{user}')
    command = user.recv(1024).decode('utf-8')
    comm = command.split("⫓")
    if comm[0] == "sandReg":
        authCode = str(random.randint(100000, 999999))
        send_email(f"Ваш код авторизации: {authCode}. Здравствуйте, на этот адрес электронной почты пытаются зарегестрировать аккаунт в krager. Если это не вы, просто проигнорируйте это сообщение",comm[1])
    elif comm[0] == "reg":
        reg(comm[1],comm[2],comm[3],comm[4])
    elif comm[0] == "login":
        log(comm[1],comm[2])
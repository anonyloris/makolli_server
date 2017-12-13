import grp, pwd
import os
import pymysql
import crypt

def get_server_user():
    user_list = []
    for p in pwd.getpwall():
	user_list.append(p[0])
    return user_list

def get_web_user():
    conn = pymysql.connect(host='localhost', user='root', password='dlrauddmlfhfltm!', db='makolli_web', charset='utf8')
    try:
	user_list=[]
	with conn.cursor() as curs:
	    select_sql = 'SELECT id FROM member'
	    curs.execute(select_sql, ())
	    
	    for i in curs.fetchall():
		user_list.append(i)
	return user_list

    finally:
	conn.close()

def add_user(username):
    conn = pymysql.connect(host='localhost', user='root', password='dlrauddmlfhfltm!', db='makolli_web', charset='utf8')
    pw = ''
    try:
	with conn.cursor() as curs:
	    select_sql = 'SELECT password FROM member WHERE id=%s'
	    curs.execute(select_sql, (username))
	    pw = curs.fetchall()[0][0]
	enc_pw = crypt.crypt(pw, '22')
	os.system('useradd -p '+enc_pw+' '+str(username))
	    
    finally:
	conn.close()

web_user = get_web_user()
server_user = get_server_user()

for usr in web_user:
    if server_user.count(usr[0]) == 0:
	add_user(usr[0])



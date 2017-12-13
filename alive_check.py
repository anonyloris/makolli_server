import socket
import threading
import schedule
import datetime
from operator import eq
import pymysql
import daemon
import os
import sys

def collector_alive(username, userip, menu):
    conn = pymysql.connect(host = 'localhost', user='root', password = 'dlrauddmlfhfltm!', db = 'makolli_web', charset='utf8')
    if eq(menu, 'net'):
	update_sql = 'UPDATE client SET netcollectorlive=%s WHERE cip=%s AND sid=%s'
    elif eq(menu, 'artifact'):
	update_sql = 'UPDATE client SET syscollectorlive=%s WHERE cip=%s AND sid=%s'
    else:
	return
	
    try:
	user_sid = 0
	with conn.cursor() as curs:
	    select_sql = 'SELECT sid FROM member WHERE id=%s'
	    curs.execute(select_sql, (username))
	    user_sid = curs.fetchall()[0][0]

	with conn.cursor() as curs:
	    curs.execute(update_sql, (str(datetime.datetime.now()), userip, user_sid))
	    conn.commit()

    finally:
	conn.close()

def set_socket(s):
    while True:
	s.listen(1)
	conn, addr = s.accept()

	data = conn.recv(64)

	username, userip, menu = data.split('/')

	collector_alive(username, userip, menu)

	conn.close()

def main():
    pid = str(os.getpid())
    pidfile = '/var/lock/makolli_alive.pid'

    if os.path.isfile(pidfile):
	sys.exit()
    file(pidfile, 'w').write(pid)

    try:
	HOST = ''
	PORT = 50506
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))

	while True:
	    socket_thread = threading.Thread(target=set_socket, args=(s,))
	    socket_thread.start()
	    socket_thread.join()

	s.close()
    finally:
	os.unlink(pidfile)

with daemon.DaemonContext():
    main()

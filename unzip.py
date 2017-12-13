from zipfile import ZipFile
from operator import eq
import pymysql
import requests
import tarfile
import os
import sys
import datetime
import socket
import threading
import daemon
import shutil

def set_db(username, userip, agent_data):
    conn = pymysql.connect(host='localhost', user='root', password='dlrauddmlfhfltm!',db='makolli_web', charset='utf8')
    try:
    	user_sid = 0
	with conn.cursor() as curs:
    	    select_sql = 'SELECT sid FROM member WHERE id=%s'
	    curs.execute(select_sql, (username))
	    user_sid = curs.fetchall()[0][0]
	    
	
	with conn.cursor() as curs:
	    insert_sql = 'INSERT INTO client(sid, cip, os, osver, osbit, kernelver, kernelbit, cpu, totalstorage, memory) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
	    curs.execute(insert_sql, (user_sid, userip, agent_data[0], agent_data[1], agent_data[2], agent_data[3], agent_data[4], agent_data[5], agent_data[6], agent_data[7]))
	    conn.commit()
	 
    finally:
	conn.close()

def compressor_alive(username, userip):
    conn = pymysql.connect(host = 'localhost', user='root', password = 'dlrauddmlfhfltm!', db = 'makolli_web', charset='utf8')

    try:
        with conn.cursor() as curs:
            update_sql = 'UPDATE client SET compressorlive=%s WHERE cip=%s'
            curs.execute(update_sql, (str(datetime.datetime.now()), userip))

        conn.commit()
    finally:
        conn.close()

def unzip_logs(username, userip):
    log_dir = os.path.join("/home", username, userip)

    log_list = os.listdir(log_dir)
    log_list.sort()
    log_zip = ZipFile(os.path.join(log_dir,log_list[-1]))
    del log_list

    logs = log_zip.namelist()
    artifacts = []

    for i in logs:
  	if i.startswith("artifact_collector"):
	    artifacts.append(i)
	    log_zip.extract(i, "./")
    	else:
	    pass

    del logs
    log_zip.close()

    artifacts.sort()
    src_log = artifacts[-1]
    del artifacts

    try:
       	with tarfile.open(src_log, "r:gz") as tar:
	    for tarinfo in tar:
	        try:
	       	    name = tarinfo.name.split('/')[1]
		    if name.endswith('_'):
			tar.extract(tarinfo, log_dir)
		except:
		    pass
    except:
	pass

    shutil.rmtree('artifact_collector', ignore_errors=False, onerror=None)

def set_config_dir(username, userip):
    user_dir = os.path.join('/home', username)
    if not os.path.isdir(user_dir):
	os.mkdir(user_dir)

    user_dir = os.path.join(user_dir, userip)
    if not os.path.isdir(user_dir):
	os.mkdir(user_dir)

def set_socket(s):
    while True:
	s.listen(1)
	conn, addr = s.accept()

	data = conn.recv(64)

	menu, userip, username = data.split('/')

	if eq(menu, 'unzip'):
	    unzip_logs(username, userip)
	    compressor_alive(username, userip)
	elif eq(menu, 'config'):
	    agent_data = conn.recv(1024)
	    set_config_dir(username, userip)
	    set_db(username, userip, agent_data.split('/'))

	conn.close()

def main():
    pid = str(os.getpid())
    pidfile = "/var/lock/makolli_centor.pid"

    if os.path.isfile(pidfile):
	print "%s already exists, exiting" % pidfile
	sys.exit()

    file(pidfile, 'w').write(pid)
    try:
    	HOST = ""
    	PORT = 50505
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


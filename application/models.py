import pymysql
import uuid
<<<<<<< HEAD
import time,random
host = "charityvote.cloalfxvxpbz.us-west-2.rds.amazonaws.com"
port = 3306
password ="tree1234"
username = "root"

def create_competition (title,amount,expiry_date):
    db = MySQLdb.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    print ("Creating Competition")
    flag = 1
    while flag == 1:
        try :
            id =  int(time.time()) + int(random.random())
            cursor.execute("insert into competitions values (%s,%s,%s,%s) ",(id,title,amount,expiry_date))
            flag = 0
        except MySQLdb.IntegrityError as e:
            if 'PRIMARY' in e.message:
                continue
    db.commit()
    print ("Creating Done")
    return id




def create_option (description,image_url,comp_id):
    db = MySQLdb.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    flag = 1
    while flag ==1:
        try:
            id =  int(time.time()) + int(random.random())
            cursor.execute("insert into comp_option values (%s,%s,%s,%s) ",(id,description,image_url,comp_id))
        except MySQLdb.IntegrityError as e:
            if 'PRIMARY' in e.message:
                continue
                
    db.commit()
=======
from flask import current_app as application

with application.app_context():
    
>>>>>>> 24332185dffef4f907922d53142b23262cba78f0

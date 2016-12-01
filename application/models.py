import MySQLdb
import uuid
host = "charityvote.cloalfxvxpbz.us-west-2.rds.amazonaws.com"
port = 3306
password ="tree1234"
username = "root"

def create_competition (title,amount,expiry_date):
    db = MySQLdb.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    id =  uuid.uuid4()
    cursor.execute("insert into competitions values (%s,%s,%s,%s) ",(id,title,amount,expiry_date))
    db.commit()
    return id




def create_option (description,image_url,comp_id):
    db = MySQLdb.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    id =  uuid.uuid4()
    ursor.execute("insert into comp_option values (%s,%s,%s,%s) ",(id,description,image_url,comp_id))
    db.commit()
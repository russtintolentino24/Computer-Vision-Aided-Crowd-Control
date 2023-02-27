import sqlite3
from sqlite3 import Error
import tkinter
import os

global db = None

#Fxn to create database object if error occurs just close object
def create_conn(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print('Database connected/created')
    except Error as e:
        print(e)
    finally:
        if conn is None:
            conn.close()
        else:
            return conn
    
#Fxn to create table using sql command
def create_table(conn,create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

#Fxn to create login entry in database
#assumes that login entry is unique already
def create_login(conn,login_cred):

    #parameters: login_cred( name , password , access)

    sql_create_login = ''' INSERT INTO login (name,password,access)
                            VALUES(?,?,?); '''
    c = conn.cursor()
    c.execute(sql_create_login,login_cred)
    conn.commit()
    
    return c.lastrowid
        
#Fxn to get number of rows in table
def get_rowcnt(conn,table_name):
    sql_get_rowcnt = ' SELECT * FROM ' + table_name + ';'
    c = conn.cursor()
    c.execute(sql_get_rowcnt)
    rowcnt = len(c.fetchall())      
    return rowcnt

def setup_db():
    #get current working directory and create main database there
    cwd = str(os.getcwd()) + '/database.db'
    print(cwd)
    db  = create_conn(cwd)

    #actual sql to create table
    sql_create_login_table = """ CREATE TABLE IF NOT EXISTS login (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                password text NOT NULL,
                                access integer NOT NULL 
                            );"""
            
    create_table(db,sql_create_login_table)

    #default login credentials for new table
    login_cred = ("admin","password", 3)
    #create_login(db,login_cred)
    #print(get_rowcnt(db,'login'))
    db.close()
    




if __name__ == '__main__':
    setup_db()  #connect to database and/or initialize tables
    mainwindow = tkinter.Tk()
    mainwindow.mainloop()


    

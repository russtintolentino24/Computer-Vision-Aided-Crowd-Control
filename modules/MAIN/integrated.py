import sqlite3
from sqlite3 import Error
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import videofeed
from videofeed import *

import cv2
import imutils
import numpy as np
from PIL import ImageTk, Image

import time
import logging
import os
#-----------------------Added by Cris Marc-------------------------
#--------Live feed and counter button---------------------------
def videoLiveFeed():
        os.system('python3 videofeed.py -c true')

def videoArchivedFeed():
        os.system('python3 videofeed.py -v samplevid.mp4')

    #-----------------------end---------------------------------------

#------------------------------START OF FXNS FOR US-3-------------------------
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
        


def setup_db():
    #get current working directory and create main database there
    cwd = str(os.getcwd()) + '/sampledb.db'
    print(cwd)
    
    #assume that database is already created and we only need to connect
    global db
    db  = create_conn(cwd)


def close_db():
    db.close()
#------------------------------END OF FXNS FOR US-3-------------------------

#------------------------------START OF FXNS FOR US-1-------------------------

# Decide how much of our database will be shown based on user access credential
def view_db_screen():
    if(login_access == 1): admin_db_screen()
    else: rest_db_screen()



# Show all since user is an admin
def admin_db_screen():
    db_screen = Toplevel()
    db_screen.title("User login database")
    db_screen.geometry("800x300")

    #Setup tree/table
    global db_tree
    db_tree = ttk.Treeview(db_screen,column=("c1","c2","c3","c4"),show='headings')
    db_tree.column("#1",anchor=CENTER)
    db_tree.heading("#1",text="ID")
    db_tree.column("#2",anchor=CENTER)
    db_tree.heading("#2",text="Name")
    db_tree.column("#3",anchor=CENTER)
    db_tree.heading("#3",text="Password")
    db_tree.column("#4",anchor=CENTER)
    db_tree.heading("#4",text="Access")
    
    db_tree.pack()

    fetch_all()

    Button(db_screen, text="add user", width=10, height=1, command=register).pack()
    Label(db_screen, text="").pack()
    Button(db_screen, text="Delete a user", width=10, height=1, command=del_user_screen).pack()


# Show restricted db screen since user is regular
def rest_db_screen():
    db_screen = Toplevel()
    db_screen.title("User login database")
    db_screen.geometry("800x300")

    #Setup tree/table
    global db_tree
    db_tree = ttk.Treeview(db_screen,column=("c1","c2"),show='headings')
    db_tree.column("#1",anchor=CENTER)
    db_tree.heading("#1",text="ID")
    db_tree.column("#2",anchor=CENTER)
    db_tree.heading("#2",text="Name")
  
    db_tree.pack()

    fetch_all()


# Get all rows from database
def fetch_all():
    c = db.cursor()
    c.execute("SELECT * FROM login")
    rows = c.fetchall()
 
    #clear table first
    db_tree.delete(*db_tree.get_children())

    #Fill empty table
    for row in rows:
       db_tree.insert("",tkinter.END,values=row)



# Designing window for registration

def register():
    global register_screen
    register_screen = Toplevel()
    register_screen.title("Register")
    register_screen.geometry("300x300")

    global username
    global password
    global access
    global username_entry
    global password_entry
    access = IntVar()
    username = StringVar()
    password = StringVar()

    Label(register_screen, text="Please enter details below").pack()
    Label(register_screen, text="").pack()

    username_label = Label(register_screen, text="Username * ")
    username_label.pack()
    username_entry = Entry(register_screen, textvariable=username)
    username_entry.pack()
    password_label = Label(register_screen, text="Password * ")
    password_label.pack()
    password_entry = Entry(register_screen, textvariable=password, show='*')
    password_entry.pack()

    access_label = Label(register_screen, text="Access scale (0 = Normal user , 1 = Admin)")
    access_label.pack()
    access_scale = Scale(register_screen, from_=0, to=1, tickinterval=1, variable=access, orient=HORIZONTAL, showvalue=0)
    access_scale.pack()

    Label(register_screen, text="").pack()
    Button(register_screen, text="Register", width=10, height=1, command=register_user).pack()
    


# Implementing event on register button

def register_user():
    username_info = username.get()
    password_info = password.get()
    access_info   = access.get()

    #--------------------------added by alfred----------------------
    #---------search query-----------
    reg_creds = (username_info,password_info,access_info)
    sql_create_user = ''' INSERT INTO login(name,password,access)
                            VALUES(?,?,?) '''

    c = db.cursor()
    c.execute(sql_create_user,reg_creds)
    db.commit()
    #-----------------------end of added by alfred---------------------


    username_entry.delete(0, END)
    password_entry.delete(0, END)

    Label(register_screen, text="Registration Success", fg="green", font=("calibri", 11)).pack()
    fetch_all()	#refresh db table



# Designing window for deleting users
def del_user_screen():
    global delete_screen
    delete_screen = Toplevel()
    delete_screen.title("Delete user")
    delete_screen.geometry("300x200")

    #get number of users from the database
    c = db.cursor()
    c.execute("SELECT * FROM login")
    records = c.fetchall()
    
    usr_cnt = len(records)
    print(usr_cnt)

  
    global id_option
    global id_menu
    global login_id

    id_option = StringVar()

    #retrieving IDs
    sql_get_ID = "SELECT id FROM login;"
    c = db.cursor()
    c.execute(sql_get_ID)
    records = c.fetchall()

    #initiate list to remove extra column
    id_option_list = []

    #removing extra column from records
    for row in records:
       id_option_list.append(str(row[0]))

    
    #Comment out for debugging
    #print("Raw IDs:")
    #print(records)
    #print("Filtered")
    #print(id_option_list)
    

    id_label = Label(delete_screen, text="Choose ID of user to be deleted")
    id_label.pack()

    id_menu = OptionMenu(delete_screen, id_option, *id_option_list)
    id_menu.pack()

    Label(delete_screen, text="").pack()
    Button(delete_screen, text="Delete user", width=10, height=1, command=delete_user).pack()

# Implementing event on delete user button
def delete_user():
    del_id = int(id_option.get()) #Converting chosen option to integer
    if(del_id == login_id):
       tkinter.messagebox.showerror("ERROR!", "Cannot delete current user")  #Throw error if user attempts to delete themselves
    else:
       c = db.cursor()
       c.execute(f"DELETE FROM login WHERE id={del_id}")
       db.commit()	#commit deletion
       fetch_all()
       
    delete_screen.destroy()




# Implementing event on login button
def login_verify():
    username1 = username_verify.get()
    password1 = password_verify.get()
    username_login_entry.delete(0, END)
    password_login_entry.delete(0, END)

    
    #--------------------------added by alfred----------------------
    #---------search query-----------
    login_creds = (username1,password1)
    sql_login_verify = "SELECT id, access FROM login WHERE name=? AND password=?;"
    c = db.cursor()
    c.execute(sql_login_verify,login_creds)
    records = c.fetchall()

    global login_status
    global login_access
    global login_id
    #check rows returned by query to see if theres a match
    if len(records) != 0:
       login_status = 1		#record login success
       login_id = records[0][0]	#record login id
       login_access = records[0][1]	#record login access credential
       close_login_screens()       
    else:
       login_status = 0      #login unsuccessful
       login_not_found() 
       
    #-----------------------end of added by alfred---------------------


#Designing popup for user not found

def login_not_found():
    global login_not_found_screen
    login_not_found_screen = Toplevel()
    login_not_found_screen.title("Success")
    login_not_found_screen.geometry("150x100")
    Label(login_not_found_screen, text="User Not Found").pack()
    Button(login_not_found_screen, text="OK", command=delete_login_not_found_screen).pack()


# Closing Login screens and proceeding to next part of the program

def close_login_screens():
    main_login_screen.destroy()



def delete_login_not_found_screen():
    login_not_found_screen.destroy()


# Designing main login window
def start_login_screen():

    global main_login_screen
    main_login_screen = Tk()
    main_login_screen.geometry("600x500")
    main_login_screen.title("Login")
    Label(main_login_screen, text="Please enter details below to login").pack()
    Label(main_login_screen, text="").pack()

    global username_verify
    global password_verify

    username_verify = StringVar()
    password_verify = StringVar()

    global username_login_entry
    global password_login_entry

    Label(main_login_screen, text="Username * ").pack()
    username_login_entry = Entry(main_login_screen, textvariable=username_verify)
    username_login_entry.pack()
    Label(main_login_screen, text="").pack()
    Label(main_login_screen, text="Password * ").pack()
    password_login_entry = Entry(main_login_screen, textvariable=password_verify, show='*')
    password_login_entry.pack()
    Label(main_login_screen, text="").pack()
    Button(main_login_screen, text="Login", width=10, height=1, command=login_verify).pack()


    
    main_login_screen.mainloop()





#------------------------------END OF FXNS FOR US-1-------------------------

#------------------------------START OF FXNS FOR US-2-------------------------

# Home dashboard loop (Main meat of the program)
def home_dashboard():
    global home_dash   #Main window
    global img_label	#Label where we're going to put the live feed of the webcamera

    

    global cam		#Camera variable for webcam feed
    cam = cv2.VideoCapture(0)

    #CV setup for human detection
    global HOGCV	#HOG for detecting humans in a frame
    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())



    
    global detect	#initialize flag to start human detection with HOG
    detect = 0

    home_dash = Tk()
    home_dash.geometry("800x500")
    home_dash.title("Home Dashboard")

    
    p0 = PanedWindow()
    p0.pack(fill=BOTH,expand=1)
 
    #Left pane should contain buttons for interface
    p1 = PanedWindow(p0,orient=VERTICAL)    
    p0.add(p1)

    #adding items to left pane
    view_db = Button(p1,text="View database", width=10,height=1,command=view_db_screen)         #Will open the Database viewer
    p1.add(view_db)

    #Buttons for starting and stoping detection
    detect_on = Button(p1,text="Start Detection",width=10,height=1,command= start_detect) #Will start the people detection
    detect_off = Button(p1,text="Stop Detection",width=10,height=1,command= stop_detect) #Will start the people detection
    p1.add(detect_on)
    p1.add(detect_off)

    global status_label
    global person
    person = 1

    global status_str
    global thresh_int
    global thresh_scale
    status_str = "Not detecting"
    thresh_int = IntVar()
    status_label = Label(p1,text=f"Status: {status_str}\n\nPersons detected: {person-1}\n\n",anchor='w' )
    thresh_label = Label(p1, text="Detection threshold")
    blank_label  = Label(p1, text="")

    thresh_scale = Scale(p1, from_=0, to=9, tickinterval=1, variable=thresh_int, orient=HORIZONTAL, showvalue=0)
    p1.add(blank_label)
    p1.add(status_label)
    p1.add(thresh_label)
    p1.add(thresh_scale)
    
    thresh_scale.set(10)

    
    #Right pane should be the live feed of the camera
    p2 = PanedWindow(p0,orient=VERTICAL)
    p0.add(p2)

    #adding items to right pane
    feed_label = Label(p2,text="Live webcam feed")
    img_label = Label(p2)
    img_label.pack()
    p2.add(feed_label)
    p2.add(img_label)

    #Start streaming and updating process
    show_livefeed()

    home_dash.mainloop()
    

#------------------------------END OF FXNS FOR US-2-------------------------

#------------------------------END OF FXNS FOR US-4-------------------------

#Updates label that contains the image of webcam
def show_livefeed():
    check, frame = cam.read()

    if check:
      
      #check if detect option is on
      if(detect):
         new_frame = detect_humans(frame)					#Generate new frame with overlay
         cv2_img = cv2.cvtColor(new_frame,cv2.COLOR_BGR2RGBA)  	#Count Humans if detect option is asserted
      else:
         cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)         	#Just convert frame to rgb

      img = ImageTk.PhotoImage(Image.fromarray(cv2_img))
      img_label.imgtk = img
      img_label.configure(image=img)
      img_label.after(10,show_livefeed)


#Asserts detect flag
def start_detect():
   global detect
   global status_str
   status_str = "Detecting"
   detect = 1
   print("start detecting")
   update_status_lbl()		#update status label
   
   global t_breach             #instantiate time counter since last breach in threshold
   t_breach = 0 

#De-asserts detect flag
def stop_detect():
   global detect
   global status_str
   status_str = "Stand by"
   detect = 0
   print("stop detecting")
   update_status_lbl()		#update status label
   
   global t_breach             #reset time since last breach in threshold
   t_breach = 0 

#Detect humans in frame and overlay tracking boxes
def detect_humans(frame):

     # resizing for faster detection
    frame = cv2.resize(frame, (640, 480))

    bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
    #bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4))
    
    global person
    person = 1
    for x,y,w,h in bounding_box_cordinates:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(frame, f'person {person}', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        person += 1

    #for testing the threshold limit for people allowable in the establishment then uncomment line below
    person = 4

    #get current set threshold
    limit = thresh_scale.get()
   
    if((person-1) > limit):
       cv2.putText(frame, f'Total Persons : {person-1}', (400,30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0,0,255), 2)
       cv2.putText(frame, 'DANGER', (400,60), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0,0,255), 2)

       global t_breach
       #Log the breach if its a minute from the last recorded breach
       if(t_breach == 0):                         #no breach has been recorded so counting should begin
          t_breach = time.time()   
          logging.warning(f'Thr: {limit} Cnt: {person-1}.')
       elif( (time.time() - t_breach) >  1):  #record a new breach since its already been a minute
          t_breach = 0
          logging.warning(f'Thr: {limit} Cnt: {person-1}.')   

    else:
       cv2.putText(frame, f'Total Persons : {person-1}', (400,30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,255,255), 2)
       cv2.putText(frame, 'SAFE', (400,60), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0,255,0), 2)

    update_status_lbl()		#update status label

    return frame

def update_status_lbl():
    #Update tracking status
    status_label.config(text=f"Status: {status_str}\n\nPersons Detected: {person-1}" , anchor = 'w')
#------------------------------START OF FXNS FOR US-4-------------------------






# Main application loop (solves login issues)
def main_app():
    setup_db()  #connect to database and/or initialize tables

    global login_status
    global login_id
    global login_access

    login_status = 0  #login status variable originally 0 (will be changed in login functions)
    login_id     = 0  #login id to avoid deleting own credentials in the db
    login_access = 0  #login access for security


    logging.basicConfig(filename='records.log',filemode='w',format='%(asctime)s %(message)s')

    start_login_screen()  
    
    if (login_status == 1):
       #If login screen succeeds then proceed to home dashboard
       home_dashboard()
    else:
       print("login failed")

    close_db()

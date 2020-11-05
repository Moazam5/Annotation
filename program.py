# References: https://www.sqlitetutorial.net/sqlite-python/create-tables/

import sqlite3
from sqlite3 import Error
import csv

#Read the text file from
#Param: text file with the ids on new line
#Return: Array with all the file names
def get_user_list(file_name):
    #Store the file names in file_list
    file_list = []
    try:
        
        file = open(file_name, "r")
    except: 
        print("Error reading the file, check if it exists and the file name is spelled correctly")
   
    #Iterate over file object
    for x in file:
        file_name = x.strip()
        file_list.append(file_name)
    print(file_list)    
    return file_list

    




#Param db_file: the database file 
#Returns connection or None
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as error:
        print(error)

    return conn



def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    Param1 conn: Connection object
    Param2 create_table_sql: a CREATE TABLE statement
    Return:
    """
    try:
        #Make cursor object which is used to execute SQL statements
        db_cursor = conn.cursor()
        db_cursor.execute(create_table_sql)
    except Error as error:
        print(error)
        
def drop_table(cursor, table_name):
    
    drop_sql = "DROP TABLE IF EXISTS {}".format(table_name)
    cursor.execute(drop_sql)
        
        
#Write data in the Event_info table
#Param1 : Connection to db
#Param2 : CSV File with the event details       
def create_events_table(conn, file_name):

    db_cursor = conn.cursor()
    with open(file_name, "r") as eventFile:
        reader = csv.DictReader(eventFile)
        
    
        #Write data to db, write event id as int
        for row in reader:
            if row["Event ID"] == "":
                continue
            else:
                id = int(row["Event ID"])

                db_cursor.execute("INSERT INTO Event VALUES (?,?,?)",
                                  (id, row["Event Name"].lower(), row["Event Alias"].lower()))
        
        conn.commit()
        
    
#Parse a string and return the first number in the sting, use this to read the trial number    
#Param : String input
#Return: Fist Int in the string 
def get_trial_number(string):
    trialNumber =  [int(s) for s in string.split() if s.isdigit()]
    return trialNumber[0]

def getEventID(string):
    with open("Events.csv", "r") as file:
        eventReader = csv.DictReader(file)
    
        for r in eventReader:
            r["Event Name"] = r["Event Name"].lower()
            r["Event Alias"] =  r["Event Alias"].lower()
            if string == r["Event Name"] or string == r["Event Alias"]:
                id = r["Event ID"]
                return id



def create_subject_table(db_cursor,file_name):
   
    db = sqlite3.connect("annotationDB.db")
    cur = db.cursor()
    with open(file_name, "r") as dataFile:
        #Read user data
        reader = csv.DictReader(dataFile)
        
      
            
        #num_event will be useful to count the number of events ocured and make unique id
        num_event = 0
        for row in reader:
            
            #read columns
            user_id_row = row["\ufeffSubject ID"].strip()
            session_row = row["Day (Session)"]
            type_row = row["Type of Trial"]
            trial_row = row["Trials"]
            date_row = row["Date of Session"]
            
            #store events as different items in a list
            event_row = row['Events of Interest'].lower()
            event_list = event_row.split(',')
          
            #Check for empty rows, use old value if found empty
            #---------This can break if initial rows are empty-------
            if row["Events of Interest"].strip() == "":  #fix for first row empty
                continue
            if session_row != "":
                ses_no = int(session_row)
            if type_row != "":
                trial_type = type_row
            if trial_row != "":
                trial_no = get_trial_number(trial_row)
                num_event = 0
            if user_id_row.strip() != "" :
                id = int(user_id_row)
            if date_row != "":
                date = date_row
            
                     
         #   put data in database here
            for i in event_list:
                occured_event_id = str(id)  + "_" + str(ses_no) + "_"+ str(trial_no) + "_"+ str(num_event)
                #to remove white space
                i = i.strip() 
                
                        
                # Here i is the event string
                event_id = getEventID(i)
                cur.execute("INSERT INTO Trial_Info VALUES  (?,?,?,?,?,?,?)",
                                  (occured_event_id, trial_no, i, row["Start Time"], 
                                    row["End Time"], row["Notes"], event_id))
                cur.execute("INSERT INTO Subject_Info VALUES (?,?,?,?,?)", (id, ses_no, date,trial_type, occured_event_id ))
                num_event += 1
            db.commit()


        
 
def main():
        
    subject_info_table = """ 
            CREATE TABLE IF NOT EXISTS Subject_Info (
                subject_id integer NOT NULL,
                session_no integer NOT NULL,
                session_date text NOT NULL,
                trial_type text NOT NULL,
                occurred_event_id text NOT NULL,
                FOREIGN KEY (occurred_event_id)
                REFERENCES Trial_Info (id)
                
                );
            """
    trial_info_table = """
        CREATE TABLE IF NOT EXISTS  Trial_Info(
            id TEXT PRIMARY KEY, 
            trial_number TEXT NOT NULL,
            event TEXT NOT NULL,
            event_start_time TEXT NOT NULL,
            event_end_time TEXT NOT NULL,
            event_notes TEXT,
            event_id TEXT,
            FOREIGN KEY(event_id) 
            REFERENCES Event(id)
            
        );"""
            
            
    event_table = """
        CREATE TABLE IF NOT EXISTS Event(
            id INT(3) PRIMARY KEY,
            name TEXT NOT NULL,
            alias TEXT
            );
    """
            
            
    
    #Create database connection and a cursor to execute sql statements
    database = "annotationDB.db"
    db = create_connection(database)
    db_cursor = db.cursor()
    
    #Delete old tables to avoid overwriting data
    drop_table(db_cursor, "Event")
    drop_table(db_cursor, "Trial_Info")
    drop_table(db_cursor, "Subject_Info")

        
    #create new table 
    if db is not None:
        create_table(db, event_table)
        create_table(db, subject_info_table)
        create_table(db, trial_info_table)
        
        
    
    #Get the list of user id's
    list = get_user_list("UserList.txt")
    #Fill in events table
    create_events_table(db,"Events.csv")

    for fileName in list:
        if fileName != "":
            print("Reading Excel Files/", fileName)
            create_subject_table(db_cursor, "Excel Files/{}".format(fileName))

        
        
if __name__ == "__main__":
    main()
    print("Successfully created Database")
    
        
        
        
        
        
        
        
        
        

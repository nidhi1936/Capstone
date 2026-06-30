import sqlite3

def get_connection():
    """Establishes connection to the SQLite database file."""
    # Creates 'job_application.db' automatically if it does not exist
    return sqlite3.connect("job_application.db")

#checks username password and if the user does not exist it adds user in db
def checkUsername(username:str,password:str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users where username=?",(username,))
        row = cursor.fetchall()
        if len(row)>0:
            if password==row[0][2]:
                return {"message":"Login_Successful","id":row[0][0]}
            else:
                return {"message":"password_incorrect","id":-1}
        else:
            try:
                cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password,))
                conn.commit()
                cursor.execute("SELECT ID FROM USERS WHERE USERNAME=?",(username,))
                row=cursor.fetchall()
                return {"message":"Login_Successful","id":row[0][0]}
            except sqlite3.IntegrityError:
                return {"message":"User exist","id":row[0][0]}

#inserts the details of the job_description
def insertDetails(details:{}):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO roles (user_id,job_title,company,job_description,resume) VALUES (?,?,?,?,?)",(details["user_id"],details["job_title"],details["company"],details["job_description"],details["resume"],))
            conn.commit()
            cursor.execute("SELECT ID FROM roles WHERE user_id=? and job_title=?",(details["user_id"],details["job_title"],))
            row=cursor.fetchall()
            cursor.execute("INSERT INTO drafts(role_id,resume_rewrite,cover_letter,interview_qa) VALUES (?,?,?,?)",(row[0][0],details["resume_rewrite"],details["cover_letter"],details["mock_interview"],))
            return {"message":"done","id":row[0][0]}
        except sqlite3.IntegrityError:
            return {"message":"error in insertion","id":row[0][0]}

#deletes data from roles and drafts table
def deleteRolesDrafts():
     with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM ROLES")
            #cursor.execute("DELETE FROM sqlite_sequence WHERE name='ROLES'")
            conn.commit()
            cursor.execute("DELETE FROM DRAFTS")
            #cursor.execute("DELETE FROM sqlite_sequence WHERE name='DRAFTS'")
            conn.commit()
        except sqlite3.IntegrityError:
            return {"message":"error in DELETION"}

#deleteRolesDrafts()
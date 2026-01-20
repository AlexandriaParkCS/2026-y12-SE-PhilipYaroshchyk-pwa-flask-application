from sqldb import SqlDb
import bcrypt
import sqlite3


# business logic related to user account here
class UserService:

    def __init__(self, db: SqlDb):
        self.db = db
        # self.salt = bcrypt.gensalt()
        self.salt = b'$2b$12$pXlzeoRw6XKXNyBbufFrYu'

    # checks if user exists. if does not exist, creates a new users saving username, 
    # email and hashed password
    def signup(self, username, email, password):
        print(f"signing up new user: {username}, {email}")
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), self.salt)
            self.db.create_user(username, email, password_hash)
        except sqlite3.IntegrityError:
            return False
        return True
    

    def login(self, username, password):
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), self.salt)
            user = self.db.get_user_by_username(username)
            if user:
                if user["password_hash"] == password_hash:
                    return user
                else:
                    print("password incorrect")
                    return None
        except sqlite3.IntegrityError:
            print(f"database error, failed to login user {username}")        
            return None
        

    def add_expense(self, user_id, expense_type, amount, description):
        try:
            expense = self.db.create_expense(user_id, expense_type, amount, description)
            if expense:
                print(f"expense created {expense['id']}")
            return expense 
        except Exception as e:
            print(f"failed to add expense {e}")
            return None

               



            



        

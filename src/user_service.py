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
            return self.db.create_user(username, email, password_hash)
        except sqlite3.IntegrityError:
            return None
    

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
        

    def add_transaction(self, user_id, transaction_type, amount: float, date, description):
        try:
            expense = self.db.create_transaction(user_id, transaction_type, amount, date, description)
            if expense:
                print(f"expense created {expense['id']}")
            return expense 
        except Exception as e:
            print(f"failed to add transaction {e}")
            return None
        
    def get_all_user_transactions(self, user_id):
        try:
            expenses = self.db.get_all_user_transactions(user_id)
            if expenses:
                print("expenses fetched OK")
                print(expenses)
                return expenses     
        except Exception as e:
            print(f"failed to add transaction {e}")
            return None
        
    def add_goal(self, user_id, amount: float, goal_name, start_date, end_date, parent_goal_id=None):
        try:
            goal = self.db.create_goal(user_id, amount, goal_name, start_date, end_date, parent_goal_id)
            if goal:
                print(f"goal created {goal['id']}")
            return goal 
        except Exception as e:
            print(f"failed to add goal {e}")
            return None
               



            



        

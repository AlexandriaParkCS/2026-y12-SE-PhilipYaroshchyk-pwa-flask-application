from sqldb import SqlDb
import bcrypt
import sqlite3

from model.transaction import Transaction
from model.goal import Goal
from model.summary import Summary


# business logic related to user account here
class UserService:

    def __init__(self, db: SqlDb, log):
        self.db = db
        self.log = log
       
    # checks if user exists. if does not exist, creates a new users saving username, 
    # email and hashed password
    def signup(self, username, email, password):
        self.log.info(f"signing up new user: {username}, {email}")
        password_salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), password_salt)
        return self.db.create_user(username, email, password_hash, password_salt)
    

    def login(self, username, password):
        try:

            user = self.db.get_user_by_username(username)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), user["password_salt"])
    
            if user:
                if user["password_hash"] == password_hash:
                    return user
                else:
                    self.log.info("password incorrect")
                    raise Exception("password incorrect")
        except sqlite3.IntegrityError as e:
            self.log.info(f"database error, failed to login user {username}")        
            raise e
        

    def add_transaction(self, user_id, transaction_type, amount_dollars: float, date, description, exp_type):
        try:

            amount = int(round(float(amount_dollars) * 100))  # convert to cents

            if exp_type == "Expense":
                amount = -amount   

            expense = self.db.create_transaction(user_id, transaction_type, amount, date, description)
            if expense:
                self.log.info(f"expense created {expense['id']}")
            return expense 
        except Exception as e:
            raise e
        
    def add_goal(self, user_id, amount_dollars: float, goal_name, start_date, end_date, parent_goal_id=None):
        try:
            amount = int(round(float(amount_dollars) * 100))  # convert to cents
            goal = self.db.create_goal(user_id, amount, goal_name, start_date, end_date, parent_goal_id)
            if goal:
                self.log.info(f"goal created {goal['id']}")
            return goal 
        except Exception as e:
            self.log.info(f"failed to add goal {e}")
            raise e
        

    def get_user_goals(self, id):
        try:
            goals = self.db.get_user_goals(id)
            for g in goals:
                g.amount = (g.amount / 100) # convert to dollars for display

            return goals
        except Exception as e:
            self.log.info(f"failed to fetch goals {e}")
            raise e    
        

    def get_user_transactions(self, id, limit, is_expense):    
        try:
            transactions = self.db.get_user_transactions(id, limit, is_expense)
            for tr in transactions:
                tr.amount = tr.amount / 100 # convert to dollars for display    
            return transactions
        except Exception as e:
            self.log.info(f"failed to fetch transaction {e}")
            raise e    
               
    def get_transaction_summary_for_a_goal(self, user_id, goal_id):

        try:   
            transactions = self.db.get_user_transactions_for_goal(user_id, goal_id) 
            goal = self.db.get_goal_by_id(user_id, goal_id)
            goal.amount = goal.amount / 100 # convert to dollars for display
            aggregations = self.db.get_aggretated_user_expenses_for_goal(user_id, goal_id)


            total_amount = 0
            for transaction in transactions:
                transaction.amount = transaction.amount / 100 # convert to dollars for display
                total_amount += transaction.amount


            tip = f"Your total expenses for this goal is ${total_amount}. You have ${goal.amount - total_amount} left to save to reach your goal of ${goal.amount}"    

            return Summary(total_amount, goal, transactions, aggregations, tip)
        except Exception as e:
            self.log.info(f"failed to fetch transaction summary for goal {goal_id} {e}")
            raise e

    def get_all_user_transactions(self, user_id):
        
        try: 
            transactions = self.db.get_all_user_transactions(user_id) 
            for tr in transactions:
                tr.amount = tr.amount / 100 # convert to dollars for display

            return transactions
        
        except Exception as e:
            self.log.info(f"failed to fetch all expenses for user {user_id} {e}")
            raise e
            

            



        

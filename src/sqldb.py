import sqlite3
from model.transaction import Transaction
from model.goal import Goal
from model.aggregation import Aggregation

class SqlDb(object):

    def __init__(self, db_path="db/app.db", log: object = None):
        self.db_path = db_path
        self._create_tables()
        self.log = log

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("""BEGIN""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL)
            """)

            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                transaction_date TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)           
                ) 
            """)


            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,        
                goal_name TEXT NOT NULL,
                start_date TEXT NOT NULL, 
                end_date TEXT NOT NULL,
                created_date TEXT NOT NULL,
                updated_date TEXT,
                           
                parent_goal_id INTEGER,           
                FOREIGN KEY (user_id) REFERENCES users(id), 
                FOREIGN KEY (parent_goal_id) REFERENCES goals(id) 
                )
           """)

            conn.commit()
        except sqlite3.Error as e:
            self.log.info(f"Error creating table: {e}")
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def create_user(self, username, email, hash, salt):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, password_salt) VALUES (?, ?, ?, ?)",
                (username, email, hash, salt)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "username": username, "email": email}
        except sqlite3.IntegrityError:
            self.log.info("Error: Username or email already exists.")
            # return error
            raise
        except sqlite3.Error as e:
            self.log.info(f"Database error during user creation: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def get_user_by_username(self, username):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email, password_hash, password_salt FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3], "password_salt": row[4]}
            else:
                return None
            
        except sqlite3.Error as e:
            self.log.info(f"Database error during user retrieval: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def update_user_email(self, username, new_email):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET email = ? WHERE username = ?",
                (new_email, username)
            )
            conn.commit()
            if cursor.rowcount:
                return self.get_user_by_username(username)
            else:
                self.log.info("User not found.")
        except sqlite3.IntegrityError:
            self.log.info("Error: Email already in use.")
        except sqlite3.Error as e:
            self.log.info(f"Database error during update: {e}")
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def delete_user(self, username):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM users WHERE username = ?",
                (username,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.log.info(f"Database error during deletion: {e}")
            return False
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()




    def create_transaction(self, user_id, transaction_type, amount, transaction_date, description):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transactions (user_id, transaction_type, amount, transaction_date, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, transaction_type, amount, transaction_date, description)
            )
            conn.commit()
            expense_id = cursor.lastrowid
            return {"id": expense_id}
        except sqlite3.IntegrityError:
            self.log.info("Error: Failed to create transaction.")
            # return error
            raise
        except sqlite3.Error as e:
            self.log.info(f"Database error during transaction creation: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def create_goal(self, user_id, amount, goal_name, start_date, end_date, parent_goal_id=None):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO goals (user_id, amount, goal_name, start_date, end_date, created_date, parent_goal_id) VALUES (?, ?, ?, ?, ?, datetime('now'), ?)",
                (user_id, amount, goal_name, start_date, end_date, parent_goal_id)
            )
            conn.commit()
            goal_id = cursor.lastrowid
            return {"id": goal_id}
        except sqlite3.IntegrityError:
            self.log.info("Error: Failed to create goal.")
            # return error
            raise
        except sqlite3.Error as e:
            self.log.info(f"Database error during goal creation: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def get_user_transactions(self, user_id, limit, is_expense):

        query = None
        if is_expense:
            query = "SELECT id, user_id, transaction_type, amount, transaction_date, description FROM transactions WHERE user_id = ? AND amount < 0 ORDER BY transaction_date DESC LIMIT ?"
        else:       
            query = "SELECT id, user_id, transaction_type, amount, transaction_date, description FROM transactions WHERE user_id = ? AND amount >= 0 ORDER BY transaction_date DESC LIMIT ?"

        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
            list = []

            if rows:
                for row in rows:
                    transaction = Transaction(id=row[0], user_id=row[1], transaction_type=row[2], amount=row[3], transaction_date=row[4], description=row[5])
                    list.append(transaction)
                return list    
            else:
                return list
        except Exception as e:
            self.log.info(f"Database error during transactions retrieval: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()


    def get_user_goals(self, user_id):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, amount, goal_name, start_date, end_date, created_date, updated_date, parent_goal_id FROM goals WHERE user_id = ? ORDER BY created_date DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            list = []

            if rows:
                for row in rows:
                    goal = Goal(id=row[0], user_id=row[1], amount=row[2], goal_name=row[3], start_date=row[4], end_date=row[5], created_date=row[6], updated_date=row[7], parent_goal_id=row[8])
                    list.append(goal)
                return list    
            else:
                return list
        except Exception as e:
            self.log.info(f"Database error during goals retrieval: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()       


    def get_all_user_transactions(self, user_id):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_id, transaction_type, amount, transaction_date, description FROM transactions WHERE user_id = ? ORDER BY transaction_date DESC", 
                           (user_id,))
            rows = cursor.fetchall()
            list = []
            for r in rows:
                transaction = Transaction(id=r[0], user_id=r[1], transaction_type=r[2], amount=r[3], transaction_date=r[4], description=r[5]) 
                list.append(transaction)
            return list
        
        except Exception as e:
            self.log.info(f"Database error during expenses retrieval: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()       



    def get_goal_by_id(self, user_id, goal_id):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, amount, goal_name, start_date, end_date, created_date, updated_date, parent_goal_id FROM goals WHERE user_id = ? AND id = ?",
                (user_id, goal_id)
            )
            result = cursor.fetchone()
            if result:
                return Goal(id=result[0], user_id=result[1], amount=result[2], goal_name=result[3], start_date=result[4], end_date=result[5], created_date=result[6], updated_date=result[7], parent_goal_id=result[8])
            else:
                return None
        except Exception as e:
            self.log.info(f"Database error during goal retrieval: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()               


    def get_aggretated_user_expenses_for_goal(self, user_id, goal_id):
        conn = None
        cursor = None

        self.log.info(f"fetching aggregated expenses for user_id={user_id} goal_id={goal_id}")
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT t.transaction_type, SUM(t.amount) FROM transactions AS t INNER JOIN goals AS g ON t.user_id = g.user_id WHERE t.user_id = ? and g.id = ? AND t.transaction_date >= g.start_date AND t.transaction_date <= g.end_date AND t.amount < 0 GROUP BY t.transaction_type", (user_id, goal_id)
            )
            rows = cursor.fetchall()
            list = []

            if rows:
                for row in rows:
                    aggregation = Aggregation(name=row[0], amount=row[1])
                    list.append(aggregation)
                return list    
            else:
                return list

        except Exception as e:
            self.log.info(f"Database error during transactions retrieval for a goal: {e}")
            raise 
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()         

    def get_user_transactions_for_goal(self, user_id, goal_id): 
        conn = None
        cursor = None

        self.log.info(f"fetching transactions for user_id={user_id} goal_id={goal_id}")

        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT t.id, t.user_id, t.transaction_type, t.amount, t.transaction_date, t.description FROM transactions AS t INNER JOIN goals AS g ON t.user_id = g.user_id WHERE t.user_id = ? and g.id = ? AND t.transaction_date >= g.start_date AND t.transaction_date <= g.end_date ORDER BY t.transaction_date ASC", (user_id, goal_id)
            )
            rows = cursor.fetchall()
            transaction_list = []
            if rows:
                for row in rows:
                    transaction = Transaction(id=row[0], user_id=row[1], transaction_type=row[2], amount=row[3], transaction_date=row[4], description=row[5])
                    transaction_list.append(transaction)
                return transaction_list    
            else:
                return transaction_list


        except Exception as e:
            self.log.info(f"Database error during transactions retrieval for a goal: {e}")
            raise 
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()     


    def get_user_transaction_for_date_range(self, user_id, from_date, to_date):
        conn = None
        cursor = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, transaction_type, amount, transaction_date, description FROM transactions WHERE user_id = ? AND transaction_date >= ? AND transaction_date <= ? ORDER BY transaction_date DESC",
                (user_id, from_date, to_date)
            )
            rows = cursor.fetchall()
            transaction_list = []

            if rows:
                for row in rows:
                    transaction = Transaction(id=row[0], user_id=row[1], transaction_type=row[2], amount=row[3], transaction_date=row[4], description=row[5])
                    list.append(transaction)
                return transaction_list    
            else:
                return transaction_list


            
        except Exception as e:
            self.log.info(f"Database error during transactions retrieval for date range: {e}")
            raise 
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()     


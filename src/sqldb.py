import sqlite3

class SqlDb(object):

    def __init__(self, db_path="db/app.db"):
        self.db_path = db_path
        self._create_tables()

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
                password_hash TEXT NOT NULL)
            """)

            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER NOT NULL,
                expense_type TEXT NOT NULL,
                amount FLOAT NOT NULL,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)           
                ) 
            """)


            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()

    def create_user(self, username, email, hash):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "username": username, "email": email}
        except sqlite3.IntegrityError:
            print("Error: Username or email already exists.")
            # return error
            raise
        except sqlite3.Error as e:
            print(f"Database error during user creation: {e}")
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
                "SELECT id, username, email, password_hash FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]}
            else:
                return None
            
        except sqlite3.Error as e:
            print(f"Database error during user retrieval: {e}")
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
                print("User not found.")
        except sqlite3.IntegrityError:
            print("Error: Email already in use.")
        except sqlite3.Error as e:
            print(f"Database error during update: {e}")
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
            print(f"Database error during deletion: {e}")
            return False
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()




    def create_expense(self, user_id, expense_type, amount, description):
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (user_id, expense_type, amount, description) VALUES (?, ?, ?, ?)",
                (user_id, expense_type, amount, description)
            )
            conn.commit()
            expense_id = cursor.lastrowid
            return {"id": expense_id}
        except sqlite3.IntegrityError:
            print("Error: Failed to create expense.")
            # return error
            raise
        except sqlite3.Error as e:
            print(f"Database error during expense creation: {e}")
            raise
        finally:
            if cursor: 
                cursor.close()
            if conn: 
                conn.close()
             

# Example usage
if __name__ == "__main__":
    db = SqlDb("db/sql.db")

    # Create
    user = db.create_user("emiltech", "emil@example.com")
    print("Created:", user)

    # Read
    user = db.get_user_by_username("emiltech")
    print("Retrieved:", user)

    # Update
    updated_user = db.update_user_email("emiltech", "emil_updated@example.com")
    print("Updated:", updated_user)

    # Delete
    success = db.delete_user("emiltech")
    print("Deleted:", success)
    

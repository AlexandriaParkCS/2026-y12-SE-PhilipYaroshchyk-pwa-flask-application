class User:
    def __init__ (self, id, username, email, password_hash):
        self._id = id
        self._username = username
        self._email = email
        self._password_hash = password_hash

    def get_id(self):   
        return self._id
    def get_username(self):
        return self._username
    def get_email(self):
        return self._email
    def get_password_hash(self):
        return self._password_hash

    def set_id(self, id):
        self._id = id
    def set_username(self, username):
        self._username = username
    def set_email(self, email):
        self._email = email
    def set_password_hash(self, password_hash):
        self._password_hash = password_hash                 

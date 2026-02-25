class Transation:
    # id, user_id, transaction_type, amount, transaction_date, description

    def __init__(self, id, user_id, transaction_type, amount, transaction_date, description):
        self._id = id
        self._user_id = user_id
        self._transaction_type = transaction_type
        self._amount = amount
        self._transaction_date = transaction_date
        self._description = description

    def get_id(self):
        return self._id
    def get_user_id(self):
        return self._user_id
    def get_transaction_type(self):
        return self._transaction_type
    def get_amount(self):
        return self._amount
    def get_transaction_date(self):
        return self._transaction_date
    def get_description(self):
        return self._description
    
    def set_id(self, id):
        self._id = id
    def set_user_id(self, user_id):
        self._user_id = user_id
    def set_transaction_type(self, transaction_type):
        self._transaction_type = transaction_type
    def set_amount(self, amount):
        self._amount = amount
    def set_transaction_date(self, transaction_date):
        self._transaction_date = transaction_date
    def set_description(self, description):
        self._description = description





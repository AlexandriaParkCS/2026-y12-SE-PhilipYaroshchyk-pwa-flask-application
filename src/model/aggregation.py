class Aggregation:
    def __init__(self, name: str, amount: float):
        self._name = name
        self._amount = amount

    def get_name(self):
        return self._name
    
    def get_amount(self):
        return self._amount
    
    def set_name(self, name):  
        self._name = name
    def set_amount(self, amount):
        self._amount = amount    
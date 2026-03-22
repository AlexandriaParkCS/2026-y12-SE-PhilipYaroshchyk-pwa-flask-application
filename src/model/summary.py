class Summary:

    def __init__(self, total, goal, transactions, aggregations):
        self._total = total
        self._goal = goal
        self._transactions = transactions
        self._aggregations = aggregations


    def get_total(self):
        return self._total
    def get_goal(self):    
        return self._goal
    def get_transactions(self):
        return self._transactions
    def get_aggregations(self):
        return self._aggregations
    
    def set_goal(self, goal):
        self._goal = goal
    def set_total(self, total): 
        self._total = total    
    def set_transactions(self, transactions):
        self._transactions = transactions
    def set_aggregations(self, aggregations):
        self._aggregations = aggregations        


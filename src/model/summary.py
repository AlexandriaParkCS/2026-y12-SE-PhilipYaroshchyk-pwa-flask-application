class Summary:

    def __init__(self, total, goal):
        self._total = total
        self._goal = goal


    def get_total(self):
        return self._total
    def get_goal(self):    
        return self._goal
    def set_goal(self, goal):
        self._goal = goal
    def set_total(self, total): 
        self._total = total    


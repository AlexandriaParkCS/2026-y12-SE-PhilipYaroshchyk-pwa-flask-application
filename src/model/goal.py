class Goal:
    def __init__ (self, id, user_id, amount, goal_name, start_date, end_date, created_date, updated_date, parent_goal_id):
        self._id = id
        self._user_id = user_id
        self._amount = amount
        self._goal_name = goal_name
        self._start_date = start_date
        self._end_date = end_date
        self._created_date = created_date
        self._updated_date = updated_date
        self._parent_goal_id = parent_goal_id

    def get_id(self):
        return self._id
    def get_user_id(self):
        return self._user_id 
    def get_amount(self):
        return self._amount
    def get_goal_name(self):
        return self._goal_name
    def get_start_date(self):
        return self._start_date
    def get_end_date(self):
        return self._end_date
    def get_created_date(self):
        return self._created_date
    def get_updated_date(self):
        return self._updated_date
    def get_parent_goal_id(self):
        return self._parent_goal_id
    
    def set_id(self, id):
        self._id = id
    def set_user_id(self, user_id):
        self._user_id = user_id
    def set_amount(self, amount):
        self._amount = amount
    def set_goal_name(self, goal_name):
        self._goal_name = goal_name
    def set_start_date(self, start_date):
        self._start_date = start_date
    def set_end_date(self, end_date):
        self._end_date = end_date
    def set_created_date(self, created_date):
        self._created_date = created_date
    def set_updated_date(self, updated_date):
        self._updated_date = updated_date
    def set_parent_goal_id(self, parent_goal_id):
        self._parent_goal_id = parent_goal_id
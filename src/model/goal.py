from dataclasses import dataclass

@dataclass
class Goal:
    id: int
    user_id: int
    amount: float
    goal_name: str
    start_date: str
    end_date: str
    created_date: str
    updated_date: str
    parent_goal_id: int
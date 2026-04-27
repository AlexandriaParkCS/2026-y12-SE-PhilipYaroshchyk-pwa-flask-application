from dataclasses import dataclass

@dataclass  
class Transaction:
    id: int
    user_id: int
    transaction_type: str
    amount: float
    transaction_date: str
    description: str
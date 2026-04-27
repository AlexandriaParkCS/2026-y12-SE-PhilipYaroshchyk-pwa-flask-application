from dataclasses import dataclass
from .goal import Goal
from .transaction import Transaction
from .aggregation import Aggregation

@dataclass 
class Summary:
    total: float
    goal: Goal
    transactions: list[Transaction]
    aggregations: list[Aggregation]
    tip: str
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    password_salt: str

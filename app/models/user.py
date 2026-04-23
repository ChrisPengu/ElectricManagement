from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class UserAccount:
    id: Optional[int]
    username: str
    password: str
    role: str
    display_name: str
    is_active: bool = True

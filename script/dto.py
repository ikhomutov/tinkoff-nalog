from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Report:
    payment_date: datetime
    company: str
    country: str
    amount: Decimal
    tax: Decimal
    currency: str
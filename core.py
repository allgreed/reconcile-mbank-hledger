from decimal import Decimal
from typing import Optional

from datetime import date
from pydantic.dataclasses import dataclass
from pydantic import PositiveInt, constr


@dataclass
class Transaction:
    amount: Decimal
    description: constr(min_length=1)


@dataclass
class MbankTransaction(Transaction):
    date: date


@dataclass
class HledgerTransaction(Transaction):
    ledger_id: PositiveInt

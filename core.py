from enum import Enum
from decimal import Decimal

from pydantic.dataclasses import dataclass
from pydantic import PositiveInt, constr


@dataclass
class Transaction:
    amount: Decimal
    description: constr(min_length=1)


@dataclass
class MbankTransaction(Transaction):
    pass


@dataclass
class HledgerTransaction(Transaction):
    ledger_id: PositiveInt

from decimal import Decimal

from datetime import date
from pydantic.dataclasses import dataclass
from pydantic import PositiveInt, constr


@dataclass(frozen=True)
class Transaction:
    amount: Decimal
    description: constr(min_length=3)


@dataclass(frozen=True)
class MbankTransaction(Transaction):
    accounting_date: date


@dataclass(frozen=True)
class HledgerTransaction(Transaction):
    ledger_id: PositiveInt

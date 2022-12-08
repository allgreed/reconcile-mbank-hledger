import dataclasses
from decimal import Decimal
from typing import Set
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


@dataclass
class TransactionsMatch:
    hledger_transactions: Set[HledgerTransaction] = dataclasses.field(default_factory=set)
    mbank_transactions: Set[MbankTransaction] = dataclasses.field(default_factory=set)

    def is_correct(self):
        import itertools
        amounts = list(map(lambda t: t.amount, itertools.chain(self.hledger_transactions, self.mbank_transactions)))
        return all(a == amounts[0] for a in amounts[1:]) 

    @property
    def is_balanced(self):
        return len(self.hledger_transactions) == len(self.mbank_transactions)

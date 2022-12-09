import dataclasses
from decimal import Decimal
from typing import Set, NewType
from datetime import date

from pydantic.dataclasses import dataclass
from pydantic import PositiveInt, constr

# this is the best I can do so far...
Currency = NewType("Currency", constr(min_length=1))

@dataclass(frozen=True)
class Transaction:
    amount: Decimal
    description: constr(min_length=3)

@dataclass(frozen=True)
class MbankTransaction(Transaction):
    accounting_date: date
    # TODO: make the types match
    currency: Currency = "PLN"


@dataclass(frozen=True)
class HledgerTransaction(Transaction):
    # TODO: well... it's not str
    currency: Currency
    ledger_id: PositiveInt
    accounting_date: date = date(2022,11,1)


@dataclass
class TransactionsMatch:
    hledger_transactions: Set[HledgerTransaction] = dataclasses.field(default_factory=set)
    mbank_transactions: Set[MbankTransaction] = dataclasses.field(default_factory=set)

    # TODO: this isn't core, it simply shouldn't be possible to create incorrect matches
    def is_correct(self):
        import itertools
        amounts = list(map(lambda t: t.amount, itertools.chain(self.hledger_transactions, self.mbank_transactions)))
        return all(a == amounts[0] for a in amounts[1:]) 

    @property
    def is_balanced(self):
        return len(self.hledger_transactions) == len(self.mbank_transactions)

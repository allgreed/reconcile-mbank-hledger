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
    # the transaction *must* originate from some kind of statement and that statement has numbered items
    item_number: int
    amount: Decimal
    description: constr(min_length=3)
    accounting_date: date
    currency: Currency


@dataclass(frozen=True)
class MbankTransaction(Transaction):
    # TODO: make the types match
    currency: Currency = "PLN"


@dataclass(frozen=True)
class HledgerTransaction(Transaction):
    # TODO: well... it's not str
    ledger_id: PositiveInt


# TODO: wtf happens with types? why is it 'set[Dataclass]' and not a proper one? o.0
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

    @property
    def contains_return(self):
        return any(t.amount > 0 for t in self.hledger_transactions)
        # TODO: and account for that is an expense account!!!

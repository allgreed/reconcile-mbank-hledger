import dataclasses
from decimal import Decimal
from typing import Set, NewType, Sequence
from collections import defaultdict
from datetime import date

from pydantic.dataclasses import dataclass
from pydantic import PositiveInt, constr

# this is the best I can do so far...
Currency = NewType("Currency", constr(min_length=1))

@dataclass(frozen=True)
class Transaction:
    amount: Decimal
    description: constr(min_length=3)
    accounting_date: date
    currency: Currency
    # sometimes you have 2 transactions with the same parameters
    # that are otherwise different transactions
    nonce: int


    def __str__(self):
        return f"{self.amount} {self.currency} on {self.accounting_date}: {self.description}"

# TODO: assign default for Currency = PLN and not do it in port
@dataclass(frozen=True)
class MbankTransaction(Transaction):
    pass


@dataclass(frozen=True)
class HledgerTransaction(Transaction):
    # TODO: well... it's not str
    ledger_id: PositiveInt

    def __str__(self):
        return f"{(super().__str__())} [{self.ledger_id}]"


@dataclass
class MatchSet:
    hledger_transactions: Set[HledgerTransaction] = dataclasses.field(default_factory=set)
    real_world_transactions: Set[Transaction] = dataclasses.field(default_factory=set)

    # TODO: this isn't core, it simply shouldn't be possible to create incorrect matches
    def is_correct(self):
        import itertools
        amounts = list(map(lambda t: t.amount, itertools.chain(self.hledger_transactions, self.real_world_transactions)))
        return all(a == amounts[0] for a in amounts[1:]) 

    @property
    def is_balanced(self):
        return len(self.hledger_transactions) == len(self.real_world_transactions)

    @property
    def contains_return(self):
        return any(t.amount > 0 for t in self.hledger_transactions)
        # TODO: and account for that is an expense account!!!


def find_unbalanced_matches(all_hledger_transactions: Sequence[HledgerTransaction], all_real_world_transactions: Sequence[Transaction]):
    matches = defaultdict(MatchSet)

    for t in all_real_world_transactions:
        matches[t.amount].hledger_transactions.add(t)

    for t in all_hledger_transactions:
        matches[t.amount].real_world_transactions.add(t)

    matches = list(matches.values())
    assert all(m.is_correct() for m in matches)

    return [m for m in matches if not m.is_balanced]

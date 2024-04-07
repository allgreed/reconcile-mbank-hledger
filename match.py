from dataclasses import dataclass
from typing import Set, Union
from core import HledgerTransaction, MbankTransaction, TransactionsMatch


@dataclass
class UnmatchedTransactionCandidate:
    transaction: Union[MbankTransaction, HledgerTransaction]
    # TODO: pydantic
    probability: float # actually between 0 and 1, how about pydantic?

# TODO: match, but with probability

# matches with probability and unmatched transaction, also with probability
def find_likely_local_balance(match: TransactionsMatch) -> ...:
    # trivial case
    if len(match.hledger_transactions) == 1 and len(match.mbank_transactions) == 0:
        return UnmatchedTransactionCandidate(transaction=match.hledger_transactions[0], probability=1.0)

    # inverse
    if len(match.hledger_transactions) == 0 and len(match.mbank_transactions) == 1:
        return UnmatchedTransactionCandidate(transaction=match.mbank_transactions[0], probability=1.0)

    return UnmatchedTransactionCandidate(transaction(match.hledger_transactions + match.mbank_transactions)[0], probability=0.0)
    # also: return set of unmatched thingies + confidence
    ...


def find_global_best_candidate(problems: Set[TransactionsMatch]) -> tuple[HledgerTransaction, MbankTransaction]:
    ...

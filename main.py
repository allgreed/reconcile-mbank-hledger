import itertools
from collections import defaultdict
from typing import Sequence

from core import HledgerTransaction, MbankTransaction
from ports import read_hledger_csv_transactions, read_mbank_transactions


# TODO: refactor to Path
def main(reconciliation_month=11, hledger_csv_statement="/tmp/sep.csv", mbank_html_statement="/home/allgreed/Downloads/bork.html"):
    with open(hledger_csv_statement) as f:
        hledger_transactions = read_hledger_csv_transactions(f)
        # assumption: reconcilement happens on monthly basis
        # TODO: assert this assumption

    with open(mbank_html_statement) as f:
        # mbank will contain slightly more data
        # export at least +2 days to get all the debit carts settlemetns!
        # TODO: assert this assumption
        mbank_transactions = [t for t in read_mbank_transactions(f) if t.accounting_date.month == reconciliation_month]

    unbalanced_matches = find_unbalanced_matches(mbank_transactions, hledger_transactions)
    assert unbalanced_matches == legacy_find_unbalanced_matches(mbank_transactions, hledger_transactions)

    if unbalanced_matches:
        ...
        # display the problem sensibly

        # TODO: pay close attention to transcation with negative expenses -> they might be insanely wrong
        # TODO: nicer way to automate reconciliment update
        # TODO: some kind of a switch for handling problems one at a time
    else:
        print("Congrats, all reconciled!")


def find_unbalanced_matches(mbank_transactions: Sequence[MbankTransaction], hledger_transactions:
        Sequence[HledgerTransaction]):
    class TransactionsMatch:
        def __init__(self):
            self.hledger_transactions = []
            self.mbank_transactions = []

        def is_correct(self):
            amounts = list(map(lambda t: t.amount, itertools.chain(self.hledger_transactions, self.mbank_transactions)))
            return all(a == amounts[0] for a in amounts[1:]) 

        @property
        def is_balanced(self):
            return len(self.hledger_transactions) == len(self.mbank_transactions)

    # constructing the matches on a 
    matches = defaultdict(TransactionsMatch)
    for t in hledger_transactions:
        matches[t.amount].hledger_transactions.append(t)
    for t in mbank_transactions:
        matches[t.amount].mbank_transactions.append(t)
    matches = list(matches.values())
    assert all(m.is_correct() for m in matches)

    return [m for m in matches if not m.is_balanced]


def legacy_find_unbalanced_matches(mbank_transactions, hledger_transactions):
    unmatchedmbank_trns = set()
    mbank_trans_by_amount = defaultdict(list)
    mbank_trns_by_id = {}
    for t in mbank_transactions:
        mbank_trans_by_amount[t.amount].append(t)
        mbank_trns_by_id[id(t)] = (t)
        unmatchedmbank_trns.add(t)

    duplicate_bleledger_trns_by_amount = defaultdict(list)
    for ht in hledger_transactions:
        corresponding_transactions = mbank_trans_by_amount[ht.amount]
        if corresponding_transactions:
            if len(corresponding_transactions) > 1:
                duplicate_bleledger_trns_by_amount[ht.amount].append(ht)
            else:
                try:
                    unmatchedmbank_trns.remove(corresponding_transactions[0])
                except KeyError:
                    # TODO: deal with double matching form hledger to mbank
                    # so: hledger has two trns with amount X, while mbank has only one with amout X
                    # print("A!", ht) 
                    pass

        else:
            # TODO: deal with those
            # print("unmatched", ht)
            pass

    # TODO: deal with this!
    for amount, cases in  duplicate_bleledger_trns_by_amount.items():
        matchz = mbank_trans_by_amount[amount]
        if len(cases) != len(matchz):
            pass
        else:
            for m in matchz:
                unmatchedmbank_trns.remove(m)    

    return sorted(unmatchedmbank_trns)


if __name__ == "__main__":
    main()

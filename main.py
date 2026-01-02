import sys
import subprocess
from collections import defaultdict
from typing import Sequence
from datetime import date, timedelta

from core import HledgerTransaction, MbankTransaction, TransactionsMatch
from ports import read_hledger_csv_transactions, read_mbank_transactions, read_revolut_csv_transactions

THE_FORMAT = "%Y-%m-%d"
# TODO: expand to reconcile more stuff, namely Revolut

# TODO: refactor to Path
# TODO: describe what is reconciliation_month
def main(reconciliation_end_date, hledger_csv_statement="/tmp/sep.csv", mbank_html_statement="/home/allgreed/Downloads/bork.html"):
    reconcilement_month = reconciliation_end_date.month

    # TODO: unhack
    read_mbank_transactions = read_revolut_csv_transactions
    mbank_html_statement = "/home/allgreed/Downloads/revo-2025.csv"

    start = reconciliation_end_date.replace(day=1).strftime(THE_FORMAT)
    end = (reconciliation_end_date + timedelta(days=1)).strftime(THE_FORMAT)
    def dump_hledger():
        subprocess.run([
            "hledger", "print", "-O", "csv", f"date:{start}-{end}",
            # TODO: skip the temp file altogether -> I can just parse on the fly by pipes :D
            "-o", "/tmp/sep.csv",
            # TODO: automate this?
            # "-f", "~/Documents/finance/old-journals/2024.journal",
        ])


    while True:
        # TODO: return heuristic
        # use: hledger register type:X "amt:<0" -O csv not:desc:"\[return\]"
        # and title does not contain "refund" / "return" / "zwrot" -> flag it!

        dump_hledger()
        with open(hledger_csv_statement) as f:
            hledger_transactions = read_hledger_csv_transactions(f)
            # TODO: assert all transations are the same currency as first transaction

        with open(mbank_html_statement) as f:
            # mbank will contain slightly more data
            # assuumption: export at least +2 days to get all the debit carts settlemetns!
            # TODO: code it!

            # TODO: assert first transaction is in PLN
            # TODO: assert all transactions have the same currency as first transaction
            # TODO: assert first transaction matches first hledger transaction
            # TODO: assert this assumption
            mbank_transactions = [t for t in read_mbank_transactions(f) if t.accounting_date.month ==
                                  reconcilement_month]

        # TODO: clean this up
        def is_reconcilment(problem):
            return len(problem.hledger_transactions) == 1 and len(problem.mbank_transactions) == 0 and next(iter(problem.hledger_transactions)).description == "Reconcilment mbank"

        def is_opening(problem):
            return len(problem.hledger_transactions) == 1 and len(problem.mbank_transactions) == 0 and next(iter(problem.hledger_transactions)).description == "opening balances"

        raw_unbalanced_matches = find_unbalanced_matches(mbank_transactions, hledger_transactions)
        unbalanced_matches = [p for p in raw_unbalanced_matches if not is_reconcilment(p) and not is_opening(p)]

        # I want to handle false-returns first, since they're easy to fix and likely cause another imbalance further
        unbalanced_matches.sort(key=lambda p: p.contains_return, reverse=True)

        # TODO: display returns first!
        while unbalanced_matches:
            problem = unbalanced_matches[0]

            display_problem(problem)
            # TODO: get problem hints -> like if I have a missing mbank/hledger entry, and there are complementary entries

            print(f"there are {len(unbalanced_matches) - 1} unsolved problems remaining!")

            key = input()
            if key.startswith("s"):
                unbalanced_matches = unbalanced_matches[1:] + [unbalanced_matches[0]]
            if key.startswith("r"):
                # TODO: maaaybe watch the ledger file for changes, but that woulnd't be so trivial to implement
                break # lel, restart
            if key.startswith("a"):
                # TODO: select transation to add
                # TODO :add it to the ledger
                # TODO: populate defaults
                print("adding transaction!")
                ...
        else:
            print("Congrats, all reconciled!")
            exit(0)

def display_problem(problem: TransactionsMatch):
    if problem.contains_return:
        print("!!!! Likely a false-positive xD :: check your signs by the transaction")
        # TODO: actually mark the retrun I guess

    print("Inconsitency detected -> unbalanced match for amount:")
    print("-------- hledger --------")
    for t in problem.hledger_transactions:
        print(t)

    print("=======================")
    for t in problem.mbank_transactions:
        print(t)

    print("---------  mbank  -------")

# TODO: not sure if this belong in main...
def find_unbalanced_matches(mbank_transactions: Sequence[MbankTransaction], hledger_transactions: Sequence[HledgerTransaction]):
    # TODO: comments?
    matches = defaultdict(TransactionsMatch)

    for t in hledger_transactions:
        matches[t.amount].hledger_transactions.add(t)

    for t in mbank_transactions:
        matches[t.amount].mbank_transactions.add(t)

    matches = list(matches.values())
    assert all(m.is_correct() for m in matches)

    return [m for m in matches if not m.is_balanced]


if __name__ == "__main__":
    import argparse
    import calendar

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "month",
        type=int,
        nargs="?",
        # targetting end of previous month
        default=date.today().month - 1,
        help="Month (1–12) to override the current month",
    )

    args = parser.parse_args()

    today = date.today()
    month = args.month

    likely_reconciling_previous_year = today.month == 1 and month != 1
    year = today.year - (1 if likely_reconciling_previous_year else 0)

    reconciliation_end_date = date(year, month, calendar.monthrange(year, month)[1])

    print("reconciliation end:", reconciliation_end_date)
    main(reconciliation_end_date=reconciliation_end_date)

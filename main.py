import subprocess
from functools import partial
from collections import defaultdict
from typing import Sequence
from datetime import date, timedelta

from core import HledgerTransaction, MbankTransaction, TransactionsMatch
from ports import read_hledger_csv_transactions, read_mbank_transactions


# TODO: refactor to Path
def main(reconciliation_month, hledger_csv_statement="/tmp/sep.csv", mbank_html_statement="/home/allgreed/Downloads/bork.html"):
    previous_month_number = (date.today().replace(day=1) - timedelta(days=1)).month
    if (reconciliation_month != previous_month_number):
        print("Warning: using a month that is not the previous month!!!")

    current_month_number = date.today().month
    def dump_hledger():
        def to_str_pad_zero_twice(s): return str(s).zfill(2)
        # TODO: pass the tempfile also
        # TODO: skip the bash script I guess lol
        subprocess.run(["sh", "./hledger_print"] + list(map(to_str_pad_zero_twice, [previous_month_number, current_month_number])))

    while True:
        dump_hledger()
        with open(hledger_csv_statement) as f:
            hledger_transactions = read_hledger_csv_transactions(f)
            # assumption: reconcilement happens on monthly basis
            # assumption: the currency is pln
            # TODO: assert this assumption

        with open(mbank_html_statement) as f:
            # mbank will contain slightly more data
            # assuumption: export at least +2 days to get all the debit carts settlemetns!
            # assumption: the currency is pln
            # TODO: assert this assumption
            mbank_transactions = [t for t in read_mbank_transactions(f) if t.accounting_date.month == reconciliation_month]

        unbalanced_matches = find_unbalanced_matches(mbank_transactions, hledger_transactions)

        while unbalanced_matches:
            problem = unbalanced_matches[0]

            display_problem(problem)
            # TODO: get problem hints -> like if I have a missing mbank/hledger entry, and there are complementary entries
            # (so missing 1 mbank : missing 1 hledger), display those also

            print(f"there are {len(unbalanced_matches) - 1} unsolved problems remaining!")

            key = input()
            if key.startswith("s"):
                unbalanced_matches = unbalanced_matches[1:] + [unbalanced_matches[0]]
            # TODO: just watch the ledger file for changes lol
            if key.startswith("r"):
                # lel, restart
                break
        else:
            print("Congrats, all reconciled!")
            exit(0)

def display_problem(problem):
    if any(t.amount > 0 for t in problem.hledger_transactions):
        # TODO: and account is expense!!!
        print("Likely a false-positive xD :: check your signs by the transaction")

    def display_mbank_transaction(t: MbankTransaction) -> str:
        return f"{t.amount} {t.accounting_date} {t.description}"

    def display_hledger_transaction(t: HledgerTransaction) -> str:
        # TODO: also ledger ID?
        return f"{t.amount} {t.accounting_date} {t.description}"

    print("Inconsitency detected -> unbalanced match for amount:")
    print("-------- hledger --------")
    for t in problem.hledger_transactions:
        print(display_hledger_transaction(t))

    print("=======================")
    for t in problem.mbank_transactions:
        print(display_mbank_transaction(t))

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
    previous_month = date.today().replace(day=1) - timedelta(days=1)
    main(reconciliation_month=int(previous_month.strftime("%m")))

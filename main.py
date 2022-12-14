from collections import defaultdict
from typing import Sequence

from core import HledgerTransaction, MbankTransaction, TransactionsMatch
from ports import read_hledger_csv_transactions, read_mbank_transactions


# TODO: refactor to Path
def main(reconciliation_month=11, hledger_csv_statement="/tmp/sep.csv", mbank_html_statement="/home/allgreed/Downloads/bork.html"):
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

    if unbalanced_matches:
        problem = unbalanced_matches[0]

        def display_mbank_transaction(t: MbankTransaction) -> str:
            return f"{t.amount} {t.accounting_date} {t.description}"

        def display_hledger_transaction(t: MbankTransaction) -> str:
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
        # display the problem sensibly

        print(f"there are {len(unbalanced_matches) - 1} unsolved problems remaining!")

        # TODO: pay close attention to transcation with negative expenses -> they might be insanely wrong
        # TODO: nicer way to automate reconciliment update
        # TODO: some kind of a switch for handling problems one at a time
    else:
        print("Congrats, all reconciled!")


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
    main()

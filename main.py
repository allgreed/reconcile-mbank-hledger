import csv
import re
from collections import defaultdict
from typing import Optional, Dict, Any, Tuple, List, Sequence
from dataclasses import dataclass, field

from core import HledgerTransaction, MbankTransaction


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

    # TODO: should match be defined on a Transaction or seperately?
    @dataclass
    class TransactionsMatch:
        hledger_transactions: List[HledgerTransaction] = field(default_factory=list)
        mbank_transactions: List[MbankTransaction] = field(default_factory=list)

        def is_correct(self):
            # TODO: code this - concat sequences and extract amount, should work based on common Transaction type
            # amounts = ...
            # return all(a == amount[0] for a in amounts[1:]) 
            return True

        @property
        def is_balanced(self):
            return len(self.hledger_transactions) == len(self.mbank_transactions)

    matches = defaultdict(TransactionsMatch)
    for t in hledger_transactions:
        matches[t.amount].hledger_transactions.append(t)
    for t in mbank_transactions:
        matches[t.amount].mbank_transactions.append(t)
    matches = list(matches.values())
    assert all(m.is_correct() for m in matches), "all matches are correct - meaning the optimisation works as expected"

    unbalanced_matches = [m for m in matches if not m.is_balanced]

    if unbalanced_matches:
        ...
        # display the problem sensibly
    else:
        print("Congrats, all reconciled!")

    # TODO: pay close attention to transcation with negative expenses -> they might be insanely wrong
    # TODO: nicer way to automate reconciliment update

    ##########
    # TODO: refactor into domain code <<<<<<<

    unmatchedmbank_trns = set()
    mbank_trans_by_amount = defaultdict(list)
    mbank_trns_by_id = {}
    for t in mbank_transactions:
        mbank_trans_by_amount[t.amount].append((t.description, id(t)))
        mbank_trns_by_id[id(t)] = (t.amount, t.description)
        unmatchedmbank_trns.add(id(t))

    duplicate_bleledger_trns_by_amount = defaultdict(list)
    for ht in hledger_transactions:
        corresponding_transaction = mbank_trans_by_amount[ht.amount]
        if corresponding_transaction:
            if len(corresponding_transaction) > 1:
                duplicate_bleledger_trns_by_amount[ht.amount].append(ht)
            else:
                # corresponding_transaction_id = id(corresponding_transaction)
                corresponding_transaction_id = corresponding_transaction[0][1]
                try:
                    unmatchedmbank_trns.remove(corresponding_transaction_id)    
                except KeyError:
                    # TODO: deal with double matching form hledger to mbank
                    # so: hledger has two trns with amount X, while mbank has only one with amout X
                    print("A!", ht) 
                    pass

        else:
            # TODO: deal with those
            print("unmatched", ht)
            pass

    # TODO: deal with this!
    for amount, cases in  duplicate_bleledger_trns_by_amount.items():
        match = mbank_trans_by_amount[amount]
        if len(cases) != len(match):
            # TODO: print a header for this
            # also: some kind of a switch for handling problems one at a time
            print(cases, match)
            pass
        else:
            matched_ids = (t[1] for t in match)
            for matched_id in matched_ids:
                unmatchedmbank_trns.remove(matched_id)    

    # TODO: handle this!
    print("=== mbank doesn't match hledger ====")
    for t in unmatchedmbank_trns:
        print(mbank_trns_by_id[t])


# TODO: type as IOsomething
# TODO: extract as port
def read_hledger_csv_transactions(file: ...) -> Sequence[HledgerTransaction]:
    def parse_hledger_chunk(row: Dict[str, Any]) -> Optional[HledgerTransaction]:
        if row["account"] == "assets:mbank:main":
            if row["description"] == "Reconcilement":
                return

            return HledgerTransaction(
                description=row["description"],
                ledger_id=row["txnidx"],
                amount=row["amount"],
            )

    result = map(parse_hledger_chunk, csv.DictReader(file))
    # remove the pesky None's
    result = list(filter(bool, result))
    # TODO: or typecheck in some other way to make the pyright happy
    assert all(isinstance(i, HledgerTransaction) for i in result)
    return result


# TODO: type as IOsomething
# TODO: extract as port
def read_mbank_transactions(file: ...) -> Sequence[MbankTransaction]:
    def parse_mbank_chunk(regexp_match: Tuple[str, str, str, str]) -> MbankTransaction:
        description = regexp_match[2]

        bank_operation_date = regexp_match[0]
        bank_clearing_date = regexp_match[1]

        assert bank_operation_date == bank_clearing_date
        bank_date = bank_operation_date

        additional_date_match = re.search("DATA TRANSAKCJI: (.*)", description)
        # this corresponds to when the card is swipped as opposed to when the
        # transaction is cleared with the provider
        expense_origin_date = additional_date_match.group(1) if additional_date_match else None

        return MbankTransaction(
            amount=regexp_match[3].replace(",",".").replace(" ", ""),
            description=description,
            accounting_date=expense_origin_date or bank_date,
        )

    MAGIC_MBANK_STATEMENT_REGEXP = r'<tr>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+><nobr>(.*)<\/nobr><\/td>\n\s+<td["\s\w=]+>.*<\/td>\n\s+<\/tr>'

    matches = re.findall(MAGIC_MBANK_STATEMENT_REGEXP, file.read().strip(), re.MULTILINE)
    return list(map(parse_mbank_chunk, matches))


if __name__ == "__main__":
    main()

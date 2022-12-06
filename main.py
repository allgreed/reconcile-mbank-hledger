import csv
import re
from collections import defaultdict
from typing import Dict, Any
import hashlib
import json
import uuid


from core import HledgerTransaction, MbankTransaction, Transaction


def main():
    # export at least +2 days to get all the debit carts settlemetns!
    # assumption: reconcilement happens on monthly basis

    # TODO: refactor into domain code

    # TODO: pay close attention to transcation with negative expenses -> they might be insanely wrong

    # TODO: make sure I'm getting the right periods for mbank -> see settlement vs transaction date
    # TODO: nicer way to automate reconciliment update

    hledger_transactions: list(HledgerTransaction) = []

    bleledger_trns = []
    unmatchedmbank_trns = set()
    mbank_trans_by_amount = defaultdict(list)
    mbank_trns_by_id = {}

    with open("/tmp/sep.csv") as csvfile:
        spamreader = csv.DictReader(csvfile)
        for row in spamreader:
            if row["account"] == "assets:mbank:main":
                if row["description"] == "Reconcilement":
                    continue

                trn_id = row["txnidx"]
                bleledger_trns.append((float(row["amount"]), row["description"], trn_id))

                hledger_transactions.append(HledgerTransaction(
                    description=row["description"],
                    ledger_id=row["txnidx"],
                    amount=row["amount"],
                ))

    with open("/home/allgreed/Downloads/bork.html") as f:
        r_bankdata = f.read().strip()
        regexp = r'<tr>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+><nobr>(.*)<\/nobr><\/td>\n\s+<td["\s\w=]+>.*<\/td>\n\s+<\/tr>'

        for m in re.findall(regexp, r_bankdata, re.MULTILINE):
            will_add = True
            klopotliwe_rozliczenie = False
            trn_id = uuid.uuid4()
            amount = float(m[3].replace(",",".").replace(" ", ""))
            desc = m[2]

            # TODO: extract parameter
            # TODO: months are not numbers
            current_month = 11
            previos_month = current_month - 1
            next_month = current_month + 1

            if "/" in desc:
                lm = re.search("DATA TRANSAKCJI: (.*)", desc)
                if lm:
                    trn_effective_date = lm.group(1)
                    
                    # TODO: dates are not strings
                    if trn_effective_date.startswith(f"2022-{previos_month}") or trn_effective_date.startswith(f"2022-{next_month}"):
                        will_add = False
                    else:
                        klopotliwe_rozliczenie = True

            assert m[0] == m[1], "operation date matches clearing date"
            date = m[0]

            # TODO: dates are not strings
            if date.startswith(f"2022-{previos_month}") or date.startswith(f"2022-{next_month}"):
                will_add = klopotliwe_rozliczenie

            if will_add:
                mbank_trans_by_amount[amount].append((desc, trn_id))
                mbank_trns_by_id[trn_id] = (amount, desc)
                unmatchedmbank_trns.add(trn_id)

    duplicate_bleledger_trns = defaultdict(list)

    for ht in hledger_transactions:
        match = mbank_trans_by_amount[float(ht.amount)]
        if match:
            if len(match) > 1:
                duplicate_bleledger_trns[float(ht.amount)].append(ht)
            else:
                matched_id = match[0][1]
                try:
                    unmatchedmbank_trns.remove(matched_id)    
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
    for amount, cases in  duplicate_bleledger_trns.items():
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

    # TODO: add some kind of success message when all is well


def hash_dict(dictionary: Dict[str, Any]) -> str:
    """from: https://stackoverflow.com/a/67438471/9134286"""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


if __name__ == "__main__":
    main()

import csv
import re
from collections import defaultdict
from typing import Dict, Any
import hashlib
import json


def main():
    # TODO: make sure I'm getting the right periods for mbank -> see settlement vs transaction date
    # TODO: nicer way to automate reconciliment update

    hledger_trns = []
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
                hledger_trns.append((float(row["amount"]), row["description"], trn_id))

    with open("/home/allgreed/Downloads/bork") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=";")
        for row in spamreader:
            trn_id = hash_dict(row)
            amount = float(row["kwota"].replace(",",".").replace(" ", ""))
            desc = row["opis"]
            if "/" in desc:
                desc = re.match(r"(.*)\/", desc).group(1).rstrip(" ")
            mbank_trans_by_amount[amount].append((desc, trn_id))
            mbank_trns_by_id[trn_id] = (amount, desc)
            unmatchedmbank_trns.add(trn_id)

    duplicate_hledger_trns = defaultdict(list)

    for ht in hledger_trns:
        amount = ht[0]
        match = mbank_trans_by_amount[amount]
        if match:
            if len(match) > 1:
                duplicate_hledger_trns[amount].append(ht)
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
            print(ht)
            pass

    # TODO: deal with this!
    for amount, cases in  duplicate_hledger_trns.items():
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
    print("==============")
    for t in unmatchedmbank_trns:
        print(mbank_trns_by_id[t])


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

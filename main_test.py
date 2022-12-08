from core import *
from main import legacy_find_unbalanced_matches

def test_find_unbalanched_matches():
    assert [] == legacy_find_unbalanced_matches(mbank_transactions=[], hledger_transactions=[])


def test_mk_transaction():
    HledgerTransaction(amount=5.12, ledger_id=3, description="aaa")

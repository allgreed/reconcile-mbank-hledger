import pytest

from core import *
from main import legacy_find_unbalanced_matches, find_unbalanced_matches

m = MbankTransaction(amount=5, description="ble", accounting_date="2022-10-02")
h = HledgerTransaction(amount=5, description="ble", ledger_id=5)
m5 = MbankTransaction(amount=5, description="fuj", accounting_date="2022-10-02")

@pytest.mark.parametrize("mbank_transactions,hledger_transactions,result", [
    (set(), set(), []),
    ({m}, set(), [TransactionsMatch(mbank_transactions=[m])]),
    (set(), {h}, [TransactionsMatch(hledger_transactions=[h])]),
    ({m}, {h}, []),
    # ([h], [m, m5], [TransactionsMatch(mbank_transactions=[m5, m], hledger_transactions=[h])]),
])
def test_find_unbalanched_matches(mbank_transactions, hledger_transactions, result):
    assert result == find_unbalanced_matches(mbank_transactions=mbank_transactions, hledger_transactions=hledger_transactions)
    assert result == legacy_find_unbalanced_matches(mbank_transactions=mbank_transactions, hledger_transactions=hledger_transactions)


def test_mk_transaction():
    HledgerTransaction(amount=5.12, ledger_id=3, description="aaa")

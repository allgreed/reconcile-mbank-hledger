import pytest

from core import *


m = MbankTransaction(amount=5, description="ble", accounting_date="2022-10-02")
h = HledgerTransaction(amount=5, description="ble", ledger_id=5)
m5 = MbankTransaction(amount=5, description="fuj", accounting_date="2022-10-02")
h5 = HledgerTransaction(amount=5, description="fuj", ledger_id=6)
m7 = MbankTransaction(amount=7, description="bork", accounting_date="2022-10-02")
h7 = HledgerTransaction(amount=7, description="bork", ledger_id=7)


@pytest.mark.parametrize("additional_m,additional_h", [
    (set(), set()),
    ({m7}, {h7}),
])
@pytest.mark.parametrize("real_world_transactions,hledger_transactions,result", [
    (set(), set(), []),
    ({m}, set(), [MatchSet(real_world_transactions=[m])]),
    (set(), {h}, [MatchSet(hledger_transactions=[h])]),
    ({m}, {h}, []),
    ({m, m5}, {h}, [MatchSet(real_world_transactions={m5, m}, hledger_transactions={h})]),
    ({m}, {h, h5}, [MatchSet(real_world_transactions={m}, hledger_transactions={h, h5})]),
])
def test_find_unbalanched_matches(real_world_transactions, hledger_transactions, result, additional_h, additional_m):
    real_world_transactions.union(additional_m)
    hledger_transactions.union(additional_h)

    assert result == find_unbalanced_matches(real_world_transactions=real_world_transactions, hledger_transactions=hledger_transactions)


def test_mk_transaction():
    HledgerTransaction(amount=5.12, ledger_id=3, description="aaa")

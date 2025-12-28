import subprocess
from functools import partial
from collections import defaultdict
from typing import Sequence
from datetime import date, timedelta

from core import HledgerTransaction, MbankTransaction, TransactionsMatch
from ports import read_hledger_csv_transactions, read_mbank_transactions

from decimal import Decimal
import datetime
x = TransactionsMatch(hledger_transactions={HledgerTransaction(amount=Decimal('-40.00'), description='Tratoria - spaghetti', accounting_date=datetime.date(2023, 11, 8), currency='PLN', ledger_id=1654), HledgerTransaction(amount=Decimal('-40.00'), description='Tratoria - foccacia z krewetkami', accounting_date=datetime.date(2023, 11, 30), currency='PLN', ledger_id=1778), HledgerTransaction(amount=Decimal('-40.00'), description='Dwie Zmiany', accounting_date=datetime.date(2023, 11, 30), currency='PLN', ledger_id=1771), HledgerTransaction(amount=Decimal('-40.00'), description='Tratoria - foccacia z krewetkami', accounting_date=datetime.date(2023, 11, 24), currency='PLN', ledger_id=1745), HledgerTransaction(amount=Decimal('-40.00'), description='Krewetki śniadaniowe tratoria', accounting_date=datetime.date(2023, 11, 18), currency='PLN', ledger_id=1713), HledgerTransaction(amount=Decimal('-40.00'), description='Dwie Zmiany', accounting_date=datetime.date(2023, 11, 15), currency='PLN', ledger_id=1687), HledgerTransaction(amount=Decimal('-40.00'), description='Dwie Zmiany', accounting_date=datetime.date(2023, 11, 7), currency='PLN', ledger_id=1651), HledgerTransaction(amount=Decimal('-40.00'), description='Tratoria - spaghetti', accounting_date=datetime.date(2023, 11, 25), currency='PLN', ledger_id=1756)}, mbank_transactions={MbankTransaction(amount=Decimal('-40.00'), description='ZAKUP PRZY UŻYCIU KARTY<br>TRATTORIA GUSTO    /Gdansk                                            DATA TRANSAKCJI: 2023-11-24', accounting_date=datetime.date(2023, 11, 24), currency='PLN'), MbankTransaction(amount=Decimal('-40.00'), description='ZAKUP PRZY UŻYCIU KARTY<br>DWIE ZMIANY        /SOPOT                                             DATA TRANSAKCJI: 2023-11-07', accounting_date=datetime.date(2023, 11, 7), currency='PLN'), MbankTransaction(amount=Decimal('-40.00'), description='ZAKUP PRZY UŻYCIU KARTY<br>TRATTORIA GUSTO    /Gdansk                                            DATA TRANSAKCJI: 2023-11-18', accounting_date=datetime.date(2023, 11, 18), currency='PLN'), MbankTransaction(amount=Decimal('-40.00'), description='ZAKUP PRZY UŻYCIU KARTY<br>DWIE ZMIANY        /SOPOT                                             DATA TRANSAKCJI: 2023-11-29', accounting_date=datetime.date(2023, 11, 29), currency='PLN'), MbankTransaction(amount=Decimal('-40.00'), description='ZAKUP PRZY UŻYCIU KARTY<br>DWIE ZMIANY        /SOPOT                                             DATA TRANSAKCJI: 2023-11-14', accounting_date=datetime.date(2023, 11, 14), currency='PLN'), MbankTransaction(amount=Decimal('-40.00'), description='ZAKUP PRZY UŻYCIU KARTY<br>TRATTORIA GUSTO    /Gdansk                                            DATA TRANSAKCJI: 2023-11-25', accounting_date=datetime.date(2023, 11, 25), currency='PLN')})
print(x)

#TODO: figure out matching
# so: a local matcher for big transactions to reduce lhs and rhs
# also: a global matcher - to try and find potential typos, like 89 -> 98

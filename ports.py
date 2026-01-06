import io
import csv
import re
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple, Sequence
from datetime import datetime, date

from core import HledgerTransaction, MbankTransaction, Transaction


# ugly hack, but also needed
_nonce = 0
def mk_nonce() -> int:
    global _nonce
    _nonce += 1
    return _nonce


def read_mbank_transactions(file: io.TextIOBase) -> Sequence[MbankTransaction]:
    MAGIC_MBANK_STATEMENT_REGEXP = r'<tr>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+><nobr>(.*)<\/nobr><\/td>\n\s+<td["\s\w=]+>.*<\/td>\n\s+<\/tr>'

    def parse_mbank_chunk(i: int, regexp_match: Tuple[str, str, str, str]) -> MbankTransaction:
        # TODO: lift this up
        # TODO: this format appears many time, does it have a name?
        def parse_date(s: str) -> date: return datetime.strptime(s, "%Y-%m-%d").date()

        rm = regexp_match
        bank_operation_date, bank_clearing_date, description = parse_date(rm[0]), parse_date(rm[1]), rm[2] 

        assert bank_operation_date.month == bank_clearing_date.month
        bank_date = max(bank_operation_date, bank_clearing_date)

        additional_date_match = re.search("DATA TRANSAKCJI: (.*)", description)
        # this corresponds to when the card is swipped as opposed to when the
        # transaction is cleared with the provider
        expense_origin_date = additional_date_match.group(1) if additional_date_match else None

        return MbankTransaction(
            nonce = mk_nonce(),
            amount=regexp_match[3].replace(",",".").replace(" ", ""),
            description=description,
            accounting_date=expense_origin_date or bank_date,
            currency="PLN",
        )

    matches = re.findall(MAGIC_MBANK_STATEMENT_REGEXP, file.read().strip(), re.MULTILINE)
    return list(map(parse_mbank_chunk, *zip(*enumerate(matches))))


def read_hledger_csv_transactions(file: io.TextIOBase, bank: str) -> Sequence[HledgerTransaction]:
    # TODO: also it's not *just* hledgerTransaction - it's MbankHledgerTransaction
    def parse_hledger_chunk(row: Dict[str, Any]) -> Optional[HledgerTransaction]:
        # TODO: have a debugger utility for this?
        #  if row["txnidx"] == "1215":
            #  print(row)

        # TODO: this is domain specific processing - move it where it belongs
        target_account = "assets:revolut" if bank == "revolut" else "assets:mbank:main"
        if row["account"] == target_account:
            if row["description"] == "Reconcilement":
                return

            date1 = row["date"]
            date2 = row["date2"]
            assert date2 == ""

            # TODO: display this error more gracefully
            # maybe introspect the pydantic errors?
            if len(row["description"]) < 3:
                print(row["description"])


            return HledgerTransaction(
                nonce = mk_nonce(),
                description=row["description"],
                ledger_id=row["txnidx"],
                amount=row["amount"],
                accounting_date=date1,
                currency = row["commodity"],
            )

    return [
        c
        for ck in csv.DictReader(file)
        if (c := parse_hledger_chunk(ck)) is not None
    ]


def read_revolut_csv_transactions(file: io.TextIOBase) -> Sequence[Transaction]:
    def parse_chunk(row: Dict[str, Any]) -> Transaction:
        date1 = row["Data rozpoczęcia"].split(" ")[0]
        #  date2 = row["Data zrealizowania"]
        amount = Decimal(row["Kwota"])
        surcharge = Decimal(row["Opłata"])

        assert (amount < 0 and surcharge > 0) or surcharge == 0
        total = amount - surcharge

        return Transaction(
            nonce = mk_nonce(),
            description=row["Opis"],
            amount=total,
            accounting_date=date1,
            currency = row["Waluta"],
        )

    return list(map(parse_chunk, csv.DictReader(file)))

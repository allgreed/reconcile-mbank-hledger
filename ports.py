import io
import csv
import re
from typing import Optional, Dict, Any, Tuple, Sequence

from core import HledgerTransaction, MbankTransaction


def read_mbank_transactions(file: io.TextIOBase) -> Sequence[MbankTransaction]:
    def parse_mbank_chunk(i: int, regexp_match: Tuple[str, str, str, str]) -> MbankTransaction:
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
            item_number=i,
        )

    MAGIC_MBANK_STATEMENT_REGEXP = r'<tr>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+>(.*)<\/td>\n\s+<td["\s\w=]+><nobr>(.*)<\/nobr><\/td>\n\s+<td["\s\w=]+>.*<\/td>\n\s+<\/tr>'

    matches = re.findall(MAGIC_MBANK_STATEMENT_REGEXP, file.read().strip(), re.MULTILINE)
    return list(map(parse_mbank_chunk, *zip(*enumerate(matches))))


def read_hledger_csv_transactions(file: io.TextIOBase) -> Sequence[HledgerTransaction]:
    def parse_hledger_chunk(i: int, row: Dict[str, Any]) -> Optional[HledgerTransaction]:
        if row["account"] == "assets:mbank:main":
            if row["description"] == "Reconcilement":
                return

            date1 = row["date"]
            date2 = row["date2"]
            assert date2 == ""

            return HledgerTransaction(
                item_number=i,
                description=row["description"],
                ledger_id=row["txnidx"],
                amount=row["amount"],
                accounting_date=date1,
                currency = row["commodity"],
            )

    result = map(parse_hledger_chunk, *zip(*enumerate(csv.DictReader(file))))
    # remove the pesky None's
    result = list(filter(bool, result))
    # TODO: or typecheck in some other way to make the pyright happy
    assert all(isinstance(i, HledgerTransaction) for i in result)
    return result

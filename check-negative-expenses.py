import subprocess
import csv
import io
from datetime import datetime

# this is stupid, but is alos fast
REVIEWED = {120, 180}
assert datetime.today().year == 2025

def main():
    r = subprocess.run([
        "hledger", "register",
        "expenses", "costs",
        "--output-format", "csv",
    ], capture_output=True, text=True)

    csv_reader = csv.reader(io.StringIO(r.stdout))

    next(csv_reader) # skip header
    for row in csv_reader:
        transaction_id = int(row[0])
        amount = float(row[5].split(" ")[0])

        if amount < 0:
            if transaction_id not in REVIEWED:
                print(row)
                break
    else:
        print("no unreview negatives!")

if __name__ == "__main__":
    main()

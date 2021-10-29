import csv
import pathlib

from narraint.config import TMP_DIR
from narrant.config import RESOURCE_DIR

if __name__ == '__main__':
    with open(pathlib.Path(RESOURCE_DIR) / "df_additional_descs_terms.txt") as incsv, open(
            pathlib.Path(TMP_DIR) / "df_vocab.tsv", "w+") as outcsv:
        reader = csv.DictReader(incsv, delimiter="\t", fieldnames=["id", "synonyms"])
        writer = csv.DictWriter(outcsv, delimiter="\t", fieldnames=["id", "enttype", "heading", "synonyms"])
        writer.writeheader()
        for line in reader:
            writer.writerow({"id": line["id"], "enttype": "DosageForm", "heading": line["synonyms"].split(";")[0],
                             "synonyms": ";".join(line["synonyms"].split(";")[1:])})

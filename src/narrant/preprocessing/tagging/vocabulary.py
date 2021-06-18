from collections import defaultdict
from pathlib import Path
from typing import Union
from narrant.config import TMP_DIR
import csv

from narrant.preprocessing.tagging.vocabularies import expand_vocabulary_term


class Vocabulary:
    def __init__(self, path: Union[str, Path]):
        self.path = path
        self.vocabularies = defaultdict(lambda: defaultdict(set))

    def load_vocab(self):
        if self.vocabularies:
            return
        with open(self.path, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                for syn in {s for t in (line["synonyms"].split(";") + [line["heading"]]) for s in expand_vocabulary_term(t.lower()) if t}:
                    self.vocabularies[line["enttype"]][syn] |= {line["id"]}
            self.vocabularies = {k: dict(v) for k, v in self.vocabularies.items()}

    def get_ent_types(self):
        return self.vocabularies.keys()
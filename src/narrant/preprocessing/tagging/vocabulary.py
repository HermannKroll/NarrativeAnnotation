import csv
from collections import defaultdict
from pathlib import Path
from typing import Union


class Vocabulary:
    def __init__(self, path: Union[str, Path]):
        self.path = path
        self.vocabularies = defaultdict(lambda: defaultdict(set))

    def load_vocab(self, expand_terms=True):
        if self.vocabularies:
            return
        with open(self.path, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                if not line["heading"] or not line["enttype"] or not line["id"]:
                    continue
                if expand_terms:
                    for syn in {s
                                for t in (line["synonyms"].split(";") if line["synonyms"] else []) + [line["heading"]]
                                for s in expand_vocabulary_term(t.lower()) if t}:
                        self.vocabularies[line["enttype"]][syn] |= {line["id"]}
                else:
                    for syn in {t.lower()
                                for t in (line["synonyms"].split(";") if line["synonyms"] else []) + [line["heading"]]}:
                        self.vocabularies[line["enttype"]][syn] |= {line["id"]}
            self.vocabularies = {k: dict(v) for k, v in self.vocabularies.items()}

    def get_ent_types(self):
        return self.vocabularies.keys()


def expand_vocabulary_term(term: str, minimum_len_to_expand=3, depth=0) -> str:
    # only consider the length the last term
    if ' ' in term and len(term.split(' ')[-1]) < minimum_len_to_expand:
        yield term
    # test if term has the minimum len to be expanded
    elif len(term) < minimum_len_to_expand:
        yield term
    else:
        if term.endswith('y'):
            yield f'{term[:-1]}ies'
        if term.endswith('ies'):
            yield f'{term[:-3]}y'
        if term.endswith('s') or term.endswith('e'):
            yield term[:-1]
        if term.endswith('or') and len(term) > 2:
            yield term[:-2] + "our"
        if term.endswith('our') and len(term) > 3:
            yield term[:-3] + "or"
        if "-" in term:
            yield term.replace("-", " ")
            if depth == 0:
                yield from expand_vocabulary_term(term.replace("-", " "), depth=1)
            yield term.replace("-", "")
            if depth == 0:
                yield from expand_vocabulary_term(term.replace("-", ""), depth=1)
        if " " in term:
            yield term.replace(" ", "-")
            if depth == 0:
                yield from expand_vocabulary_term(term.replace(" ", "-"), depth=1)
            yield term.replace(" ", "")
            if depth == 0:
                yield from expand_vocabulary_term(term.replace(" ", ""), depth=1)
        yield from [term, f'{term}e', f'{term}s']

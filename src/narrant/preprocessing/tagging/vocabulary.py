import csv
from collections import defaultdict
from pathlib import Path
from typing import Union


class VocabularyEntry:

    def __init__(self, entity_id, entity_type, heading, synonyms):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.heading = heading
        self.synonyms = synonyms


class Vocabulary:
    def __init__(self, path: Union[str, Path]):
        self.path = path
        self.vocabularies = defaultdict(lambda: defaultdict(set))
        self.vocabulary_entries = list()
        self._entry_by_id_and_type = {}
        self.size = 0

    def load_vocab(self, expand_terms=True):
        if self.vocabularies:
            return
        with open(self.path, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                if not line["heading"] or not line["enttype"] or not line["id"]:
                    continue

                self.size += 1
                entry = VocabularyEntry(line["id"], line["enttype"], line["heading"], line["synonyms"])
                self.vocabulary_entries.append(entry)

                key = (line["id"], line["enttype"])
                if key in self._entry_by_id_and_type:
                    raise ValueError(f"Found duplicated entry in vocabulary: {key}")
                else:
                    self._entry_by_id_and_type[key] = entry

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

    def get_entity_heading(self, entity_id: str, entity_type: str) -> str:
        """
        Get an entity heading from the vocabulary
        :param entity_id: entity id
        :param entity_type: entity type
        :return: heading
        """
        return self._entry_by_id_and_type[(entity_id, entity_type)].heading

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

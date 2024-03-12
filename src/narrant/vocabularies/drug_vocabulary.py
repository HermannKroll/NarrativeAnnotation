import csv
import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Set

from lxml import etree as ET

import narrant.vocabularies.chemical_vocabulary as chem_vocab
import narrant.vocabularies.excipient_vocabulary as exc_vocab
from kgextractiontoolbox.entitylinking.tagging.dictagger import clean_vocab_word_by_split_rules
from kgextractiontoolbox.entitylinking.tagging.vocabulary import expand_vocabulary_term, Vocabulary
from kgextractiontoolbox.progress import print_progress_with_eta
from narrant import config
from narrant.config import CHEMBL_BLACKLIST_FILE, DRUG_TAGGER_VOCAB
from narrant.entitylinking.enttypes import DRUG
from narrant.vocabularies.chembl_vocabulary import ChemblVocabulary


class DrugVocabulary(ChemblVocabulary):
    def __init__(self):
        """
        Note that our chembl drugs are retrieved via /molecules and not via /drugs! For that we need to add a
        filter to the URL to access the correct data (pref_name not null ~ 47539 results [12-2022]). Another
        change is the internal type usage of 'Drug' instead of 'Molecule'
        """
        vocab_type = 'molecule'
        super().__init__(DRUG_TAGGER_VOCAB, vocab_type)
        self.url_params['pref_name__isnull'] = 'false'  # specific API request filter
        self.internal_type = DRUG

    def _create_vocabulary_from_dir(self, tmp_dir):
        vocabulary = Vocabulary('')
        synonyms = list()
        skipped_synonyms = 0

        logging.info("Start creating {} vocabulary.".format(self.vocab_type))

        for file_name in os.listdir(tmp_dir):
            file_name = os.path.join(tmp_dir, file_name)
            if not os.path.isfile(file_name):
                continue

            with open(file_name) as file:
                for t in json.load(file):
                    if not (t['molecule_chembl_id'] or t['pref_name']):
                        continue

                    entity_id = t['molecule_chembl_id']
                    heading = t['pref_name']

                    if t['molecule_synonyms']:
                        for tc in t['molecule_synonyms']:
                            if tc['syn_type'] and tc['syn_type'] == 'TRADE_NAME':
                                skipped_synonyms += 1
                                continue
                            if tc['molecule_synonym']:
                                synonyms.append(tc['molecule_synonym'])
                            if tc['synonyms'] and tc['synonyms'].lower() != synonyms[-1].lower():
                                synonyms.append(tc['synonyms'])

                    if len(synonyms) > 0:
                        syn_str = ";".join(synonyms)
                        synonyms.clear()
                    else:
                        syn_str = ""

                    vocabulary.add_vocab_entry(entity_id, self.internal_type, heading, syn_str)

        logging.info("Parsed {} drugs with {} terms. Skipped {} synonyms. Saving vocabulary..."
                     .format(vocabulary.count_distinct_entities(), skipped_synonyms,
                             vocabulary.count_distinct_terms()))

        vocabulary.export_vocabulary_as_tsv(self.vocab_dir)

    @staticmethod
    def read_chembl_blacklist_terms(file: str = CHEMBL_BLACKLIST_FILE) -> Set[str]:
        terms = set()
        with open(file, 'rt') as file:
            for line in file:
                terms.add(line.strip().lower())
        return terms

    @staticmethod
    def create_drug_vocabulary_from_chembl(source_file=config.DRUG_TAGGER_VOCAB,
                                           expand_terms=True,
                                           ignore_excipient_terms=True,
                                           ignore_drugbank_chemicals=True):
        # create drug vocabulary if it does not exist
        if not os.path.isfile(source_file):
            DrugVocabulary().initialize_vocabulary()

        # read excipient terms if they should be ignored
        excipient_terms = set()
        if ignore_excipient_terms:
            excipient_terms = exc_vocab.ExcipientVocabulary.read_excipients_names()
        drugbank_chemicals = set()
        if ignore_drugbank_chemicals:
            drugbank_chemicals = chem_vocab.ChemicalVocabulary.read_drugbank_chemical_names()

        # read blacklisted terms
        blacklist_terms = DrugVocabulary.read_chembl_blacklist_terms()

        drug_by_term = defaultdict(set)
        chembl_ids_to_ignore = set()
        chembl_id_to_terms = defaultdict(set)

        vocab = Vocabulary(source_file)
        vocab.load_vocab(expand_terms=expand_terms)

        for entry in vocab.vocabulary_entries:
            chembl_id = entry.entity_id
            pref_name = entry.heading.strip().lower()
            terms = list(pref_name)
            if entry.synonyms:
                synonyms = entry.synonyms.lower().split(';')
                terms.extend(synonyms)

            chembl_id_to_terms[chembl_id].update(terms)
            for t in terms:
                if ignore_excipient_terms and t in excipient_terms:
                    chembl_ids_to_ignore.add(chembl_id)
                if ignore_drugbank_chemicals and t in drugbank_chemicals:
                    chembl_ids_to_ignore.add(chembl_id)
                if t in blacklist_terms:
                    chembl_ids_to_ignore.add(chembl_id)

        # go through all drugs
        for chembl_id, terms in chembl_id_to_terms.items():
            # if chembl id should be ignored - skip it
            if chembl_id in chembl_ids_to_ignore:
                continue
            for term in terms:
                if expand_terms:
                    for t in expand_vocabulary_term(term):
                        drug_by_term[t].add(chembl_id)
                else:
                    drug_by_term[term].add(chembl_id)
        return {term: ids for term, ids in drug_by_term.items() if len(ids) <= 2}


def get_chemblid2synonym(csv_file):
    with open(csv_file) as f:
        reader = csv.reader(f, delimiter=',', quotechar='"', )
        index = {}
        for row in reader:
            if row[0] not in index:
                index[row[0]] = set()
            index[row[0]].add(row[1].lower())
            index[row[0]].add(row[2].lower())
        return index


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    DrugVocabulary().initialize_vocabulary(force_create=True)

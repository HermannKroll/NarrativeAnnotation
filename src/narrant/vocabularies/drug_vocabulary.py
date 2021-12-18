import csv
import logging
import os
from collections import defaultdict
from datetime import datetime
from itertools import islice
from typing import Set

from lxml import etree as ET

from narrant import config
from narrant.config import CHEMBL_BLACKLIST_FILE
from narrant.preprocessing.tagging.dictagger import clean_vocab_word_by_split_rules
from narrant.preprocessing.tagging.vocabulary import expand_vocabulary_term
from narrant.vocabularies.excipient_vocabulary import ExcipientVocabulary
from narrant.progress import print_progress_with_eta
from narrant.vocabularies.chemical_vocabulary import ChemicalVocabulary


class DrugVocabulary:

    @staticmethod
    def read_chembl_blacklist_terms(file: str = CHEMBL_BLACKLIST_FILE) -> Set[str]:
        terms = set()
        with open(file, 'rt') as f:
            for line in file:
                terms.add(line.strip().lower())
        return terms

    @staticmethod
    def create_drug_vocabulary_from_chembl(source_file=config.CHEMBL_DRUG_CSV,
                                           expand_terms=True,
                                           ignore_excipient_terms=True,
                                           ignore_drugbank_chemicals=True):

        # read excipient terms if they should be ignored
        excipient_terms = set()
        if ignore_excipient_terms:
            excipient_terms = ExcipientVocabulary.read_excipients_names()
        drugbank_chemicals = set()
        if ignore_drugbank_chemicals:
            drugbank_chemicals = ChemicalVocabulary.read_drugbank_chemical_names()

        # read blacklisted terms
        blacklist_terms = DrugVocabulary.read_chembl_blacklist_terms()


        drug_by_term = defaultdict(set)
        chembl_ids_to_ignore = set()
        chembl_id_to_terms = defaultdict(set)
        with open(source_file, 'rt') as f:
            reader = csv.reader(f, delimiter=',')
            for row in islice(reader, 1, None):
                chembl_id = row[0].strip()
                pref_name = row[1].lower().strip()
                synonym = row[2].lower().strip()
                terms = list([pref_name, synonym])

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

    @staticmethod
    def create_drugbank_vocabulary_from_source(source_file=config.DRUGBANK_XML_DUMP, drug_min_name_length=3,
                                               check_products=0, drug_max_per_product=2, ignore_excipient_terms=True,
                                               ignore_drugbank_chemicals=True,
                                               expand_terms=True,
                                               use_chembl_synonyms=False,
                                               chembl_file=os.path.join(config.DATA_DIR, "chembl_synonyms.csv")):

        # TODO real check
        drug_number = 13581  # subprocess.check_output(f"grep -c '^<drug' {self.source_file}")
        start = datetime.now()
        drugs_found = 0
        logging.info(f"")
        pref = '{http://www.drugbank.ca}'
        desc_by_term = {}
        drugs_without_description_and_indication = 0

        # TODO:add config
        if use_chembl_synonyms:
            chemblid2synonym = get_chemblid2synonym(chembl_file)

        # read excipient terms if they should be ignored
        if ignore_excipient_terms:
            excipient_terms = ExcipientVocabulary.read_excipients_names()
        if ignore_drugbank_chemicals:
            drugbank_chemicals = ChemicalVocabulary.read_drugbank_chemical_names()

        for event, elem in ET.iterparse(source_file, tag=f'{pref}drug'):
            desc = ''
            for dbid in elem.findall(f'{pref}drugbank-id'):
                if dbid.attrib.get('primary'):
                    desc = dbid.text
                    break
            if desc == '':
                continue
            drugs_found += 1
            print_progress_with_eta("building index...", drugs_found, drug_number, start, print_every_k=100)
            description_text = elem.find(f'{pref}description').text
            if description_text and 'allergen' in description_text.lower()[0:30]:
                continue
            indication_text = elem.find(f'{pref}indication').text
            if not description_text and not indication_text:
                drugs_without_description_and_indication += 1
                continue
            name_elements = list(elem.findall(f'{pref}name'))
            synonyms = elem.find(f'{pref}synonyms')
            if synonyms is not None:
                name_elements += list(synonyms.findall(f'{pref}synonym'))
            if check_products > 0:
                products = elem.find(f'{pref}products')
                if products is not None:
                    for product in products.findall(f'{pref}product'):
                        name = product.find(f'{pref}name')
                        if name is not None:
                            name_elements.append(name)
            exp_props = elem.find(f'{pref}experimental-properties')
            if exp_props is not None:
                for exp_prop in exp_props:
                    if exp_prop.find(f'{pref}kind').text == "Molecular Formula":
                        name_elements.append(exp_prop.find(f'{pref}value'))

            names = {ne.text for ne in name_elements}
            if use_chembl_synonyms:
                chembl_id = ""
                for ext_id in elem.find(f"{pref}external-identifiers"):
                    if ext_id.find(f"{pref}resource").text == "ChEMBL":
                        chembl_id = ext_id.find(f"{pref}identifier").text
                        break
                if chembl_id and chembl_id in chemblid2synonym:
                    names |= chemblid2synonym[chembl_id]
            names = {n for n in names if len(n) >= drug_min_name_length}
            names = {clean_vocab_word_by_split_rules(n.lower()) for n in names}

            # ignore dbid if it's already an excipient
            if ignore_excipient_terms and len([n for n in names if n in excipient_terms]) > 0:
                continue
            # ignore dbid if it's already an DrugBankChemical
            if ignore_drugbank_chemicals and len([n for n in names if n in drugbank_chemicals]) > 0:
                continue

            if expand_terms:
                names = names | {f"{n}s" for n in names} | {f"{n}e" for n in names}
            for n in names:
                if n in desc_by_term:
                    desc_by_term[n].add(desc)
                else:
                    desc_by_term[n] = {desc, }

        if drug_max_per_product > 0:
            desc_by_term = {k: v
                            for k, v in desc_by_term.items()
                            if len(v) <= drug_max_per_product}
        return desc_by_term


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
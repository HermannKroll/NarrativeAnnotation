import json
import logging
import os
import string

from kgextractiontoolbox.entitylinking.tagging.vocabulary import Vocabulary
from narrant.config import TARGET_TAGGER_VOCAB_DIRECTORY, TARGET_TAGGER_VOCAB
from narrant.preprocessing.enttypes import TARGET
from narrant.vocabularies.chembl_vocabulary import ChemblVocabulary
from narrant.vocabularies.generic_vocabulary import GenericVocabulary

URL = "https://www.ebi.ac.uk"
URL_PATH = "/chembl/api/data/target?format=json&limit={}"


class TargetVocabulary(ChemblVocabulary):

    def __init__(self, vocab_file=TARGET_TAGGER_VOCAB, entity_type=TARGET, entity_type_in_vocab=TARGET):
        super().__init__(vocab_file, entity_type)
        self.ignored_target_types = {'organism', 'tissue', 'unchecked', 'no target'}
        self.allowed_target_types = {}
        self.allowed_organism = {}
        self.entity_type_in_vocab = entity_type_in_vocab
        self.preferred_target_organism = "homo sapiens"

    @staticmethod
    def create_target_vocabulary(expand_by_s_and_e=True):
        if not os.path.isfile(TARGET_TAGGER_VOCAB):
            TargetVocabulary().initialize_vocabulary()

        return GenericVocabulary.create_vocabulary_from_directory(TARGET_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)

    def _create_vocabulary_from_dir(self, tmp_dir):
        vocabulary = Vocabulary('')

        logging.info("Start creating target vocabulary.")
        target2organism = {}
        target2entry = {}

        target2no_of_synonyms = {}

        for file_name in os.listdir(tmp_dir):
            file_name = os.path.join(tmp_dir, file_name)
            if not os.path.isfile(file_name):
                continue

            with open(file_name) as file:
                for t in json.load(file):
                    if not (t['target_chembl_id'] or t['component_description']):
                        continue
                    # ignore certain target types
                    if len(self.ignored_target_types) > 0 \
                            and t["target_type"].strip().lower() in self.ignored_target_types:
                        continue
                    # if certain types are allowed, check type
                    if len(self.allowed_target_types) > 0 \
                            and t["target_type"].strip().lower() not in self.allowed_target_types:
                        continue

                    # Ignore targets if they belong to an organism that is not desired
                    if len(self.allowed_organism) > 0 and 'organism' in t:
                        if t["organism"] and t["organism"].strip().lower() not in self.allowed_organism:
                            continue
                        # otherwise organism not known -> continue

                    entity_id = t['target_chembl_id']
                    heading = t['pref_name']
                    if 'organism' in t and t["organism"]:
                        organism = t["organism"].strip().lower()
                    else:
                        organism = "unknown organism"
                    target2organism[entity_id] = organism

                    synonyms = list()
                    if t['target_components']:
                        for tc in t['target_components']:
                            if tc['component_description']:
                                synonyms.append(tc['component_description'])
                            if tc['target_component_synonyms']:
                                synonyms.extend([syn['component_synonym'] for syn in tc['target_component_synonyms']])

                    target2entry[entity_id] = (heading, synonyms)
                    target2no_of_synonyms[entity_id] = len(synonyms)

        logging.info('Computing vocabulary...')
        heading2synonyms = {}
        heading2best_heading = {}
        term2targets = {}
        trans_map = {p: '' for p in string.punctuation}
        translator = str.maketrans(trans_map)
        for entity_id in target2entry:
            heading, synonyms = target2entry[entity_id]
            heading_l = heading.lower().translate(translator).strip()
            if heading_l in heading2synonyms:
                h_old = sum([1 for c in heading2best_heading[heading_l] if c.isupper()])
                h_new = sum([1 for c in heading if c.isupper()])
                if h_new > h_old:
                    heading2best_heading[heading_l] = heading
                heading2synonyms[heading_l].update(synonyms)
            else:
                heading2best_heading[heading_l] = heading
                heading2synonyms[heading_l] = set(synonyms)

            for term in [heading] + synonyms:
                term = term.strip().lower()
                if term in term2targets:
                    term2targets[term].add(heading_l)
                else:
                    term2targets[term] = {heading_l}

        ignored_terms = set()
        for term, targets in term2targets.items():
            if len(targets) > 2:
                ignored_terms.add(term)

        for heading_l, synonyms in heading2synonyms.items():
            heading = heading2best_heading[heading_l]
            filtered_synonyms = [s for s in synonyms if s.lower().strip() not in ignored_terms]
            vocabulary.add_vocab_entry(heading, self.entity_type_in_vocab, heading, ";".join(filtered_synonyms))

        logging.info("Parsed {} targets with {} terms. Saving vocabulary..."
                     .format(vocabulary.count_distinct_entities(),
                             vocabulary.count_distinct_terms()))

        vocabulary.export_vocabulary_as_tsv(self.vocab_dir)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    TargetVocabulary().initialize_vocabulary(force_create=True)

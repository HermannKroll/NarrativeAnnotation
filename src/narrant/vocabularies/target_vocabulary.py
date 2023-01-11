import json
import logging
import os

from kgextractiontoolbox.entitylinking.tagging.vocabulary import Vocabulary
from narrant.config import TARGET_TAGGER_VOCAB_DIRECTORY, TARGET_TAGGER_VOCAB
from narrant.preprocessing.enttypes import TARGET
from narrant.vocabularies.chembl_vocabulary import ChemblVocabulary
from narrant.vocabularies.generic_vocabulary import GenericVocabulary

URL = "https://www.ebi.ac.uk"
URL_PATH = "/chembl/api/data/target?format=json&limit={}"


class TargetVocabulary(ChemblVocabulary):

    IGNORED_TARGET_TYPES = {'organism', 'tissue', 'unchecked', 'no target'}

    def __init__(self):
        super().__init__(TARGET_TAGGER_VOCAB, TARGET)

    @staticmethod
    def create_target_vocabulary(expand_by_s_and_e=True):
        if not os.path.isfile(TARGET_TAGGER_VOCAB):
            TargetVocabulary().initialize_vocabulary()

        return GenericVocabulary.create_vocabulary_from_directory(TARGET_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)

    def _create_vocabulary_from_dir(self, tmp_dir):
        vocabulary = Vocabulary('')
        synonyms = list()

        logging.info("Start creating target vocabulary.")

        for file_name in os.listdir(tmp_dir):
            file_name = os.path.join(tmp_dir, file_name)
            if not os.path.isfile(file_name):
                continue

            with open(file_name) as file:
                for t in json.load(file):
                    if not (t['target_chembl_id'] or t['component_description']):
                        continue
                    # ignore certain target types
                    if t["target_type"].strip().lower() in TargetVocabulary.IGNORED_TARGET_TYPES:
                        continue

                    entity_id = t['target_chembl_id']
                    heading = t['pref_name']

                    if t['target_components']:
                        for tc in t['target_components']:
                            if tc['component_description']:
                                synonyms.append(tc['component_description'])
                            if tc['target_component_synonyms']:
                                synonyms.extend([syn['component_synonym'] for syn in tc['target_component_synonyms']])

                    if len(synonyms) > 0:
                        syn_str = ";".join(synonyms)
                        synonyms.clear()
                    else:
                        syn_str = ""

                    vocabulary.add_vocab_entry(entity_id, self.vocab_type, heading, syn_str)

        logging.info("Parsed {} targets with {} terms. Saving vocabulary..."
                     .format(vocabulary.count_distinct_entities(),
                             vocabulary.count_distinct_terms()))

        vocabulary.export_vocabulary_as_tsv(self.vocab_dir)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    TargetVocabulary().initialize_vocabulary(force_create=True)

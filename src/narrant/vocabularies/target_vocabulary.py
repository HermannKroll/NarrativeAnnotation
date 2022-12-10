import csv
import datetime
import json
import logging
import os
import shutil
import tempfile
from datetime import datetime

import requests

from kgextractiontoolbox.entitylinking.tagging.vocabulary import Vocabulary
from kgextractiontoolbox.progress import Progress
from narrant.config import TARGET_TAGGER_VOCAB_DIRECTORY, CHEMBL_TARGET_CSV, TARGET_TAGGER_VOCAB
from narrant.preprocessing.enttypes import TARGET
from narrant.vocabularies.generic_vocabulary import GenericVocabulary

URL = "https://www.ebi.ac.uk"
URL_PATH = "/chembl/api/data/target?format=json&limit={}"


class TargetVocabulary:
    @staticmethod
    def create_target_vocabulary(expand_by_s_and_e=True):
        if not os.path.isfile(TARGET_TAGGER_VOCAB) or not os.path.isfile(CHEMBL_TARGET_CSV):
            TargetVocabulary.initialize_target_vocabulary()

        return GenericVocabulary.create_vocabulary_from_directory(TARGET_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)

    @staticmethod
    def _create_vocabulary_from_dir(tmp_dir):
        start_time = datetime.now()
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

                    vocabulary.add_vocab_entry(entity_id, TARGET, heading, syn_str)

        logging.info("Parsed {} targets with {} terms in {}s. Saving vocabulary..."
                     .format(vocabulary.count_distinct_entities(),
                             vocabulary.count_distinct_terms(), datetime.now() - start_time))

        vocabulary.export_vocabulary_as_tsv(TARGET_TAGGER_VOCAB)

    @staticmethod
    def _create_chembl_entities_from_dir(tmp_dir):
        start_time = datetime.now()
        chembl_vocab = list()
        synonyms = list()

        logging.info("Start creating CHEMBL entities.")

        for file_name in os.listdir(tmp_dir):
            file_name = os.path.join(tmp_dir, file_name)
            if not os.path.isfile(file_name):
                continue

            with open(file_name) as file:
                for t in json.load(file):
                    if not (t['target_chembl_id'] or t['component_description']):
                        continue
                    entity_id = t['target_chembl_id']
                    heading = t['pref_name']

                    if t['target_components']:
                        for tc in t['target_components']:
                            if tc['component_description']:
                                synonyms.append(tc['component_description'])

                    if len(synonyms) > 0:
                        syn_str = ";".join(synonyms)
                        synonyms.clear()
                    else:
                        syn_str = ""

                    chembl_vocab.append({"chembl_id": entity_id, "pref_name": heading, "synonyms": syn_str})

        with open(CHEMBL_TARGET_CSV, "w") as file:
            wr = csv.DictWriter(file, fieldnames=["chembl_id", "pref_name", "synonyms"])
            wr.writeheader()
            wr.writerows(chembl_vocab)

    @staticmethod
    def _request_target_jsons(tmp_dir, limit=1000):
        # initial request to check connection and to receive metadata information
        response = requests.get("{}/chembl/api/data/target?limit=1&format=json".format(URL, URL_PATH.format(1)))
        if not response.ok:
            return

        page_meta = response.json()['page_meta']
        total_targets = page_meta['total_count']
        num_files = total_targets // limit + 1
        actual_targets = 0

        next_req = URL_PATH.format(limit)

        logging.info("Retrieving {} in {} api requests.".format(total_targets, num_files))

        p = Progress(total=num_files)
        p.start_time()
        p.print_progress(0)
        for i in range(1, num_files + 1):
            response = requests.get("{}{}".format(URL, next_req))
            if not response.ok:
                break

            result = response.json()
            next_req = result['page_meta']['next']

            targets = result['targets']
            actual_targets += len(targets)

            with open(os.path.join(tmp_dir, "targets_{:02}.json".format(i)), "w") as file:
                file.write(json.dumps(targets))
                file.close()

            response.close()
            p.print_progress(i)

        p.done()
        logging.info("Retrieved {} from {} total targets.".format(actual_targets, total_targets))
        return actual_targets

    @classmethod
    def initialize_target_vocabulary(cls, force_vocab=False, force_chembl=False):
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d:%H:%M:%S',
                            level=logging.INFO)

        logging.info("Initializing TARGET vocabulary and(/or) CHEMBL entities.")

        vocab_exist = os.path.isfile(TARGET_TAGGER_VOCAB)
        chembl_exist = os.path.isfile(CHEMBL_TARGET_CSV)

        if (vocab_exist and not force_vocab) or (chembl_exist and not force_chembl):
            logging.info("Vocabulary already exists. [use 'force_vocab=True' to force execution]")
            logging.info("CHEMBL entities already exist. [use 'force_chembl=True' to force execution]")
            logging.info("Stopping...")
            return

        if chembl_exist and force_chembl:
            logging.info("Remove old CHEMBL entities vocabulary.")
            os.remove(CHEMBL_TARGET_CSV)
        if vocab_exist and force_vocab:
            logging.info("Remove old TARGET vocabulary.")
            os.remove(TARGET_TAGGER_VOCAB)

        root_dir = tempfile.mkdtemp()
        logging.info("Using tmp dir {}.".format(root_dir))
        num_targets = cls._request_target_jsons(root_dir)

        if num_targets == 0:
            logging.error("No target data available. Removing tmp dir.")
            shutil.rmtree(root_dir)
            logging.info("Stopping...")
            return

        if force_vocab or not vocab_exist:
            cls._create_vocabulary_from_dir(root_dir)

        if force_chembl or not chembl_exist:
            cls._create_chembl_entities_from_dir(root_dir)

        logging.info(f'Remove temp directory: {root_dir}')
        shutil.rmtree(root_dir)


if __name__ == "__main__":
    TargetVocabulary.initialize_target_vocabulary(force_vocab=True, force_chembl=True)

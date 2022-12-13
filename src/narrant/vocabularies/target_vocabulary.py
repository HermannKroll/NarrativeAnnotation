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
from narrant.config import TARGET_TAGGER_VOCAB_DIRECTORY, TARGET_TAGGER_VOCAB
from narrant.preprocessing.enttypes import TARGET
from narrant.vocabularies.generic_vocabulary import GenericVocabulary

URL = "https://www.ebi.ac.uk"
URL_PATH = "/chembl/api/data/target?format=json&limit={}"


class TargetVocabulary:
    @staticmethod
    def create_target_vocabulary(expand_by_s_and_e=True):
        if not os.path.isfile(TARGET_TAGGER_VOCAB):
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
    def _request_target_jsons(tmp_dir, limit=1000):
        total_targets = 0
        actual_targets = 0
        iteration = 0
        num_files = 0
        p = None
        next_req = "/chembl/api/data/target?limit={}&format=json".format(limit)

        logging.info('Start requesting data {}{}'.format(URL, next_req))

        while True:
            response = requests.get("{}{}".format(URL, next_req))
            if not response.ok:
                logging.error('An error occurred in the {} api request.'.format(iteration))
                break

            result = response.json()
            if not p:
                total_targets = result['page_meta']['total_count']
                num_files = total_targets // limit + 1
                p = Progress(total=num_files, text='total API requests')
                p.start_time()

            targets = result['targets']
            actual_targets += len(targets)

            iteration += 1

            with open(os.path.join(tmp_dir, "targets_{:02}.json".format(iteration)), "w") as file:
                file.write(json.dumps(targets))
                file.close()

            response.close()
            p.print_progress(iteration)

            if result['page_meta']['next']:
                next_req = result['page_meta']['next']
            else:
                break

        p.done()
        logging.info("Retrieved {} from {} total targets in {}/{} requests."
                     .format(actual_targets, total_targets, iteration, num_files))
        return actual_targets

    @classmethod
    def initialize_target_vocabulary(cls, force_create=False):
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d:%H:%M:%S',
                            level=logging.INFO)

        logging.info("Initializing TARGET vocabulary.")
        vocab_exist = os.path.isfile(TARGET_TAGGER_VOCAB)

        if vocab_exist and not force_create:
            logging.error("Vocabulary already exists. [use 'force_vocab=True' to force execution]. Stopping...")
            return

        if vocab_exist:
            logging.info("Remove old TARGET vocabulary.")
            os.remove(TARGET_TAGGER_VOCAB)

        root_dir = tempfile.mkdtemp()
        logging.info("Using tmp dir {}.".format(root_dir))
        num_targets = cls._request_target_jsons(root_dir)

        if num_targets == 0:
            logging.error("No target data available. Removing tmp dir. Stopping...")
            shutil.rmtree(root_dir)
            return

        cls._create_vocabulary_from_dir(root_dir)

        logging.info(f'Remove temp directory: {root_dir}')
        shutil.rmtree(root_dir)


if __name__ == "__main__":
    TargetVocabulary.initialize_target_vocabulary(force_create=True)

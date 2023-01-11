import json
import logging
import os
import shutil
import tempfile
from abc import abstractmethod, ABC

import requests

from kgextractiontoolbox.progress import Progress

URL = "https://www.ebi.ac.uk"
URL_PATH = "/chembl/api/data/{}?{}"
REQ_LIMIT = 1000
DEFAULT_PARAMS = dict(format='json', limit=REQ_LIMIT)


class ChemblVocabulary(ABC):
    """
    Helper class for vocabulary retrieved from ChEMBL. For that methods exists to load the
    data using the API and to store it in an appropriate file corresponding to the type
    of the vocabulary.
    """

    def __init__(self, vocab_dir, vocab_type):
        """
        Initialize the member attributes such that they match with the ChEMBL api. Ensure
        that this abstract class does it in the correct way. Else override this function...
        """
        self.vocab_dir = vocab_dir
        self.vocab_type = vocab_type
        self.url_path_kw = vocab_type.lower()
        self.url_params = DEFAULT_PARAMS
        self.json_data_kw = "{}s".format(vocab_type.lower())

    @abstractmethod
    def _create_vocabulary_from_dir(self, tmp_dir):
        pass

    def initialize_vocabulary(self, force_create=False):
        logging.info("Initializing {} vocabulary.".format(self.vocab_type))
        vocab_exist = os.path.isfile(self.vocab_dir)

        if vocab_exist and not force_create:
            logging.error("Vocabulary already exists. [use 'force_vocab=True' to force execution]. Stopping...")
            return

        if vocab_exist:
            logging.info("Remove old {} vocabulary.")
            os.remove(self.vocab_dir)

        root_dir = tempfile.mkdtemp()
        logging.info("Using tmp dir {}.".format(root_dir))
        num_targets = self._request_chembl_jsons(root_dir)

        if num_targets == 0:
            logging.error("No {} data available. Removing tmp dir. Stopping...".format(self.vocab_type))
            shutil.rmtree(root_dir)
            return

        self._create_vocabulary_from_dir(root_dir)

        logging.info(f'Remove temp directory: {root_dir}')
        shutil.rmtree(root_dir)

    def _request_chembl_jsons(self, tmp_dir):
        total_requests = 0
        actual_targets = 0
        iteration = 0
        num_files = 0
        p = None
        next_req = URL_PATH.format(self.url_path_kw, "&".join([f"{k}={v}" for k, v in self.url_params.items()]))

        logging.info('Start requesting data {}{}'.format(URL, next_req))

        while True:
            response = requests.get("{}{}".format(URL, next_req))
            if not response.ok:
                logging.error('An error occurred in the {} api request.'.format(iteration))
                break

            result = response.json()
            if not p:
                total_requests = result['page_meta']['total_count']
                num_files = total_requests // REQ_LIMIT + 1
                p = Progress(total=num_files, text='total API requests')
                p.start_time()

            api_data = result[self.json_data_kw]
            actual_targets += len(api_data)

            iteration += 1

            with open(os.path.join(tmp_dir, "{}_{:02}.json".format(self.json_data_kw, iteration)), "w") as file:
                file.write(json.dumps(api_data))
                file.close()

            response.close()
            p.print_progress(iteration)

            if result['page_meta']['next']:
                next_req = result['page_meta']['next']
            else:
                break

        p.done()
        logging.info("Retrieved {} from {} total targets in {}/{} requests."
                     .format(actual_targets, total_requests, iteration, num_files))
        return actual_targets

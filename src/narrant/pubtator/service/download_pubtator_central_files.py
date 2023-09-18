import argparse
import logging
from time import sleep
from typing import Set

import requests

from kgextractiontoolbox.progress import Progress
from kgextractiontoolbox.document.document import TaggedDocument
from narrant.util.helpers import chunks

DOWNLOAD_BATCH_SIZE = 950
PUBTATOR_DOWNLOAD_URL = 'https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/pubtator'


def download_pubtator_files_from_pubtator_central(pmids: Set[int], output_file: str):
    logging.info(f'{len(pmids)} documents must be downloaded from PubTator Central...')

    pmid_list = sorted(list(pmids))
    progress = Progress(total=len(pmid_list), print_every=1, text="Downloading PubTator Central Annotations...")
    progress_value = 0
    progress.start_time()
    first = True
    with open(output_file, 'wt') as f_out:
        for pmid_chunk in chunks(pmid_list, DOWNLOAD_BATCH_SIZE):
            progress.print_progress(progress_value)
            # Compute the params
            params = {"pmids": [str(pmid) for pmid in pmid_chunk]}
            # hand-craft url because otherwise , will be escaped
            # unfourtenatly PubTator needs commas as a delimiter
            #  url = f'{PUBTATOR_DOWNLOAD_URL}?pmids={pmid_str}'

            # do the post request
            result = requests.post(PUBTATOR_DOWNLOAD_URL, json=params)

            if result.status_code == 200:
                raw_text = result.content.decode('utf-8')
                for doc_content in raw_text.split('\n\n'):
                    if not doc_content.strip():
                        continue
                    try:
                        doc = TaggedDocument(from_str=f'{doc_content}\n')
                        doc.sort_tags()
                        doc.check_and_repair_tag_integrity()
                        if doc.id and doc.has_content():
                            if first:
                                f_out.write(str(doc))
                                first = False
                            else:
                                f_out.write(f'\n{str(doc)}')
                    except:
                        logging.warning(f'Skipping document: {doc_content}')
                        pass
            else:
                logging.info(f'Received status code {result.status_code} from PubTator Central ({result.text})')
                break

            # Sleep a bit to prevent being blocked
            sleep(2.0)
            progress_value += len(pmid_chunk)

    progress.done()
    logging.info('Finished')


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("idfile", help="The id file (plain file with document ids in each line)")
    parser.add_argument("output", help="Output file for PubTator Documents and Annotations")
    args = parser.parse_args(args)

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    logging.info(f'Reading PMIDs from file: {args.idfile}')
    with open(args.idfile, 'rt') as f:
        pmids = set([line.strip() for line in f])
    logging.info(f'{len(pmids)} PMIDs found in file...')
    download_pubtator_files_from_pubtator_central(pmids, args.output)


if __name__ == "__main__":
    main()

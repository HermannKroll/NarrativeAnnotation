import argparse
import calendar
import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from typing import Dict, List, Tuple

import requests

from kgextractiontoolbox.document.narrative_document import NarrativeDocument, NarrativeDocumentMetadata


def get_md5_hash_str(str_input):
    m = hashlib.md5()
    m.update(str_input.encode())
    return m.hexdigest()


def build_url(cursor: str, collection_filter: str, start_date: str, base_url: str):
    """
    Build request wih a given cursor.
    """
    url = base_url.format(cursor, collection_filter, f'{start_date}T00:00:00Z')
    return url


def crawl_k10_index(work_dir: str, collection_filter: str, start_date: str, collection: str, base_url: str,
                    max_retries: int, output_file: str):
    """
    Dumping loop
    """
    current_cursor = "*"
    start_url = build_url(current_cursor, collection_filter, start_date, base_url)
    logging.info(f"Starting with URL {start_url}")
    counter = 0
    retry_counter = 0
    current_url = start_url
    logging.info("start url  " + start_url)
    loop = True
    produced_doc_files = []

    # check whether working directory exists
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir, exist_ok=True)

    md5hash2id = defaultdict(list)
    md5hash2most_information_docid = {}
    logging.info("Starting crawling loop...")
    # handle key error here
    while loop:
        if retry_counter > max_retries:
            logging.error(f'Maximum retries exceeded: tried {retry_counter} times')
            break

        try:
            # make a pause to not overload the server
            time.sleep(10)
            logging.info('Performing request:' + current_url)
            response = requests.get(current_url)
            if response.status_code == 200:
                retry_counter = 0

                # first decode the json document data
                content = json.loads(response.content.decode("utf-8"))

                docfile = write_file(work_dir, content, counter, collection, md5hash2id, md5hash2most_information_docid)
                # some requests may not carry any data
                if docfile:
                    produced_doc_files.append(docfile)

                next_cursor = get_next_cursor(content)
                logging.info(f"Next cursor: {next_cursor}")
                if next_cursor != '' and current_cursor != next_cursor:
                    current_cursor = next_cursor
                    current_url = build_url(current_cursor, collection_filter, start_date, base_url)
                    counter = counter + 1
                else:
                    loop = False
            else:
                logging.debug(f'Received status code: {response.status_code} - retrying...')
                retry_counter += 1
                # retry
        except KeyError:
            logging.debug(f'Key error in request - retrying...')

        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            logging.debug(f'Connection refused - retrying...')

            # if connection problem with K10 exist
            retry_counter += 1

    logging.info("Crawling finished")

    timestamp = calendar.timegm(time.gmtime())
    file_path_collisions = os.path.join(f"{work_dir}", collection, f"{timestamp}.collisions.json")
    logging.info('Writing final collision data ' + file_path_collisions)
    with open(file_path_collisions, "w") as f:
        # only store collisions
        md5hash2id = {k: v for k, v in md5hash2id.items() if len(v) > 1}
        json.dump(md5hash2id, f)

    # create a set of document ids that we want to export
    most_information_document_ids = {str(docid) for docid, _ in md5hash2most_information_docid.values()}
    logging.info(f'Writing final document data to {output_file}')
    first_line = True
    with open(output_file, "w") as f_out:
        for docfile in produced_doc_files:
            with open(docfile, "r") as f_in:
                for line in f_in:
                    # check whether this document was the most informed one
                    doc_entry = json.loads(line)
                    if str(doc_entry["id"]) in most_information_document_ids:
                        if first_line:
                            f_out.write(line)
                            first_line = False
                        else:
                            f_out.write('\n' + line)

    logging.info('Data written. Finished.')


def get_next_cursor(content):
    """
    Extract next cursor from json response
    """
    nextCursor = content['nextCursorMark']
    logging.info("Next cursor to fetch " + nextCursor)
    return nextCursor


def write_file(work_dir: str, content: Dict, index: int, collection: str, md5hash2id: Dict[str, List],
               md5hash2most_information_docid: Dict[str, Tuple[str, int]]):
    """
    Write current batch to file
    """
    # first write json data to raw file
    timestamp = calendar.timegm(time.gmtime())
    document_file_directory = os.path.join(f"{work_dir}", collection)
    os.makedirs(document_file_directory, exist_ok=True)

    file_path_raw = os.path.join(f"{work_dir}", collection, f"{timestamp}.{index}.raw.json")
    with open(file_path_raw, "w") as f:
        json.dump(content, f)

    if "response" not in content:
        logging.debug('No response data in response - - skipping processing of request')
        return

    # we only need the response data
    content = content["response"]
    if "numFound" not in content or int(content["numFound"]) == 0:
        logging.debug('No documents in response - skipping processing of request')
        return

    if "docs" not in content:
        logging.debug('No document data in response - skipping processing of request')
        return

    document_json_strings = list()
    for document_data in content["docs"]:
        abstract = ""
        publication_year = 0
        publication_month = 0
        authors = ""
        journals = ""

        if "title" not in document_data or "id" not in document_data:
            logging.debug(f'Skipping entry {document_data} because id and title are not filled.')
            continue

        title = document_data["title"][0].strip()
        doc_id = document_data["id"].strip()
        pubpharm_doi = "https://www.pubpharm.de/vufind/Record/" + doc_id

        if "abstract" in document_data:
            abstract = document_data["abstract"][0].strip()
        if "author_browse" in document_data:
            authors = ' | '.join([a.strip() for a in document_data["author_browse"]])
        if "container_title" in document_data:
            journals = document_data["container_title"].strip()
        if "publishDateDaySort_date" in document_data:
            try:
                # should be yyyy-mm-dd (but maybe mm and dd is missing)
                publication_time_info = document_data["publishDateDaySort_date"].strip().split('-')
                if len(publication_time_info) >= 1:
                    # we assume year only
                    publication_year = int(publication_time_info[0])
                if len(publication_time_info) >= 2:
                    # we assume yyyy-mm
                    publication_month = int(publication_time_info[1])
                # days are ignored
            except ValueError:
                logging.debug(f'{document_data["publishDateDaySort_date"]} is not an integer')
        else:
            logging.debug(f'Skipping entry {doc_id} - no publishDate info given')
            continue

        if publication_year < 1000 or publication_year > 9999:
            logging.debug(f'Skipping entry {doc_id} - publication year ({publication_year}) not in range [1000, 9999] '
                          f'(info: {document_data["publishDateDaySort_date"]})')
            continue
        # 0 is the default month if missing
        if publication_month < 0 or publication_month > 12:
            logging.debug(f'Skipping entry {doc_id} - publication month ({publication_month}) not in range [0, 12] '
                          f'(info: {document_data["publishDateDaySort_date"]})')
            continue

        metadata = NarrativeDocumentMetadata(publication_year, publication_month, authors, journals, pubpharm_doi)

        # match key for purposes
        # md5sum title + abstract + author
        matching_key = f'{title}___{abstract}___{authors}'
        md5hash = get_md5_hash_str(matching_key)

        # collisions speichern / statistics
        # md5hash + [doc1 , doc2, doc3] / min. 2 docs
        md5hash2id[md5hash].append(doc_id)

        # we use the md5hash to remove duplicates
        document = NarrativeDocument(doc_id, title, abstract, metadata)
        document_dict = document.to_dict(export_content=True, export_tags=False, export_sections=False,
                                         export_classification=False)
        document_json_string = json.dumps(document_dict)
        document_json_strings.append(document_json_string)

        # in the end, we want to export the document with the most information per md5hash
        # information are mostly based on journals and publication data information
        if md5hash not in md5hash2most_information_docid:
            md5hash2most_information_docid[md5hash] = (doc_id, len(document_json_string))
        else:
            if len(document_json_string) > md5hash2most_information_docid[md5hash][1]:
                md5hash2most_information_docid[md5hash] = (doc_id, len(document_json_string))

    document_file_directory = os.path.join(f"{work_dir}", collection, f"{timestamp}.{index}.jsonl")
    logging.info("Write File " + document_file_directory)
    with open(document_file_directory, "w") as f:
        out_string = "\n".join(document_json_strings)
        f.write(out_string)

    return document_file_directory


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    argparse = argparse.ArgumentParser()
    argparse.add_argument("output", type=str, help="File path where there crawled document data should be stored.")
    argparse.add_argument("--workdir", type=str, required=True,
                          help="Working directory where crawled document data should be stored.")
    argparse.add_argument("-cf", "--collection-filter", required=True, type=str, help="Collection name to crawl.")
    argparse.add_argument("-c", "--collection", required=True, type=str, help="Collection name for our pipeline")
    argparse.add_argument("-d", "--date", type=str, required=True,
                          help="Data since when updated should be retrieved. (YYYY-MM-DD)")
    argparse.add_argument("-b", "--base-url", type=str, required=True, help="Data source base URL.")
    argparse.add_argument("--max-retries", type=int, default=10,
                          help="How many retries should be made if request fails")
    args = argparse.parse_args()

    crawl_k10_index(args.workdir, args.collection_filter, args.date, args.collection, args.base_url, args.max_retries,
                    args.output)

import argparse
import calendar
import json
import logging
import os
import time
from datetime import date

import requests

from kgextractiontoolbox.document.narrative_document import NarrativeDocument, NarrativeDocumentMetadata

# Static part of directory
BASE_DIR = "./k10Plus_Dump"


def build_dir():
    """
    Setup working directory.
    """
    today = str(date.today())
    download_dir = BASE_DIR + today
    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)
    logging.info("Write dumps to " + download_dir)
    return download_dir


def build_url(cursor: str, collection: str, start_date: str, base_url: str, url_filter: str):
    """
    Build request wih a given cursor.
    """
    url = base_url.format(collection, start_date, cursor) + url_filter
    return url


def load_dumps(work_dir: str, collection: str, start_date: str, output_collection: str, base_url: str, url_filter: str):
    """
    Dumping loop
    """
    current_cursor = "*"
    start_url = build_url(current_cursor, collection, start_date, base_url, url_filter)
    counter = 0
    current_url = start_url
    logging.info("start url  " + start_url)
    loop = True
    while loop:
        response = requests.get(current_url)
        write_file(work_dir, response.content, counter, output_collection)

        next_cursor = get_next_cursor(response.content)
        if next_cursor != '' and current_cursor != next_cursor:
            current_cursor = next_cursor
            current_url = build_url(current_cursor, collection, start_date, base_url, url_filter)
            counter = counter + 1
        else:
            loop = False
    logging.info("Done")


def get_next_cursor(content):
    """
    Extract next cursor from json response
    """
    json_string = content
    obj = json.loads(json_string)
    nextCursor = obj['nextCursorMark']
    logging.info("Next cursor to fetch " + nextCursor)
    return nextCursor


def write_file(work_dir: str, content: bytes, index: int, output_collection: str):
    """
    Write current batch to file
    TODO: USE output_collection
    """

    # TODO decode correct format json/xml?
    content = content.decode("utf-8")

    # TODO create NarrativeDocument for each document element
    document_json_strings = list()
    for document_data in content:
        publication_year = 0
        publication_month = 0
        authors = "None"
        journals = "None"
        doi = "None"

        metadata = NarrativeDocumentMetadata(publication_year, publication_month, authors, journals, doi)

        doc_id = None
        title = ""
        abstract = ""

        document = NarrativeDocument(doc_id, title, abstract, metadata)
        document_dict = document.to_dict(export_content=True, export_tags=False, export_sections=False,
                                         export_classification=False)
        document_json_strings.append(json.dumps(document_dict))

    timestamp = calendar.timegm(time.gmtime())
    file_path = os.path.join(f"{work_dir}", output_collection, f"{timestamp}.jsonl")
    logging.info("Write File " + file_path)
    with open(file_path, "w") as f:
        out_string = "\n".join(document_json_strings)
        f.write(out_string)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    argparse = argparse.ArgumentParser()
    argparse.add_argument("-c", "--collection", required=True, type=str, help="Collection name to crawl.")
    argparse.add_argument("-o", "--out-collection", required=True, type=str, help="Output collection name.")
    argparse.add_argument("-d", "--date", type=str, default="2014-12-01",
                          help="Data since when updated should be retrieved. (YYYY-MM-DD)")
    argparse.add_argument("-b", "--base-url", type=str, required=True, help="Data source base URL.")
    argparse.add_argument("-f", "--url-filter", type=str, required=True, help="Data source specific filter")
    args = argparse.parse_args()

    cwd = build_dir()
    load_dumps(cwd, args.collection, args.date, args.out_collection, args.base_url, args.url_filter)

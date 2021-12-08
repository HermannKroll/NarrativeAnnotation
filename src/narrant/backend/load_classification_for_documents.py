import argparse
import csv
import logging
from typing import Set

from narraint.backend.database import SessionExtended
from narrant.backend.models import Document, DocumentClassification


def load_document_class(document_ids: Set[int], document_collection: str, document_class: str):
    """
    Add the document classification for the set of document ids to the database
    Only insert classification for documents that are present in the database
    :param document_ids: a set of document ids
    :param document_collection: the corresponding document collection
    :param document_class: the document class
    :return: None
    """
    logging.info(f'Querying for document ids in collection: {document_collection}')
    session = SessionExtended.get()
    known_doc_ids = Document.get_document_ids_for_collection(session, document_collection)

    relevant_ids_in_db = document_ids.intersection(known_doc_ids)
    missing = document_ids - known_doc_ids
    logging.info(f'{len(relevant_ids_in_db)} found in database ({len(missing)} ids are missing)')

    logging.info(f'Computing insert of document classification (class={document_class})...')
    insert_values = []
    for doc_id in relevant_ids_in_db:
        insert_values.append(dict(document_id=doc_id,
                                  document_collection=document_collection,
                                  classification=document_class,
                                  explanation="External File"))

    logging.info('Beginning insert...')
    DocumentClassification.bulk_insert_values_into_table(session, insert_values)
    logging.info('Finished')


def load_document_ids_from_pubmed_result_tsv(pubmed_tsv_file: str):
    """
    Reads document ids from a PubMed export TSV file
    :param pubmed_tsv_file: path to the PubMed export file
    :return: None
    """
    logging.info(f'Read document ids from file: {pubmed_tsv_file}')
    document_ids = set()
    with open(pubmed_tsv_file, 'rt') as f:
        reader = csv.DictReader(filter(lambda r: r[0] != '#', f), delimiter='\t')
        for row in reader:
            document_ids.add(int(row["pmid"]))
    logging.info(f'{len(document_ids)} ids found')
    return document_ids


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="An PubMed exported TSV file")
    parser.add_argument("dclass", help="The document class which will be added to the database for all document ids")
    parser.add_argument("-c", "--collection", required=True, help="The corresponding document collection")
    args = parser.parse_args(args)

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    document_ids = load_document_ids_from_pubmed_result_tsv(args.input)
    load_document_class(document_ids, args.collection, args.dclass)


if __name__ == "__main__":
    main()

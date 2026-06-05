import argparse
import logging
import csv

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import DocumentMetadata

def export_document_ids_from_journal_list(journal_list_file: str, document_collection: str, output_file: str):
    """
    Exports all article ids that belong to one of the journals of the input journal list
    :param journal_list_file: file containing a list of relevant journals (one journal per line or CSV cell)
    :param document_collection: the corresponding document collection
    :param output_file: Relevant documents will be written to that file
    :return: None
    """
    logging.info(f"Reading journal list from: {journal_list_file}")
    journal_names = set()

    if journal_list_file.endswith('.csv'):
        with open(journal_list_file, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for column in row:
                    name = column.strip().lower()
                    if name:
                        journal_names.add(name)
    elif journal_list_file.endswith('.txt'):
        with open(journal_list_file, 'rt', encoding='utf-8') as f:
            for line in f:
                name = line.strip().lower()
                if name:
                    journal_names.add(name)
    else:
        raise ValueError("Only .csv and .txt files are supported")

    logging.info(f'Found {len(journal_names)} different journal names')

    logging.info(f'Querying document id journal mappings from DocumentMetadata table '
                 f'(document_collection = {document_collection}) ...')
    session = Session.get()
    journal_q = session.query(DocumentMetadata.document_id, DocumentMetadata.journals)
    journal_q = journal_q.filter(DocumentMetadata.document_collection == document_collection)
    journal_q = journal_q.distinct()

    relevant_document_ids = set()
    for entry in journal_q:
        # Journals are formatted in this way: Current pharmaceutical design, Vol. 21 No. 11 (2015)
        journal = entry[1].split(',')[0].strip().lower()
        if journal in journal_names:
            relevant_document_ids.add(entry[0])

    logging.info(f'Retrieved {len(relevant_document_ids)} relevant document ids...')
    with open(output_file, 'wt', encoding='utf-8') as f:
        f.write('\n'.join([str(did) for did in relevant_document_ids]))
    logging.info('Finished')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("journal_file", help="Path to journal list (.csv or .txt)")
    parser.add_argument("output", help="Path to output file")
    parser.add_argument("-c", "--collection", help="Relevant document collection", required=True)
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    export_document_ids_from_journal_list(journal_list_file=args.journal_file, document_collection=args.collection,
                                          output_file=args.output)

if __name__ == "__main__":
    main()
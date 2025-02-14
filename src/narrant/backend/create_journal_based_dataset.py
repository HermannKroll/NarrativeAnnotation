import logging
import random
import pandas as pd
import argparse
import os
from kgextractiontoolbox.backend.models import DocumentMetadata
from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.retrieve import iterate_over_all_documents_in_collection

COLLECTION = 'PubMed'


def export_document_ids_from_journal_list(journal_list_file: str, document_collection: str, random_seed: int, sample_size: int):
    logging.info(f"Reading journal list from: {journal_list_file}")
    journal_names = set()
    if journal_list_file.endswith('.xlsx'):
        df = pd.read_excel(journal_list_file, engine='openpyxl', header=None)
        for index, row in df.iterrows():
            for column in row:
                if pd.notnull(column):
                    name = str(column).strip().lower()
                    journal_names.add(name)
    else:
        with open(journal_list_file, 'rt') as f:
            for line in f:
                journal_names.add(line.strip().lower())

    logging.info(f'Querying document id journal mappings from DocumentMetadata table ')
    session = Session.get()
    journal_q = session.query(DocumentMetadata.document_id, DocumentMetadata.journals)
    journal_q = journal_q.filter(DocumentMetadata.document_collection == document_collection)
    journal_q = journal_q.distinct()

    relevant_document_ids = set()
    all_document_ids = set()
    for entry in journal_q:
        all_document_ids.add(entry[0])
        journal = entry[1].split(',')[0].strip().lower()
        if journal in journal_names:
            relevant_document_ids.add(entry[0])

    logging.info(f'Retrieved {len(relevant_document_ids)} relevant document ids...')

    not_relevant_document_ids = all_document_ids - relevant_document_ids

    random.seed(random_seed)

    relevant_document_ids_sample = random.sample(relevant_document_ids, min(len(relevant_document_ids), sample_size))
    not_relevant_document_ids_sample = random.sample(not_relevant_document_ids, min(len(not_relevant_document_ids), sample_size))

    logging.info('Finished sampling document ids...')

    return relevant_document_ids_sample, not_relevant_document_ids_sample


def build_dataset(relevant_document_ids, not_relevant_document_ids, document_collection, random_seed: int):
    logging.info('Retrieving texts from database....')
    session = Session.get()
    doc_ids = relevant_document_ids + not_relevant_document_ids
    x_data, y_data, pmids_data = [], [], []
    for doc in iterate_over_all_documents_in_collection(session=session, collection=document_collection, document_ids=doc_ids):
        text = doc.get_text_content(sections=False)
        x_data.append(text)
        pmids_data.append(doc.id)
        if doc.id in relevant_document_ids:
            y_data.append(1)
        else:
            y_data.append(0)

    logging.info('Finished retrieving texts...')

    data = list(zip(pmids_data, x_data, y_data))
    random.seed(random_seed)
    random.shuffle(data)

    train_size = int(0.7 * len(data))
    dev_size = int(0.15 * len(data))

    train_data = data[:train_size]
    dev_data = data[train_size:train_size + dev_size]
    test_data = data[train_size + dev_size:]

    logging.info('Finished splitting data...')

    return train_data, dev_data, test_data


def save_dataset_to_csv(data, filename):
    df = pd.DataFrame(data, columns=['pmid', 'text', 'label'])
    df.to_csv(filename, index=False)
    logging.info(f'Saved dataset to {filename}')


def main():
    parser = argparse.ArgumentParser(description='Export and process document IDs based on journal list.')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the journal list file (xlsx or txt).')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory to save datasets.')
    parser.add_argument('--split', action='store_true', help='Split the dataset into train, dev, and test sets if specified.')
    parser.add_argument('--sample_size', type=int, default=10000, help='Sample size for relevant and non-relevant documents.')
    parser.add_argument('--random_seed', type=int, default=42, help='Random seed for reproducibility.')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    os.makedirs(args.output_dir, exist_ok=True)

    relevant_document_ids, not_relevant_document_ids = export_document_ids_from_journal_list(
        args.input_file, COLLECTION, random_seed=args.random_seed, sample_size=args.sample_size)

    if args.split:
        train_data, dev_data, test_data = build_dataset(relevant_document_ids, not_relevant_document_ids, COLLECTION,
                                                        random_seed=args.random_seed)
        save_dataset_to_csv(train_data, os.path.join(args.output_dir, 'train_data.csv'))
        save_dataset_to_csv(dev_data, os.path.join(args.output_dir, 'dev_data.csv'))
        save_dataset_to_csv(test_data, os.path.join(args.output_dir, 'test_data.csv'))
    else:
        all_data = [(pmid, text, label) for pmid, text, label in zip(relevant_document_ids + not_relevant_document_ids, [None]*len(relevant_document_ids + not_relevant_document_ids), [1]*len(relevant_document_ids) + [0]*len(not_relevant_document_ids))]
        save_dataset_to_csv(all_data, os.path.join(args.output_dir, 'dataset.csv'))


if __name__ == "__main__":
    main()

import logging
import random
import argparse
import os
import csv
from kgextractiontoolbox.backend.models import DocumentMetadata
from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.retrieve import iterate_over_all_documents_in_collection

COLLECTION = 'PubMed'

def export_document_ids_from_journal_list(journal_list_file: str, document_collection: str, random_seed: int, sample_size: int):
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

    logging.info(f'Querying document id journal mappings from DocumentMetadata table')
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
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['pmid', 'text', 'label'])
        for row in data:
            writer.writerow(row)
    logging.info(f'Saved dataset to {filename}')

def main():
    parser = argparse.ArgumentParser(description='Export and process document IDs based on journal list.')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the journal list file (csv or txt).')
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
        all_data = [(pmid, None, label) for pmid, label in zip(relevant_document_ids + not_relevant_document_ids,
                                                               [1] * len(relevant_document_ids) + [0] * len(not_relevant_document_ids))]
        save_dataset_to_csv(all_data, os.path.join(args.output_dir, 'dataset.csv'))

if __name__ == "__main__":
    main()

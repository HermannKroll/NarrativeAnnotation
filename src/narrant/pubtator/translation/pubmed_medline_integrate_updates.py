import logging
from argparse import ArgumentParser

from kgextractiontoolbox.document.document import TaggedDocument
from narrant.pubtator.extract import read_pubtator_documents


def pubmed_medline_merge_with_updates(medline_file, medline_updates_file, output):
    medline_ids = set([TaggedDocument(content).id for content in read_pubtator_documents(medline_file)])
    logging.info(f'{len(medline_ids)} PMIDs in Medline')
    update_ids = set([TaggedDocument(content).id for content in read_pubtator_documents(medline_updates_file)])
    logging.info(f'{len(update_ids)} PMIDs in Update File')

    medline_ids_to_extract = medline_ids - update_ids
    logging.info(f'{len(medline_ids_to_extract) - len(medline_ids)} medline articles were updated')

    logging.info('Begin merge...')
    with open(output, 'wt') as f_out:
        logging.info('Write not updated medline files...')
        for document_content in read_pubtator_documents(medline_file):
            doc = TaggedDocument(document_content)
            if doc.id in medline_ids_to_extract:
                f_out.write(document_content + "\n")
        logging.info('Write updated medline files...')
        for document_content in read_pubtator_documents(medline_updates_file):
            f_out.write(document_content + "\n")
    logging.info('Finished')


def main():
    parser = ArgumentParser()
    parser.add_argument("medline", help="PubMed Medline PubTator file", metavar="FILE")
    parser.add_argument("medline_updates", help="PubMed Medline Updates PubTator file", metavar="FILE")
    parser.add_argument("output", help="merged PubTator output file", metavar="FILE")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    # logging.info(f'Converting the PubMed Medline to PubTator ({args.input} -> {args.output})')
    pubmed_medline_merge_with_updates(args.medline, args.medline_updates, args.output)


if __name__ == "__main__":
    main()

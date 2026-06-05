import argparse
import logging

from kgextractiontoolbox.document.document import TaggedDocument


def validate_pubtator_file(input_file: str):
    from kgextractiontoolbox.document.extract import read_documents
    for idx, document_content in enumerate(read_documents(input_file)):
        if not document_content:
            continue
        doc = TaggedDocument(document_content)

        if not doc:
            logging.warning(f'Document could not be parsed from: {document_content}')

        if not doc.title and not doc.abstract:
            logging.warning(f'Document title and abstract NOT found in: {document_content}')


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args(args)
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    validate_pubtator_file(args.input)


if __name__ == "__main__":
    main()

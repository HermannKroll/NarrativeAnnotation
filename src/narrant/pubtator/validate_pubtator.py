import argparse
import logging

from kgextractiontoolbox.document.document import TaggedDocument


def validate_pubtator_file(input_file:str):
    from narrant.pubtator.extract import read_pubtator_documents
    for idx, pubtator_content in enumerate(read_pubtator_documents(input_file)):
        if not pubtator_content:
            continue
        doc = TaggedDocument(pubtator_content)

        if not doc:
            logging.warning(f'Document could not be parsed from: {pubtator_content}')

        if not doc.title and not doc.abstract:
            logging.warning(f'Document title and abstract NOT found in: {pubtator_content}')



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

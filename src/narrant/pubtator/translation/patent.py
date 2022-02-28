import logging
import os.path
from argparse import ArgumentParser
from pathlib import Path
from typing import Union, Iterator

from kgextractiontoolbox.backend.models import Document
from kgextractiontoolbox.document.document import TaggedDocument
from kgextractiontoolbox.document.doctranslation import DocumentTranslationLoader, SourcedDocument, \
    run_document_translation


class PatentConverter(DocumentTranslationLoader):
    """
    Convert TIB patents dump to collection of JSON documents.

    .. note:

       Patents are identified using a country code and an ID, which are only unique in combination.
       Since we require ids to be integers, we generate artifical document ids
       IDs need to be digits, we replace the country code with a unique digit.
    """

    def read_sourced_documents(self, file: Union[Path, str]) -> Iterator[SourcedDocument]:
        """
        Read patents from input file
        :param file:
        :return:
        """
        logging.info(f"Reading file: {file}")
        with open(file) as f:
            for idx, line in enumerate(f):
                id_part, body = line.strip().split("|", maxsplit=1)
                did = id_part[id_part.rindex(":") + 1:]
                if idx % 2 == 0:
                    title = body
                else:
                    abstract = body

                    title = Document.sanitize(title)
                    abstract = Document.sanitize(abstract)
                    if title or abstract:
                        doc = TaggedDocument(id=did, title=title, abstract=abstract)
                        basename = os.path.basename(file)
                        yield SourcedDocument(id_part, basename, doc)

    def count_documents(self, file: Union[Path, str]):
        count = 0
        for line in open(file):
            count += 1
        return int(count / 2)


def main():
    parser = ArgumentParser(description="Tool to convert Patent file to Pubtator format")
    parser.add_argument("input", help="Input file", metavar="INPUT_FILE_OR_DIR")
    parser.add_argument("output", help="Output file", metavar="OUTPUT_FILE")
    parser.add_argument("-c", "--collection", required=True, help="document collection")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    run_document_translation(args.input, args.output, PatentConverter, collection=args.collection)


if __name__ == "__main__":
    main()

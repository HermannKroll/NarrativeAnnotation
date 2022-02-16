import json
import logging
import re
from argparse import ArgumentParser

from narrant.backend.models import Document
from narrant.progress import Progress
from narrant.pubtator.document import TaggedDocument


class PatentConverter:
    """
    Convert TIB patents dump to collection of PubTator documents.

    .. note:

       Patents are identified using a country code and an ID, which are only unique in combination. Since PubTator
       IDs need to be digits, we replace the country code with a unique digit.
    """
    REGEX_ID = re.compile(r"^\d+$")
    COUNTRY_PREFIX = dict(
        AU=11,
        CN=12,
        WO=13,
        GB=14,
        US=15,
        EP=16,
        CA=17,
        JP=18,
        KR=19,
        DE=20,
        ES=21,
        FR=22,
        RU=23,
        AT=24,
        CH=25
    )
    COUNTRIES = set(COUNTRY_PREFIX.keys())
    COUNTRY_PREFIX_REVERSE = {v: k for k, v in COUNTRY_PREFIX.items()}

    @staticmethod
    def decode_patent_country_code(patent_id):
        patent_str = str(patent_id)
        c_code, rest = int(patent_str[:2]), patent_str[2:]
        if c_code not in PatentConverter.COUNTRY_PREFIX_REVERSE:
            raise ValueError('Country Code {} is unknown'.format(c_code))
        return PatentConverter.COUNTRY_PREFIX_REVERSE[c_code] + rest

    def convert(self, in_file, out_file):
        """
        `in_file` is the file preprocessed by the Academic library of the TU Braunschweig.

        :param in_file: File for the TIB dump
        :param out_file: Output file for the PubTatator file
        :return:
        """
        logging.info("Reading file ...")
        title_by_id = dict()
        abstract_by_id = dict()
        count = 0
        with open(in_file) as f:
            for idx, line in enumerate(f):
                id_part, body = line.strip().split("|", maxsplit=1)
                did = id_part[id_part.rindex(":") + 1:]
                country_code = did[:2]
                patent_id = did[2:]
                if country_code in self.COUNTRIES and self.REGEX_ID.fullmatch(patent_id):
                    if not patent_id.isdigit():
                        logging.warning(f'{patent_id} is not an integer - skipping ({id_part})')
                    count += 1
                    did = "{}{}".format(self.COUNTRY_PREFIX[country_code], patent_id)
                    if idx % 2 == 0:
                        title_by_id[did] = body
                    else:
                        abstract_by_id[did] = body
                else:
                    logging.warning(f'Skipping unknown country code: {country_code} in ({id_part})')

        total = len(title_by_id.keys())
        logging.info(f'{total} patents to convert...')
        progress = Progress(total, print_every=100, text="Converting patents...")
        progress.start_time()
        first_doc = True
        with open(out_file, 'wt') as f_out:
            f_out.write("[\n")
            for idx, (did, title) in enumerate(title_by_id.items()):
                progress.print_progress(idx)
                if did in abstract_by_id:
                    abstract = abstract_by_id[did]
                    title = Document.sanitize(title)
                    abstract = Document.sanitize(abstract)
                    if title or abstract:
                        doc = TaggedDocument(id=did, title=title, abstract=abstract)
                        if not first_doc:
                            f_out.write(',\n')
                        else:
                            first_doc = False
                        json.dump(doc.to_dict(), f_out, indent=1)
                else:
                    logging.info("WARNING: Document {} has no title and no abstract".format(did))
            f_out.write("\n]\n")
        progress.done()


def main():
    parser = ArgumentParser(description="Tool to convert Patent file to Pubtator format")
    parser.add_argument("input", help="Input file", metavar="INPUT_FILE_OR_DIR")
    parser.add_argument("output", help="Output file", metavar="OUTPUT_FILE")
    args = parser.parse_args()

    t = PatentConverter()
    t.convert(args.input, args.output)


if __name__ == "__main__":
    main()

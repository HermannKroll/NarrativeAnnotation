import logging
import re
import sys
from argparse import ArgumentParser

from narrant.backend.models import Document
from narrant.progress import Progress


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
        JP=18
    )
    COUNTRIES = set(COUNTRY_PREFIX.keys())
    COUNTY_PREFIX_REVERS = {v: k for k, v in COUNTRY_PREFIX.items()}

    @staticmethod
    def decode_patent_country_code(patent_id):
        patent_str = str(patent_id)
        c_code, rest = int(patent_str[0]), patent_str[1:]
        if c_code == 0 or c_code > len(PatentConverter.COUNTY_PREFIX_REVERS):
            raise ValueError('Country Code {} is unknown'.format(c_code))
        return PatentConverter.COUNTY_PREFIX_REVERS[c_code - 1] + rest

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
                    count += 1
                    did = "{}{}".format(self.COUNTRY_PREFIX[country_code], patent_id)
                    if idx % 2 == 0:
                        title_by_id[did] = body.title()
                    else:
                        abstract_by_id[did] = body
                else:
                    raise ValueError(f'Unknown country code: {country_code}')

        total = len(title_by_id.keys())
        logging.info(f'{total} patents to convert...')
        progress = Progress(total, print_every=100, text="Converting patents...")
        progress.start_time()
        with open(out_file, 'wt') as f_out:
            for idx, (did, title) in enumerate(title_by_id.items()):
                progress.print_progress(idx)
                if did in abstract_by_id:
                    content = Document.create_pubtator(did, title, abstract_by_id[did])
                    f_out.write(content + '\n')
                else:
                    logging.info("WARNING: Document {} has no abstract".format(did))
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

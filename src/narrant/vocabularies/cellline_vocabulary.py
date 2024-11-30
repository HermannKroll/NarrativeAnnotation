import os.path
import xml.etree.ElementTree as ET

from kgextractiontoolbox.entitylinking.tagging.vocabulary import Vocabulary
from narrant.config import CELL_LINE_VOCAB, CELL_LINE_CELLOSAURUS, CELL_LINE_VOCAB_DIRECTORY
from narrant.entitylinking.enttypes import CELLLINE
from narrant.vocabularies.generic_vocabulary import GenericVocabulary


class CellLineVocabulary:
    @staticmethod
    def _create_cell_line_vocab_from_cellosaurus(expand_by_s_and_e=True):
        """
        Parse cell-line entries of the cellosaurus.xml file used for the CellLine
        vocabulary. A cell-line entry consists of a unique accession number, a
        recommended name (most frequently used) and corresponding synonyms. The
        accession number is as the unique vocabulary id.
        """
        if not os.path.exists(CELL_LINE_CELLOSAURUS):
            raise FileNotFoundError(f"File {CELL_LINE_CELLOSAURUS} does not exist!"
                                    f"Download from https://ftp.expasy.org/databases/cellosaurus/cellosaurus.xml")

        tree = ET.parse(CELL_LINE_CELLOSAURUS)
        vocab = Vocabulary("")

        for cell_line in tree.getroot().iterfind("./cell-line-list/cell-line"):
            entity_id = cell_line.find("accession-list/accession").text.strip().replace("_", ":")

            name_list = cell_line.find("name-list")
            heading = ""
            synonym = list()
            for name in name_list:
                name_str = name.text.strip()
                name_type = name.get("type", "")
                if name_type == "identifier":
                    assert heading == ""
                    heading = name_str
                elif name_type == "synonym":
                    synonym.append(name_str)

            synonyms = ";".join(synonym)
            vocab.add_vocab_entry(entity_id, CELLLINE, heading, synonyms, expand_terms=expand_by_s_and_e)
        return vocab

    @staticmethod
    def create_cell_line_vocabulary(expand_by_s_and_e=True):
        if not os.path.exists(CELL_LINE_VOCAB):
            # create vocabulary csv first
            vocab = CellLineVocabulary._create_cell_line_vocab_from_cellosaurus(expand_by_s_and_e=expand_by_s_and_e)
            vocab.export_vocabulary_as_tsv(CELL_LINE_VOCAB)
            return vocab
        return GenericVocabulary.create_vocabulary_from_directory(CELL_LINE_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)


if __name__ == '__main__':
    vocabulary = CellLineVocabulary.create_cell_line_vocabulary(expand_by_s_and_e=False)
    print(vocabulary)

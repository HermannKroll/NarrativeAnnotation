import logging
import os

from narrant.config import ORGANISM_TAGGER_VOCAB, ORGANISM_TAGGER_VOCAB_DIRECTORY
from narrant.entitylinking.enttypes import ORGANISM
from narrant.vocabularies.generic_vocabulary import GenericVocabulary
from narrant.vocabularies.target_vocabulary import TargetVocabulary


class OrganismVocabulary(TargetVocabulary):

    def __init__(self):
        super().__init__(ORGANISM_TAGGER_VOCAB, entity_type_in_vocab=ORGANISM)
        self.ignored_target_types = {}
        self.allowed_target_types = {'organism'}
        self.use_headings_as_key = False

    @staticmethod
    def create_organism_vocabulary(expand_by_s_and_e=True):
        if not os.path.isfile(ORGANISM_TAGGER_VOCAB):
            OrganismVocabulary().initialize_vocabulary()

        return GenericVocabulary.create_vocabulary_from_directory(ORGANISM_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    OrganismVocabulary().initialize_vocabulary(force_create=True)
